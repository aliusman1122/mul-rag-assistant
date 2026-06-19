# =============================================================================
# FILE: scripts/scrape.py
# PURPOSE: University website scrape karne ka standalone script.
#          Yeh sirf ek baar run karna hai (ya jab website update ho).
#
# Run karne ka tareeqa:
#   python scripts/scrape.py
#
# ⚠️  NAYI UNIVERSITY KE LIYE:
#   config/settings.py mein SCRAPE_URLS list update karo
# =============================================================================

import sys
import os
import logging

# Project root ko path mein add karo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.scraper_service import UniversityScraper
from config.settings import SCRAPE_URLS

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/scrape.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Logs folder create karo
os.makedirs('logs', exist_ok=True)


def main():
    """Main scraping function."""
    print("=" * 60)
    print("🌐 University Website Scraper")
    print("=" * 60)
    print(f"\n📋 URLs to scrape: {len(SCRAPE_URLS)}")
    
    for i, url in enumerate(SCRAPE_URLS, 1):
        print(f"  {i}. {url}")
    
    print("\n🚀 Starting scraper...\n")
    
    scraper = UniversityScraper()
    saved_path = scraper.run()
    
    if saved_path:
        print(f"\n✅ Scraping complete!")
        print(f"📁 Data saved to: {saved_path}")
        print(f"\n💡 Next step: Run ingestion script")
        print(f"   python scripts/ingest.py")
    else:
        print("\n❌ Scraping failed! Check the URLs and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()