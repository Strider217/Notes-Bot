from aiogram import F,Router
from aiogram.filters import Command
from aiogram.types import Message

rt = Router()

@rt.message()
async def other_message(msg: Message):
    await msg.reply(text='Че ты несешь вообще?')