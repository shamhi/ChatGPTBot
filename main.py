from aiogram import Dispatcher, Bot
from app.middlewares import InfoLoggerMiddleware, ThrottlingMiddleware
from app.routers import main_router
from app.filters import ChatTypeFilter, IsAdmin
from aiogram.types import BotCommand
from app import config
from app import utils
import structlog
import tenacity
import asyncpg



async def create_db_connections(dp: Dispatcher):
    logger: structlog.typing.FilteringBoundLogger = dp["connect_logger"]

    logger.debug("Connecting to PostgreSQL", db="main")
    try:
        db_pool = await utils.connect_to_services.wait_postgres(
            logger=dp["db_logger"],
            host=config.PG_HOST,
            port=config.PG_PORT,
            user=config.PG_USER,
            password=config.PG_PASSWORD,
            database=config.PG_DATABASE,
        )
    except tenacity.RetryError:
        logger.error("Failed to connect to PostgreSQL", db="main")
        exit(1)
    else:
        logger.debug("Successfully connected to PostgreSQL", db="main")
    dp["db_pool"] = db_pool


async def close_db_connections(dp: Dispatcher):
    if "db_pool" in dp.workflow_data:
        db_pool: asyncpg.Pool = dp["db_pool"]
        await db_pool.close()


async def setup_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description='Запуск'),
        BotCommand(command='newchat', description='Новый диалог')
    ]

    await bot.set_my_commands(commands=commands)


def setup_logging(dp: Dispatcher):
    dp["aiogram_logger"] = utils.logging.setup_logger().bind(type="aiogram")
    dp["db_logger"] = utils.logging.setup_logger().bind(type="db")
    dp["connect_logger"] = utils.logging.setup_logger().bind(type="connect")
    dp["throttling_logger"] = utils.logging.setup_logger().bind(type="throttling")


async def setup_aiogram(dp: Dispatcher, bot: Bot):
    await setup_commands(bot)
    setup_logging(dp)
    logger = dp["aiogram_logger"]
    logger.debug("Configuring aiogram")
    # await create_db_connections(dp)
    setup_handlers(dp)
    setup_filters(dp)
    setup_middlewares(dp)
    logger.info("Configured aiogram")


async def aiogram_on_startup(dispatcher: Dispatcher, bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)
    await setup_aiogram(dispatcher, bot)
    dispatcher["aiogram_logger"].info("Started polling")


async def aiogram_on_shutdown(dispatcher: Dispatcher, bot: Bot):
    dispatcher["aiogram_logger"].debug("Stopping polling")
    # await close_db_connections(dispatcher)
    await bot.session.close()
    await dispatcher.storage.close()
    dispatcher["aiogram_logger"].info("Stopped polling")


def setup_handlers(dp: Dispatcher):
    dp.include_router(main_router)


def setup_filters(dp: Dispatcher):
    dp.message.filter(ChatTypeFilter('private'))
    dp.message.filter(IsAdmin())


def setup_middlewares(dp: Dispatcher):
    dp.update.outer_middleware(InfoLoggerMiddleware(logger=dp['aiogram_logger']))
    dp.message.middleware(ThrottlingMiddleware(logger=dp['throttling_logger'], throttling_time=8))


def main():
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher()

    dp.startup.register(aiogram_on_startup)
    dp.shutdown.register(aiogram_on_shutdown)
    dp.run_polling(bot)


if __name__ == '__main__':
    main()
