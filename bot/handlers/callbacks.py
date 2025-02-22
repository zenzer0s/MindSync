from aiogram import Router, types, F
from database.db_utils import GoogleSheetsDB
from bot.config import GOOGLE_CREDS_PATH, SPREADSHEET_NAME

router = Router()
db = GoogleSheetsDB(GOOGLE_CREDS_PATH, SPREADSHEET_NAME)

@router.callback_query(F.data == "help")
async def process_help_callback(callback: types.CallbackQuery):
    await callback.answer("Showing help...")
    help_text = (
        "Available commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/add [url] - Add a new URL\n"
        "/list - List saved URLs\n"
        "/delete [url] - Delete a URL\n"
        "/search [query] - Search saved URLs"
    )
    await callback.message.answer(help_text)

@router.callback_query(F.data == "list")
async def process_list_callback(callback: types.CallbackQuery):
    await callback.answer("Listing URLs...")
    urls = await db.get_urls(limit=5)
    if not urls:
        await callback.message.answer("No URLs saved yet!")
        return
    
    response = "📚 Last 5 saved URLs:\n\n"
    for i, url in enumerate(urls, 1):
        response += f"{i}. {url['Title']}\n🔗 {url['URL']}\n\n"
    
    await callback.message.answer(response, disable_web_page_preview=True)

@router.callback_query(F.data == "add")
async def process_add_callback(callback: types.CallbackQuery):
    await callback.answer("Please send the URL to add.")
    await callback.message.answer("Send me the URL you want to add.")

@router.callback_query(F.data == "delete")
async def process_delete_callback(callback: types.CallbackQuery):
    await callback.answer("Please send the URL to delete.")
    await callback.message.answer("Send me the URL you want to delete.")

@router.callback_query(F.data == "search")
async def process_search_callback(callback: types.CallbackQuery):
    await callback.answer("Please enter your search query.")
    await callback.message.answer("Send me what you want to search for.")