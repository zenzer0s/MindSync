from aiogram import Router, types, F

router = Router()

@router.callback_query(F.data == "help")
async def process_help_callback(callback: types.CallbackQuery):
    await callback.answer("Showing help...")
    help_text = (
        "Available commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/add [url] - Add a new URL\n"
        "/list - List saved URLs\n"
        "/delete [url] - Delete a URL"
    )
    await callback.message.answer(help_text)

@router.callback_query(F.data == "search")
async def process_search_callback(callback: types.CallbackQuery):
    await callback.answer("Please enter your search query...")
    await callback.message.answer("Send me what you want to search for.")