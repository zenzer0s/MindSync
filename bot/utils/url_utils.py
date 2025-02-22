import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import logging

logger = logging.getLogger(__name__)

async def validate_url(url: str) -> tuple[bool, str]:
    """
    Validate if the given string is a valid URL.
    Returns a tuple of (is_valid: bool, message: str)
    """
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False, "Invalid URL format. URL must start with http:// or https://"
        return True, ""
    except Exception as e:
        logger.error(f"URL validation error: {e}")
        return False, f"Invalid URL: {str(e)}"

async def extract_metadata(url: str) -> tuple[dict | None, str]:
    """
    Extract metadata from the given URL with improved error handling.
    Returns a tuple of (metadata: dict | None, error_message: str)
    """
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                if response.status == 404:
                    return None, "URL not found (404 error)"
                elif response.status == 403:
                    return None, "Access forbidden (403 error)"
                elif response.status != 200:
                    return None, f"Failed to fetch URL (HTTP {response.status})"
                
                try:
                    html = await response.text()
                except UnicodeDecodeError:
                    html = await response.read()
                    html = html.decode('utf-8', errors='ignore')
                
                soup = BeautifulSoup(html, 'html.parser')
                
                metadata = {
                    'url': str(response.url),  # Use final URL after redirects
                    'title': '',
                    'description': '',
                    'image': ''
                }
                
                # Get title with fallbacks
                for title_source in [
                    lambda: soup.title.string,
                    lambda: soup.find('meta', property='og:title')['content'],
                    lambda: soup.find('h1').text,
                    lambda: str(response.url)
                ]:
                    try:
                        metadata['title'] = title_source().strip()
                        if metadata['title']:
                            break
                    except (AttributeError, KeyError, TypeError):
                        continue
                
                # Get description
                for desc in [
                    soup.find('meta', attrs={'name': 'description'}),
                    soup.find('meta', property='og:description'),
                    soup.find('meta', attrs={'name': 'twitter:description'})
                ]:
                    if desc and desc.get('content'):
                        metadata['description'] = desc['content'].strip()
                        break
                
                # Get image with absolute URL
                for img in [
                    soup.find('meta', property='og:image'),
                    soup.find('meta', attrs={'name': 'twitter:image'}),
                    soup.find('link', rel='icon')
                ]:
                    if img:
                        img_url = img.get('content') or img.get('href')
                        if img_url:
                            metadata['image'] = urljoin(str(response.url), img_url)
                            break
                
                # Clean and validate metadata
                metadata = {k: str(v).strip() for k, v in metadata.items()}
                
                if not metadata['title']:
                    metadata['title'] = str(response.url)
                
                logger.info(f"Successfully extracted metadata from {url}")
                return metadata, ""
                
    except aiohttp.ClientError as e:
        error_msg = f"Network error: {str(e)}"
        logger.error(f"{error_msg} while fetching {url}")
        return None, error_msg
    except Exception as e:
        error_msg = f"Error processing URL: {str(e)}"
        logger.error(f"{error_msg} for {url}")
        return None, error_msg