import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.utils.url_utils import validate_url, extract_metadata
from database.db_utils import GoogleSheetsDB
from bot.config import GOOGLE_CREDS_PATH, SPREADSHEET_NAME

router = Router()
db = GoogleSheetsDB(GOOGLE_CREDS_PATH, SPREADSHEET_NAME)
logger = logging.getLogger(__name__)

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
    print(f"URLs retrieved: {urls}")
    if not urls:
        await message.reply("No URLs saved yet!")
        return
    
    response = "📚 Last 5 saved URLs:\n\n"
    for i, url in enumerate(urls, 1):
        response += f"{i}. {url['Title']}\n🔗 {url['URL']}\n\n"
    
    await message.reply(response, disable_web_page_preview=True)

@router.message(Command("delete"))
async def cmd_delete_url(message: types.Message):
    urls = await db.get_urls()
    if not urls:
        await message.reply("No URLs saved yet!")
        return
    
    response = "🗑️ Select the number of the URL to delete:\n\n"
    for i, url in enumerate(urls, 1):
        response += f"{i}. {url['Title']}\n🔗 {url['URL']}\n\n"
    
    await message.reply(response, disable_web_page_preview=True)

@router.message(Command("search"))
async def cmd_search_urls(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Please provide a search query:\n/search [query]")
        return
    
    query = parts[1].lower()
    urls = await db.get_urls()
    matching_urls = [url for url in urls if query in url['Title'].lower() or query in url['Description'].lower()]
    
    if not matching_urls:
        await message.reply("No matching URLs found!")
        return
    
    response = "🔍 Search results:\n\n"
    for i, url in enumerate(matching_urls, 1):
        response += f"{i}. {url['Title']}\n🔗 {url['URL']}\n\n"
    
    await message.reply(response, disable_web_page_preview=True)

@router.message()
async def handle_message(message: types.Message):
    text = message.text.lower()
    
    # Handle URL input directly (auto-save)
    if text.startswith(('http://', 'https://')):
        url = text.strip()
        
        # Validate URL
        is_valid, error_msg = await validate_url(url)
        if not is_valid:
            await message.reply(f"❌ {error_msg}")
            return
        
        # Show processing message
        processing_msg = await message.reply("Processing URL... ⏳")
        
        # Extract metadata
        metadata, error_msg = await extract_metadata(url)
        if not metadata:
            await processing_msg.edit_text(f"❌ {error_msg}")
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
        return

    # Handle multiple deletion inputs (1 2 3 or 1,2,3)
    if any(char.isdigit() for char in text):
        # Split input by comma or space and convert to integers
        try:
            numbers = [int(num.strip()) for num in text.replace(',', ' ').split()]
            urls = await db.get_urls()
            deleted_urls = []
            failed_urls = []

            for num in numbers:
                index = num - 1
                if 0 <= index < len(urls):
                    url = urls[index]['URL']
                    if await db.delete_url(url):
                        deleted_urls.append(f"{num}. {urls[index]['Title']}")
                    else:
                        failed_urls.append(f"{num}. {urls[index]['Title']}")
                else:
                    await message.reply(f"❌ Invalid number: {num}")

            # Prepare response message
            response = []
            if deleted_urls:
                response.append("✅ Successfully deleted:\n" + "\n".join(deleted_urls))
            if failed_urls:
                response.append("⚠️ Failed to delete:\n" + "\n".join(failed_urls))

            if response:
                await message.reply("\n\n".join(response))

            # Show updated list
            updated_urls = await db.get_urls()
            if updated_urls:
                response = "📚 Updated URL list:\n\n"
                for i, url in enumerate(updated_urls, 1):
                    response += f"{i}. {url['Title']}\n🔗 {url['URL']}\n\n"
                await message.answer(response, disable_web_page_preview=True)
            return
        except ValueError:
            pass

    # Handle search command
    elif text.startswith('search'):
        await cmd_search_urls(message)
        return

    # Default response with keyboard
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📚 Help", callback_data="help")
    keyboard.button(text="🔍 Search", callback_data="search")
    keyboard.button(text="📄 List URLs", callback_data="list")
    keyboard.button(text="➕ Add URL", callback_data="add")
    keyboard.button(text="❌ Delete URL", callback_data="delete")
    keyboard.adjust(3)
    
    await message.reply(
        "I can help you manage URLs!\n"
        "Use the buttons below or:\n"
        "• Send numbers (e.g., '1 2 3' or '1,2,3') to delete multiple URLs\n"
        "• Send a URL directly to add it\n"
        "• Type 'search' followed by keywords to search",
        reply_markup=keyboard.as_markup()
    )