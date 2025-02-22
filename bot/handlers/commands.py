from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📚 Help", callback_data="help")
    keyboard.button(text="🔍 Search", callback_data="search")
    keyboard.button(text="📄 List URLs", callback_data="list")
    keyboard.button(text="➕ Add URL", callback_data="add")
    keyboard.button(text="❌ Delete URL", callback_data="delete")
    keyboard.adjust(3)  # Adjust to 3 columns
    
    await message.reply(
        "Welcome to MetaMind Bot! 🤖\n\n"
        "I can help you manage and analyze your URLs.\n"
        "Use the buttons below to interact with me.",
        reply_markup=keyboard.as_markup()
    )

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "Available commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/add [url] - Add a new URL\n"
        "/list - List saved URLs\n"
        "/delete [url] - Delete a URL\n"
        "/search [query] - Search saved URLs"
    )
    await message.reply(help_text)