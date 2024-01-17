import aiohttp
import asyncio

from aiogram import md

from app.config import EDEN_API


class ChatGPT:
    def __init__(
            self,
            current_message: str = None,
            user_history: list[dict[str, str]] = None
    ):
        self.current_message = current_message
        self.user_history = user_history


    async def get_inline_response(self) -> str:
        url = "https://api.edenai.run/v2/text/chat"

        payload = {
            "temperature": 0,
            "max_tokens": 1000,
            "providers": "openai",
            "openai": "gpt-3.5-turbo",
            "text": self.current_message
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
                answer = response_data.get('openai', {}).get('generated_text')

            return answer
        except Exception as er:
            return f'Ошибка\n```\n{er}\n```'


    async def get_response(self) -> dict:
        url = "https://api.edenai.run/v2/text/chat"

        payload = {
            "temperature": 0,
            "max_tokens": 1000,
            "providers": "openai",
            "openai": "gpt-3.5-turbo",
            "text": self.current_message,
            "previous_history": self.user_history
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

            return response_data
        except:
            ...

    @staticmethod
    def reformat_response(text) -> str:
        if text:
            text = md.quote(text).replace(r'\`', '`')
            return text

        return f"{text} isn\'t string"
