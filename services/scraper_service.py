# =============================================================================
# FILE: services/scraper_service.py
# PURPOSE: University ki website se information automatically scrape karta hai.
#          Iska matlab hai: Website ko read karo aur text nikalo.
#
# ⚠️  NAYI UNIVERSITY KE LIYE: SCRAPE_URLS config mein change karo
#
# Flow: URL list -> Download pages -> Extract text -> Save JSON
# =============================================================================

import json
import time
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from config.settings import SCRAPE_URLS, SCRAPED_DATA_PATH

logger = logging.getLogger(__name__)


class UniversityScraper:
    """
    University website scraper.
    
    Yeh class:
    1. URLs ki list leti hai
    2. Har URL download karti hai
    3. Unwanted HTML tags remove karti hai (nav, footer, ads, etc.)
    4. Clean text save karti hai JSON mein
    
    Nayi university ke liye: config/settings.py mein SCRAPE_URLS list change karo
    """
    
    def __init__(self):
        self.output_path = Path(SCRAPED_DATA_PATH)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # HTTP request headers (browser ki tarah request karo)
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        # Koi element scrape nahi karna chahiye
        # ⚠️  Nayi website ke liye adjust karo
        self.tags_to_remove = [
            'script',   # JavaScript
            'style',    # CSS
            'nav',      # Navigation menu
            'footer',   # Footer
            'header',   # Header (usually logo/menu)
            'aside',    # Sidebar
            'iframe',   # Embedded frames
            'form',     # Forms
            'button',   # Buttons
            'svg',      # Icons
        ]
        
        logger.info(f"🌐 Scraper initialized. Output: {self.output_path}")
    
    def scrape_url(self, url: str) -> Optional[Dict]:
        """
        Single URL scrape karo.
        
        Args:
            url: Website URL
        
        Returns:
            Dict with title, content, url - ya None if failed
        """
        logger.info(f"  📥 Scraping: {url}")
        
        try:
            # Page download karo
            response = requests.get(
                url,
                headers=self.headers,
                timeout=30,
                verify=True
            )
            
            # Status check
            response.raise_for_status()
            
            # HTML parse karo
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Title extract karo
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
            
            # Unwanted tags remove karo
            for tag in self.tags_to_remove:
                for element in soup.find_all(tag):
                    element.decompose()
            
            # Main content dhundo
            # Try different content containers
            content_element = (
                soup.find('main') or          # <main> tag
                soup.find(id='main-content') or
                soup.find(class_='main-content') or
                soup.find('article') or       # <article> tag
                soup.find(class_='content') or
                soup.find('body')             # Fallback: full body
            )
            
            if not content_element:
                logger.warning(f"  ⚠️  No content found on: {url}")
                return None
            
            # Text extract karo (extra whitespace clean karo)
            raw_text = content_element.get_text(separator=' ', strip=True)
            
            # Text clean karo
            clean_text = self._clean_text(raw_text)
            
            # Too short text skip karo
            if len(clean_text) < 100:
                logger.warning(f"  ⚠️  Too short content ({len(clean_text)} chars): {url}")
                return None
            
            logger.info(f"  ✅ Scraped: {len(clean_text)} chars from {url}")
            
            return {
                "url": url,
                "title": title,
                "content": clean_text,
                "char_count": len(clean_text)
            }
            
        except requests.exceptions.ConnectionError:
            logger.error(f"  ❌ Connection failed: {url}")
            return None
        except requests.exceptions.Timeout:
            logger.error(f"  ❌ Timeout: {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"  ❌ HTTP Error {e.response.status_code}: {url}")
            return None
        except Exception as e:
            logger.error(f"  ❌ Error scraping {url}: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """
        Text ko clean karo:
        - Extra whitespace remove karo
        - Multiple newlines single newline banao
        - Unwanted characters remove karo
        """
        import re
        
        # Multiple spaces ko single space banao
        text = re.sub(r' +', ' ', text)
        
        # Multiple newlines ko double newline banao
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Tab characters remove karo
        text = re.sub(r'\t+', ' ', text)
        
        # Leading/trailing whitespace remove karo
        text = text.strip()
        
        return text
    
    def scrape_all(self, urls: List[str] = None) -> List[Dict]:
        """
        Saari URLs scrape karo aur results return karo.
        
        Args:
            urls: URLs ki list (None = config se use karo)
        
        Returns:
            List of scraped page dicts
        """
        if urls is None:
            urls = SCRAPE_URLS
        
        # Empty URLs filter karo
        urls = [u.strip() for u in urls if u and u.strip()]
        
        if not urls:
            logger.warning("⚠️  No URLs to scrape!")
            return []
        
        logger.info(f"🌐 Starting to scrape {len(urls)} URLs...")
        
        results = []
        
        for i, url in enumerate(urls, 1):
            logger.info(f"[{i}/{len(urls)}] Processing: {url}")
            
            result = self.scrape_url(url)
            
            if result:
                results.append(result)
            
            # Polite delay - server par load mat dalo
            if i < len(urls):
                time.sleep(1)  # 1 second wait
        
        logger.info(f"\n✅ Scraping complete! {len(results)}/{len(urls)} URLs successful")
        
        return results
    
    def save_scraped_data(self, data: List[Dict], filename: str = "scraped_data.json") -> str:
        """
        Scraped data ko JSON file mein save karo.
        
        Args:
            data: Scraped data list
            filename: Output filename
        
        Returns:
            str: Saved file path
        """
        output_file = self.output_path / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Saved scraped data: {output_file}")
        logger.info(f"   Total pages: {len(data)}")
        logger.info(f"   Total chars: {sum(d.get('char_count', 0) for d in data):,}")
        
        return str(output_file)
    
    def run(self) -> str:
        """
        Complete scraping run karo: scrape + save.
        Yahi main method hai jo script se call hota hai.
        
        Returns:
            str: Saved file path
        """
        # Scrape karo
        data = self.scrape_all()
        
        if not data:
            logger.error("❌ No data scraped!")
            return ""
        
        # Save karo
        saved_path = self.save_scraped_data(data)
        
        return saved_path


# Test ke liye
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    scraper = UniversityScraper()
    
    # Single URL test
    result = scraper.scrape_url("https://www.mul.edu.pk/en/admissions-open")
    
    if result:
        print(f"\n✅ Title: {result['title']}")
        print(f"📊 Content length: {result['char_count']} chars")
        print(f"\nFirst 500 chars:")
        print(result['content'][:500])