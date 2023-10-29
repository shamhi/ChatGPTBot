from aiogram import Router, html, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from app.routers import functions as fn

main_router = Router()


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

    rand_pc = randint(3, 25)

    await sleep(.5)
    await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id,
                                        text=f"<b>Обработка</b> <code>{rand_pc}%..</code>",
                                        parse_mode='html')

    state_data = await state.get_data()
    user_msg_1 = state_data.get('previous_user_msg_1')
    assistant_msg_1 = state_data.get('previous_assistant_msg_1')

    user_msg_2 = state_data.get('previous_user_msg_2')
    assistant_msg_2 = state_data.get('previous_assistant_msg_2')

    user_msg_3 = state_data.get('previous_user_msg_3')
    assistant_msg_3 = state_data.get('previous_assistant_msg_3')

    response = await fn.get_response(current_message=message.text,
                                     previous_user_message=[user_msg_1, user_msg_2, user_msg_3],
                                     previous_assistant_message=[assistant_msg_1, assistant_msg_2, assistant_msg_3])

    await state.update_data(previous_user_msg_2=user_msg_1, previous_assistant_msg_2=assistant_msg_1)
    await state.update_data(previous_user_msg_3=user_msg_2, previous_assistant_msg_3=assistant_msg_2)

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

            await state.update_data(previous_user_msg_1=message.text, previous_assistant_msg_1=response)

            return
        else:
            await message.bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id,
                                                text='<b>Произошла неизвестная ошибка\nПопробуйте позже...</b>',
                                                parse_mode='html')
            return
