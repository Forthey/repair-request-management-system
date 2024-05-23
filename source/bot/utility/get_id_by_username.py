from telethon import TelegramClient
from telethon.errors import UsernameInvalidError
from telethon.tl.functions.users import GetFullUserRequest

from config import settings


async def get_user_id(username) -> int | None:
    async with TelegramClient(
            settings.get_bot_username,
            settings.get_tg_api_id,
            settings.get_tg_api_hash) as client:
        # bot = await client.start(bot_token=settings.TOKEN)
        bot = await client.start('0')

        async with bot:
            try:
                user = await bot(GetFullUserRequest(username))
            except UsernameInvalidError as e:
                return None
            except ValueError as e:
                return None

    return user.full_user.id
