from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📚 Help", callback_data="help")
    keyboard.button(text="🔍 Search", callback_data="search")
    
    await message.reply(
        "Welcome to MetaMind Bot! 🤖\n\n"
        "I can help you manage and analyze your URLs.\n"
        "Use /help to see available commands.",
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
        "/search [query] - Search saved URLs"
    )
    await message.reply(help_text)