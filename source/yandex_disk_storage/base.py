import asyncio

import aiofiles
import httpx
import yadisk
import wldhx.yadisk_direct

from io import BytesIO

client = yadisk.AsyncClient(token="y0_AgAAAAAgwKOmAAvH2QAAAAEEzHBAAAC0OiK8OJ1Bi5f2RhQlNp4H5fASDg")


async def upload_file(filename: str, file: BytesIO | None) -> str | None:
    if not await client.check_token():
        print("Yandex auth error: probably need to refresh token")
        return None

    await client.upload(file, f"/bot/{filename}")
    meta = await client.get_meta(f"/bot/{filename}")
    return meta.file


async def test():
    print(await client.get_meta("/bot/Рандом2.jpg"))


async def get_preview(filename: str) -> str:
    print(filename)
    meta = await client.get_meta(f"/bot/{filename}")
    print(meta)
    return meta.preview

# asyncio.run(test())
