import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from analytics.push import push_analytics
from database.database import Session


async def parse_and_push_analytics():
    scheduler = AsyncIOScheduler()
    await push_analytics()
    scheduler.add_job(push_analytics,
                      "interval", minutes=1)
    scheduler.start()
    while True:
        await asyncio.sleep(60)
