import asyncio
from database.queries.workers import get_workers

tmp_access_rights = {"Админ": "Админ", "Работник": "Работник"}

workers_id: list[int] = []


async def fetch_workers():
    global workers_id
    workers_id = list(map(lambda worker: worker.telegram_id, await get_workers()))


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(fetch_workers())
