from typing import Callable, Awaitable, Any, cast
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from cachetools import TTLCache
from dataclasses import dataclass, field
import structlog




@dataclass(kw_only=True, slots=True)
class ThrottlingData:
    rate: int = field(default=0)
    send_warning: bool = field(default=False)



class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, logger: structlog.typing.FilteringBoundLogger, throttling_time: int):
        self.logger = logger
        self.cache = TTLCache(maxsize=10_000, ttl=throttling_time)

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any]
    ):
        event = cast(Message, event)
        logger = self.logger.bind(TTLCache=self.cache)

        user = event.from_user

        if user.id not in self.cache:
            self.cache[user.id] = ThrottlingData()

        throttling_data = self.cache[user.id]

        if throttling_data.rate == 5:
            self.cache[user.id] = throttling_data

            if not throttling_data.send_warning:
                await event.answer('Вы заблокированы за спам. Повторите через некоторое время')

                throttling_data.send_warning = True

            return

        throttling_data.rate += 1


        logger.debug('Throttling Check')
        return await handler(event, data)

