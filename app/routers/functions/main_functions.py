from aiogram import Bot, md
from app.config import EDEN_API
import aiohttp
import asyncio


async def get_response(
        current_message: str,
        history: list[dict[str, str]],
        bot: Bot,
        chat_id: int,
        message_id: int
) -> str:
    url = "https://api.edenai.run/v2/text/chat"

    payload = {
        "temperature": 0,
        "max_tokens": 1000,
        "providers": "openai",
        "openai": "gpt-3.5-turbo",
        "text": current_message,
        "previous_history": history
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {EDEN_API}"
    }

    async with aiohttp.ClientSession() as session:
        response = await session.post(url, json=payload, headers=headers)
        if response.status == 429:
            retry_after = int(response.headers.get("Retry-After"))
            await asyncio.sleep(retry_after)
        response_data = await response.json()
        answer = response_data.get('openai', {}).get('generated_text')

    if answer is None:
        await delete_none_answer(bot=bot, chat_id=chat_id, message_id=message_id)
        return

    return answer


async def delete_none_answer(bot: Bot, chat_id: int, message_id: int) -> None:
    await bot.delete_message(chat_id=chat_id, message_id=message_id)


def reformat_answer(text: str) -> str:
    text = md.quote(text).replace(r'\`', '`')
    return text
