from aiogram import Router, types, F
from aiogram.filters import Command
from ..utils.url_utils import validate_url, extract_metadata
from ...database.db_utils import GoogleSheetsDB
from ..config import GOOGLE_CREDS_PATH, SPREADSHEET_NAME

router = Router()
db = GoogleSheetsDB(GOOGLE_CREDS_PATH, SPREADSHEET_NAME)

@router.message(Command("add"))
async def cmd_add_url(message: types.Message):
    # Extract URL from message
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Please provide a URL:\n/add [url]")
        return
    
    url = parts[1]
    
    # Validate URL
    if not await validate_url(url):
        await message.reply("Please provide a valid URL!")
        return
    
    # Show processing message
    processing_msg = await message.reply("Processing URL... ⏳")
    
    # Extract metadata
    metadata = await extract_metadata(url)
    if not metadata:
        await processing_msg.edit_text("Failed to extract metadata from the URL!")
        return
    
    # Format response message
    response = (
        f"✅ URL added successfully!\n\n"
        f"📝 Title: {metadata['title']}\n"
        f"🔗 URL: {metadata['url']}\n"
    )
    
    if metadata['description']:
        response += f"📄 Description: {metadata['description'][:100]}...\n"
    
    # Save metadata to database
    if await db.add_url(metadata):
        response += "\n✨ Saved to database!"
    else:
        response += "\n⚠️ Failed to save to database!"
    
    await processing_msg.edit_text(response, disable_web_page_preview=True)

@router.message(Command("list"))
async def cmd_list_urls(message: types.Message):
    urls = await db.get_urls(limit=5)
    if not urls:
        await message.reply("No URLs saved yet!")
        return
    
    response = "📚 Last 5 saved URLs:\n\n"
    for i, url in enumerate(urls, 1):
        response += f"{i}. {url['title']}\n🔗 {url['url']}\n\n"
    
    await message.reply(response, disable_web_page_preview=True)

@router.message()
async def handle_message(message: types.Message):
    await message.reply(
        "I can help you manage URLs!\n"
        "Use /help to see available commands."
    )