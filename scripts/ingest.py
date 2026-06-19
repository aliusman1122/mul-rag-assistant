# =============================================================================
# FILE: scripts/ingest.py
# PURPOSE: Documents ko vector database mein store karne ka script.
#          Yeh script PDFs aur scraped data process karta hai.
#
# Run karne ka tareeqa:
#   python scripts/ingest.py
#   python scripts/ingest.py --reset    # Database pehle clear karo
#
# ⚠️  NAYI UNIVERSITY KE LIYE:
#   1. data/pdfs/ mein nayi PDFs daal do
#   2. Pehle scripts/scrape.py run karo
#   3. Phir yeh script run karo
# =============================================================================

import sys
import os
import argparse
import logging
import time

# Project root ko path mein add karo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Logging setup
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/ingest.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main ingestion function."""
    
    # Arguments parse karo
    parser = argparse.ArgumentParser(
        description='Ingest documents into vector database'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset database before ingesting'
    )
    args = parser.parse_args()
    
    print("=" * 60)
    print("⚙️  Document Ingestion Pipeline")
    print("=" * 60)
    
    if args.reset:
        print("\n⚠️  WARNING: Database will be reset first!")
    
    print("\n📋 Pipeline Steps:")
    print("  1️⃣  Load documents (PDFs + scraped data)")
    print("  2️⃣  Split into chunks")
    print("  3️⃣  Generate embeddings")
    print("  4️⃣  Store in ChromaDB")
    print()
    
    start_time = time.time()
    
    # Import here to avoid circular imports
    from services.ingest_service import get_ingest_service
    
    try:
        ingest_service = get_ingest_service()
        result = ingest_service.ingest_all(reset_first=args.reset)
        
        elapsed = time.time() - start_time
        
        if result["status"] == "success":
            print("\n" + "=" * 60)
            print("✅ INGESTION COMPLETE!")
            print("=" * 60)
            print(f"\n📊 Results:")
            print(f"   Documents loaded:  {result.get('documents_loaded', 0)}")
            print(f"   Chunks created:    {result.get('chunks_created', 0)}")
            print(f"   Chunks in DB:      {result.get('chunks_stored', 0)}")
            print(f"   Avg chunk size:    {result.get('avg_chunk_size', 0)} chars")
            print(f"   Time taken:        {elapsed:.1f} seconds")
            print(f"\n💡 Next step: Start the server")
            print(f"   uvicorn api.main:app --reload")
        else:
            print(f"\n❌ Ingestion failed: {result.get('message', 'Unknown error')}")
            print("\n💡 Troubleshooting:")
            print("   1. Make sure PDFs are in data/pdfs/")
            print("   2. Run: python scripts/scrape.py (for web data)")
            print("   3. Check: data/scraped/ folder")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()