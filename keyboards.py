from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

main_kb = ReplyKeyboardBuilder()

button1 = KeyboardButton(text = '✍️')
button2 = KeyboardButton(text = '👀')
button3 = KeyboardButton(text = '🗓️')

main_kb.row(button1,button2,button3, width=4)

main_kb = main_kb.as_markup(one_time_keyboard = True,
                            resize_keyboard = True
                            )


del_kb = ReplyKeyboardBuilder()

button4 = KeyboardButton(text = '❌')
button5 = KeyboardButton(text = '🔙')

del_kb.row(button4,button5, width=2)

del_kb = del_kb.as_markup(one_time_keyboard = True,
                            resize_keyboard = True
                            )
