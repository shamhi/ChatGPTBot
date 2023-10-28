from aiogram.filters import Filter
from aiogram.types import Message
from app.config import IDS



ADMIN_IDS = IDS

class IsAdmin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in ADMIN_IDS
