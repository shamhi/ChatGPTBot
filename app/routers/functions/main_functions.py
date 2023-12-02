from aiogram import Bot, md
from app.config import EDEN_API
import aiohttp
import asyncio



async def inline_get_response(text: str):
    url = "https://api.edenai.run/v2/text/chat"

    payload = {
        "temperature": 0,
        "max_tokens": 1000,
        "providers": "openai",
        "openai": "gpt-3.5-turbo",
        "text": text
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

    return answer


async def get_response(
        current_message: str,
        history: list[dict[str, str]]
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
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.post(url, json=payload, headers=headers)
            if response.status == 429:
                retry_after = int(response.headers.get("Retry-After"))
                await asyncio.sleep(retry_after)
            response_data = await response.json()
            answer = response_data.get('openai').get('generated_text')


        return answer
    except Exception as er:
        return f'Ошибка\n```\n{er}\n```'


def reformat_answer(text: str) -> str:
    try:
        text = md.quote(text).replace(r'\`', '`')
        return text
    except Exception as er:
        return f'Ошибка\n```\n{er}\n```'
