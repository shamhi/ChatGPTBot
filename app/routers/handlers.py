from aiogram import Router, html, F
from aiogram.types import Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto, InlineQueryResultsButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from app.routers import functions as fn
from app.db.postgres.storage import PostgresConnection
import structlog
import asyncpg

main_router = Router()


# TODO: Use DB for gpt context


@main_router.inline_query(F.query)
async def test_inline(query: InlineQuery):
    text = query.query

    response = await fn.inline_get_response(text=text)

    results = [
        InlineQueryResultArticle(
            id='0',
            title=f"Запрос: {text}",
            description=f"Ответ: {response}",
            input_message_content=InputTextMessageContent(
                message_text=fn.reformat_answer(response),
                parse_mode='markdownv2'
            )
        )
    ]
    await query.answer(results=results, is_personal=True)


@main_router.message(CommandStart())
async def cmd_start(message: Message):
    if message.from_user is None:
        return

    await message.answer(
        f'<b>Добро пожаловать,</b> <a href="tg://user?id={message.from_user.id}">{html.quote(message.from_user.full_name)}</a>\n\n'
        '📃Я чат-бот, который может ответить на любой вопрос (ну почти)📚\n\n'
        'Отправь мне вопрос и я постараюсь на него ответить', parse_mode='html')


@main_router.message(Command('newchat'))
async def cmd_newchat(message: Message, state: FSMContext):
    await state.update_data(history=[])
    await message.answer('Ваша история с ботом очищена, начат новый диалог')


@main_router.message(F.text)
async def gpt_answer(message: Message, state: FSMContext):
    msg = await message.answer("Ваш запрос обрабатывается...")

    state_data = await state.get_data()
    history = state_data.get('history') or []

    await message.bot.send_chat_action(chat_id=message.chat.id, action='typing')
    response = await fn.get_response(
        current_message=message.text,
        history=history,
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=msg.message_id
    )

    if len(history) >= 20:
        history = history[2:]

    history.extend([{'role': 'user', 'message': message.text}, {'role': 'assistant', 'message': response}])
    await state.update_data(history=history)

    await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id,
                                        text=fn.reformat_answer(text=response),
                                        parse_mode='markdownv2')
