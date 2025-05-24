import asyncio
import tempfile
import shutil
import os

from loguru import logger

from analytics.parser import AnalyticsParser
from database.database import Session

FILE_PATH = "docs/analytics.json"
SLEEP_TIME = 60
GIT_BRANCH = "gh-pages"


async def run_git_command(cmd, cwd=None):
    logger.debug(f"Запуск команды: {cmd} в {cwd or os.getcwd()}")
    process = await asyncio.create_subprocess_shell(
        cmd,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    stdout_text = stdout.decode().strip()
    stderr_text = stderr.decode().strip()

    if process.returncode != 0:
        logger.error(f"Ошибка команды: {cmd}")
        logger.error(stderr_text)
        raise Exception(f"Ошибка git команды: {cmd}")

    logger.debug(f"Результат команды {cmd}: {stdout_text}")
    return stdout_text


async def clone_branch(branch: str):
    tmp_dir = tempfile.mkdtemp()
    try:
        await run_git_command(
            f"git clone -b {branch} git@github.com:nikikorolev/simple_offer.git {tmp_dir}"
        )
        return tmp_dir
    except Exception:
        shutil.rmtree(tmp_dir)
        raise


async def push_analytics():
    logger.info("Обнаружены изменения, подготавливаем git...")

    tmp_dir = await clone_branch(GIT_BRANCH)

    try:
        await run_git_command(
            "git config user.email 'niki.korolev@gmail.com'", cwd=tmp_dir
        )
        await run_git_command("git config user.name 'Nikita Korolev'", cwd=tmp_dir)

        async with Session() as session:
            parser = AnalyticsParser(session)
            await parser.save_and_get_data_to_json()

        shutil.copy(FILE_PATH, os.path.join(tmp_dir, FILE_PATH))

        await run_git_command("git add docs/analytics.json", cwd=tmp_dir)

        # Проверяем есть ли изменения для коммита
        diff_process = await asyncio.create_subprocess_exec(
            "git", "diff", "--cached", "--quiet", cwd=tmp_dir
        )
        await diff_process.communicate()

        if diff_process.returncode == 0:
            logger.info("Изменений для коммита нет")
            return

        await run_git_command(
            'git commit -m "fix: auto-update analytics.json"', cwd=tmp_dir
        )
        await run_git_command(f"git push origin {GIT_BRANCH}", cwd=tmp_dir)

        logger.success("Успешно обновлено и запушено.")
    finally:
        shutil.rmtree(tmp_dir)
