from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_submit_kb(question: str):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='☑️', callback_data='gpt_query'),
            InlineKeyboardButton(text='Fork', switch_inline_query_current_chat=question)
        ]
    ])

    return kb
