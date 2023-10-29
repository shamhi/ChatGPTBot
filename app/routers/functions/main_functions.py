from aiogram import md
from app.config import EDEN_API
import aiohttp


async def get_response(
        current_message: str,
        previous_user_message: list[str],
        previous_assistant_message: list[str]
) -> str:
    try:
        url = "https://api.edenai.run/v2/text/chat"

        payload = {
            "temperature": 0,
            "max_tokens": 1000,
            "providers": "openai",
            "openai": "gpt-3.5-turbo",
            "text": current_message,
            "previous_history": [
                {
                    "role": "user",
                    "message": previous_user_message[2] or ''
                },
                {
                    "role": "assistant",
                    "message": previous_assistant_message[2] or ''
                },
                {
                    "role": "user",
                    "message": previous_user_message[1] or ''
                },
                {
                    "role": "assistant",
                    "message": previous_assistant_message[1] or ''
                },
                {
                    "role": "user",
                    "message": previous_user_message[0] or ''
                },
                {
                    "role": "assistant",
                    "message": previous_assistant_message[0] or ''
                }
            ]
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {EDEN_API}"
        }

        async with aiohttp.ClientSession() as session:
            response = await session.post(url, json=payload, headers=headers)
            response_data = await response.json()
            answer = str(response_data['openai']['generated_text'])

        return answer
    except Exception:
        return


def reformat_answer(text: str) -> str:
    text = md.quote(text).replace(r'\`', '`')
    return text
