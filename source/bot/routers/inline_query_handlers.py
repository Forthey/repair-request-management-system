from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent

router = Router()


@router.inline_query()
async def search(inline_query: InlineQuery):
    print(inline_query.query)
    test = InlineQueryResultArticle(
        id="1",
        title="test title",
        description=inline_query.query,
        input_message_content=InputTextMessageContent(
            message_text="Hihihihi"
        )
    )

    await inline_query.answer([test], is_personal=True)
