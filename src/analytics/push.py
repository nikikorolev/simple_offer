from loguru import logger
import subprocess

from analytics.parser import AnalyticsParser
from database.database import Session

FILE_PATH = "docs/analytics.json"
SLEEP_TIME = 60
GIT_BRANCH = "gh-pages"


def run_git_command(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd,
                            capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Ошибка комманды: {cmd}")
        logger.error(result.stderr)
        raise Exception(f"Ошибка git комманды: {cmd}")
    return result.stdout.strip()


async def push_analytics():
    logger.info("Обнаружены изменения, подготавливаем git...")

    try:
        run_git_command("git config user.email 'niki.korolev@gmail.com'")
        run_git_command("git config user.name 'Nikita Korolev'")
        run_git_command(
            "git remote set-url origin git@github.com:nikikorolev/simple_offer.git")

        run_git_command("git reset --hard")
        run_git_command("git clean -fd")

        run_git_command(f"git checkout {GIT_BRANCH}")
        run_git_command(f"git pull origin {GIT_BRANCH} --rebase")

        async with Session() as session:
            parser = AnalyticsParser(session)
            await parser.save_and_get_data_to_json()

        run_git_command(f"git add {FILE_PATH}")

        result = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if result.returncode == 0:
            logger.info("Изменений для коммита нет")
            return

        run_git_command('git commit -m "fix: auto-update analytics.json"')
        run_git_command(f"git push origin {GIT_BRANCH}")
        logger.success("Успешно обновлено и запушено.")

    except Exception as e:
        logger.exception(f"Ошибка при пуше аналитики: {e}")
