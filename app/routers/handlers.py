from aiogram import Router, html, F
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext

from app.models import ChatGPT
from app.keyboards import ikb

main_router = Router()


# TODO: Use DB for gpt context


# @main_router.inline_query(F.query)
async def response_query(query: InlineQuery, state: FSMContext):
    question = query.query

    gpt = ChatGPT(current_message=question)

    results = [
        InlineQueryResultArticle(
            id='0',
            title='Submit',
            description=f'Question: {question}',
            input_message_content=InputTextMessageContent(
                message_text=f'❓Question: {gpt.reformat_response(question)}\n\n'
                             f'🤖Answer: _Нажмите на "☑️" чтобы отправить запрос к GPT_',
                parse_mode='markdownv2'
            ),
            reply_markup=ikb.get_submit_kb(question)
        )
    ]

    await query.answer(results)

    response = await gpt.get_inline_response()
    await state.update_data(inline_question=question, response=response)



# @main_router.callback_query(F.data == 'gpt_query')
async def edit_response(call: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    question = state_data.get('inline_question')
    response = state_data.get('response')
    if not isinstance(question, str) and not isinstance(response, str):
        return

    await call.bot.edit_message_text(inline_message_id=call.inline_message_id,
                                     text=f'❓Question: {ChatGPT.reformat_response(question)}\n\n'
                                          f'🤖Answer: {ChatGPT.reformat_response(response)}',
                                     parse_mode='markdownv2')


# @main_router.inline_query()
async def none_inline(query: InlineQuery):
    results = [
        InlineQueryResultArticle(
            id='0',
            title="Usage",
            description="Usage: @gptshambot [question]",
            input_message_content=InputTextMessageContent(
                message_text='Usage: @gptshambot [question]'
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


@main_router.message(Command('get_chat'))
async def cmd_get_chat(message: Message, command: CommandObject):
    args = command.args
    try:
        chat = await message.bot.get_chat(args)
        await message.answer(f'Chat ID: `{chat.id}`\n'
                             f'User Name: `{chat.username}`\n'
                             f'Title: `{chat.title}`')
    except:
        await message.answer(rf'`{args}` not found', parse_mode='markdownv2')


@main_router.message(Command('newchat'))
async def cmd_newchat(message: Message, state: FSMContext):
    await state.update_data(history=[])
    await message.answer('Ваша история с ботом очищена, начат новый диалог')


@main_router.message(F.text)
async def send_gpt_response(message: Message, state: FSMContext):
    msg = await message.answer("Ваш запрос обрабатывается...")

    state_data = await state.get_data()
    history = state_data.get('history') or []

    gpt = ChatGPT(current_message=message.text, user_history=history)

    await message.bot.send_chat_action(chat_id=message.chat.id, action='typing')
    response = await gpt.get_response()

    if len(history) >= 20:
        history = history[2:]

    history.extend([{'role': 'user', 'message': message.text}, {'role': 'assistant', 'message': response}])
    await state.update_data(history=history)

    await msg.edit_text(text=gpt.reformat_response(response), parse_mode='markdownv2')
