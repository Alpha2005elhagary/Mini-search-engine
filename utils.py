# utils.py - Display and helper functions
from datetime import datetime

def display_results(results, search_engine, page=0, per_page=5):
    """Display paginated results with snippets"""
    if not results:
        print("\n❌ No results found.")
        return 0, 0
    
    start = page * per_page
    end = start + per_page
    page_results = results[start:end]
    
    total_pages = (len(results) + per_page - 1) // per_page
    
    print(f"\n📄 Results {start+1}-{min(end, len(results))} of {len(results)} (Page {page+1}/{total_pages})")
    print("-" * 60)
    
    for idx, (doc_id, score) in enumerate(page_results):
        doc = search_engine.indexer.documents[doc_id]
        print(f"\n{start+idx+1}. 📄 {doc['filename']}")
        print(f"   📁 Type: {doc['type']} | ⭐ Score: {score}")
        print(f"   📅 Modified: {doc['date']}")
        
        # Get snippet (simplified - extract first few words of query)
        query_terms = []  # Would need to pass query terms
        snippet = search_engine.get_snippet(doc_id, [], 100)
        print(f"   📝 Preview: {snippet[:100]}...")
    
    return page, total_pages

def show_stats(indexer):
    """Show detailed stats about the index"""
    print("\n" + "="*50)
    print("📊 INDEX STATISTICS")
    print("="*50)
    
    if indexer.doc_counter == 0:
        print("No documents indexed yet!")
        return
    
    # Total documents
    print(f"\n📚 Total documents: {indexer.doc_counter}")
    
    # Breakdown by type
    type_counts = {}
    for doc in indexer.documents.values():
        t = doc['type']
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print(f"\n📁 Breakdown by file type:")
    for t, count in sorted(type_counts.items()):
        print(f"   {t}: {count} files")
    
    # Top 10 terms
    terms = sorted(indexer.inverted_index.items(), 
                   key=lambda x: len(x[1]), reverse=True)[:10]
    
    print(f"\n🔥 Top 10 most frequent terms:")
    for i, (word, docs) in enumerate(terms, 1):
        print(f"   {i}. '{word}' - appears in {len(docs)} documents")
    
    # Vocabulary size
    print(f"\n📖 Unique terms in index: {len(indexer.inverted_index)}")

def get_date_input(prompt):
    """Get date from user input"""
    print(prompt)
    date_str = input("   (YYYY-MM-DD, or press Enter to skip): ")
    if date_str.strip():
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            print("   Invalid date format, skipping...")
    return None

def get_file_type_filter():
    """Get file type filter from user"""
    print("\n📁 Filter by file type?")
    print("   Options: TXT, PDF, JSON, CSV, XLSX")
    print("   (comma-separated, or press Enter to skip): ")
    types = input("   ").upper().strip()
    if types:
        return [t.strip() for t in types.split(',')]
    return None















