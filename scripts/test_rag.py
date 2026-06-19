# =============================================================================
# FILE: scripts/test_rag.py
# PURPOSE: RAG system ka quick test karo
#
# Run karne ka tareeqa:
#   python scripts/test_rag.py
# =============================================================================

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.WARNING)  # Sirf warnings aur errors

def main():
    print("=" * 60)
    print("🧪 RAG System Quick Test")
    print("=" * 60)
    
    # Test questions
    test_questions = [
        "What is the fee for BS Computer Science?",
        "What are the admission requirements for BS AI?",
        "How can I contact the admission office?",
        "What programs does MUL offer?",
        "When does admission open?",
    ]
    
    try:
        from services.rag_service import get_rag_service
        
        service = get_rag_service()
        stats = service.get_stats()
        
        print(f"\n📊 Database Status:")
        print(f"   Documents: {stats['database'].get('total_documents', 0)}")
        print(f"   LLM Provider: {stats['llm_provider']}")
        print(f"   Ready: {stats['ready']}")
        
        if not stats['ready']:
            print("\n⚠️  Database is empty! Run ingestion first:")
            print("   python scripts/scrape.py")
            print("   python scripts/ingest.py")
            return
        
        print(f"\n🧪 Running {len(test_questions)} test questions...\n")
        
        passed = 0
        failed = 0
        
        for i, question in enumerate(test_questions, 1):
            print(f"[{i}/{len(test_questions)}] {question}")
            
            result = service.query(question, use_llm=False)  # No LLM, just retrieval
            
            docs_found = result.get("docs_retrieved", 0)
            
            if docs_found > 0:
                print(f"  ✅ Found {docs_found} relevant documents")
                print(f"  📄 Top source: {result['sources'][0]['source'] if result.get('sources') else 'N/A'}")
                passed += 1
            else:
                print(f"  ❌ No documents found!")
                failed += 1
            
            print()
        
        print("=" * 60)
        print(f"📊 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("✅ All tests passed! RAG system is working correctly.")
        else:
            print("⚠️  Some tests failed. Check your data ingestion.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure to run ingestion first:")
        print("  python scripts/ingest.py")


if __name__ == "__main__":
    main()