import re
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup

async def validate_url(url: str) -> bool:
    """Validate if the given string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

async def extract_metadata(url: str) -> dict:
    """Extract metadata from the given URL."""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                metadata = {
                    'url': url,
                    'title': soup.title.string if soup.title else '',
                    'description': '',
                    'image': ''
                }
                
                # Get meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    metadata['description'] = meta_desc.get('content', '')
                
                # Get OpenGraph image
                og_image = soup.find('meta', property='og:image')
                if og_image:
                    metadata['image'] = og_image.get('content', '')
                
                return metadata
        except Exception as e:
            return None