from aiogram import Router, types

router = Router()

@router.message()
async def handle_message(message: types.Message):
    await message.reply("I received your message!")