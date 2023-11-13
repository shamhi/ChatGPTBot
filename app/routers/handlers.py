from aiogram import Router, html, F
from aiogram.types import Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto, InlineQueryResultsButton
from aiogram.filters import CommandStart
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


@main_router.message(F.text)
async def gpt_answer(message: Message, state: FSMContext):
    from random import randint
    from asyncio import sleep


    msg = await message.answer("<b>Обработка</b> <code>0%..</code>", parse_mode='html')
    rand_pc = randint(10, 35)
    await sleep(.5)
    await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id,
                                        text=f"<b>Обработка</b> <code>{rand_pc}%..</code>",
                                        parse_mode='html')

    state_data = await state.get_data()

    history = state_data.get('history')
    history = [] if history is None else history

    await message.bot.send_chat_action(chat_id=message.chat.id, action='typing')
    response = await fn.get_response(
        current_message=message.text,
        history=history,
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=msg.message_id
    )

    if not response:
        return

    if len(history) >= 20:
        history.pop(0)
        history.pop(0)

    history.append({'role': 'user', 'message': message.text})
    history.append({'role': 'assistant', 'message': response})

    await state.update_data(history=history)

    percent, dots = rand_pc, 1
    while True:
        dots = dots if dots <= 3 else 1
        percent += randint(1, 5)

        text = f"<b>Обработка</b> <code>{str(min(percent, 100))}%{'.' * dots}</code>"
        await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=text,
                                            parse_mode='html')
        dots += 1
        if response:
            text = f"<b>Обработка</b> <code>{str(percent + ((100 - percent) // 2))}%{'.' * dots}</code>"
            await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=text,
                                                parse_mode='html')
            text = f"<b>Обработка</b> <code>100%...</code>"
            await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=text,
                                                parse_mode='html')

            try:
                await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id,
                                                    text=fn.reformat_answer(text=response),
                                                    parse_mode='markdownv2')
            except:
                await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=response,
                                                    parse_mode=None)

            return
        else:
            await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id,
                                                text='<b>Произошла неизвестная ошибка\nПопробуйте позже...</b>',
                                                parse_mode='html')
            return
