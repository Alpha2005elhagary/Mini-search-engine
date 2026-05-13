# main.py - Complete application
import os
from indexer import Indexer
from search import SearchEngine
from utils import display_results, show_stats, get_date_input, get_file_type_filter
from datetime import datetime

class MiniSearchEngine:
    def __init__(self):
        self.indexer = Indexer()
        self.search_engine = None
        self.current_results = []
        self.current_page = 0
        self.results_per_page = 5
        
    def run(self):
        print("\n" + "🔍" * 20)
        print("   MINI SEARCH ENGINE - Student Project")
        print("🔍" * 20)
        
        # Try to load existing index
        if self.indexer.load_index():
            print("\n✅ Loaded existing index!")
            self.search_engine = SearchEngine(self.indexer)
        
        while True:
            self.show_main_menu()
            choice = input("\n👉 Choose option: ")
            
            if choice == '1':
                self.build_index()
            elif choice == '2':
                if self.indexer.doc_counter > 0:
                    self.search_menu()
                else:
                    print("❌ No index found! Build index first (option 1).")
            elif choice == '3':
                show_stats(self.indexer)
            elif choice == '4':
                print("\n👋 Thanks for using Mini Search Engine!")
                break
            else:
                print("❌ Invalid choice!")
                
    def show_main_menu(self):
        print("\n" + "="*50)
        print(f"📊 Indexed: {self.indexer.doc_counter} documents")
        print("="*50)
        print("1. 📚 Build/Refresh Index")
        print("2. 🔎 Search Documents")
        print("3. 📊 View Statistics")
        print("4. 🚪 Exit")
    
    def build_index(self):
        print("\n" + "-"*40)
        print("📚 BUILD NEW INDEX")
        print("-"*40)
        
        # Step 1: Choose formats
        self.indexer.choose_formats()
        
        if not self.indexer.selected_formats:
            print("❌ No formats selected!")
            return
        
        # Step 2: Get folder path
        folder = input("\n📁 Enter folder path (default: 'data'): ").strip()
        if not folder:
            folder = "data"
        
        if not os.path.exists(folder):
            print(f"❌ Folder '{folder}' doesn't exist!")
            create = input("   Create it? (y/n): ").lower()
            if create == 'y':
                os.makedirs(folder)
                print(f"✅ Created '{folder}'. Add files and run again.")
            return
        
        # Step 3: Build index
        success = self.indexer.build_index(folder)
        
        if success:
            self.search_engine = SearchEngine(self.indexer)
            print("\n✅ Index ready for searching!")
    
    def search_menu(self):
        """Handle search with all features"""
        print("\n" + "-"*40)
        print("🔎 SEARCH")
        print("-"*40)
        
        # Get search query
        print("\n💡 Query examples:")
        print("   • Boolean:   cat AND dog")
        print("   • Phrase:    \"information retrieval\"")
        print("   • Fuzzy:     retrieval~")
        print("   • Wildcard:  comp*")
        print("   • Group:     (cat OR dog) AND NOT mouse")
        
        query = input("\n📝 Enter search query: ").strip()
        
        if not query:
            print("❌ No query entered!")
            return
        
        # Get date filters
        print("\n📅 DATE FILTER (optional)")
        date_from = get_date_input("   From date:")
        date_to = get_date_input("   To date:")
        
        # Get file type filter
        file_types = get_file_type_filter()
        
        # Perform search
        print("\n🔍 Searching...")
        results = self.search_engine.search(query, date_from, date_to, file_types)
        
        # Handle no results
        if not results:
            print("\n❌ No documents match your search.")
            
            # Did you mean?
            suggestion = self.search_engine.did_you_mean(query)
            if suggestion:
                print(f"💡 Did you mean: '{suggestion}'?")
                try_again = input("   Search with suggestion? (y/n): ").lower()
                if try_again == 'y':
                    results = self.search_engine.search(suggestion, date_from, date_to, file_types)
        
        # Display results with pagination
        if results:
            self.current_results = results
            self.current_page = 0
            self.show_results_page()
    
    def show_results_page(self):
        """Show current page of results"""
        if not self.current_results:
            return
        
        page, total_pages = display_results(
            self.current_results, 
            self.search_engine,
            self.current_page,
            self.results_per_page
        )
        
        if total_pages > 1:
            print(f"\n📄 Page {self.current_page + 1}/{total_pages}")
            print("[N]ext  [P]revious  [Q]uit to menu")
            choice = input("👉 ").lower()
            
            if choice == 'n' and self.current_page + 1 < total_pages:
                self.current_page += 1
                self.show_results_page()
            elif choice == 'p' and self.current_page > 0:
                self.current_page -= 1
                self.show_results_page()

# Run the application
if __name__ == "__main__":
    app = MiniSearchEngine()
    app.run()