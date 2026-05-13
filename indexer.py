# indexer.py - Complete updated version with enhanced tokenization
import re
import os
import json
from datetime import datetime
from file_handlers import HANDLERS

# STOP_WORDS set - common words to exclude from index
STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'while', 'from', 'has', 'he',
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'into', 'was', 'were',
    'will', 'with', 'i', 'you', 'we', 'they', 'this', 'that', 'these', 'those',
    'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
    'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
    'but', 'do', 'does', 'doing', 'did', 'done', 'have', 'having', 'been', 'being',
    'can', 'could', 'will', 'would', 'should', 'may', 'might', 'must' 
}

class Indexer:
    def __init__(self, index_path="index_data/index.json"):
        self.index_path = index_path
        self.inverted_index = {}  # word -> {doc_id: [positions]}
        self.documents = {}       # doc_id -> {path, type, date, content}
        self.doc_counter = 0
        self.selected_formats = []
        
    def choose_formats(self):
        """Let user pick which file formats to index"""
        print("\n📁 SELECT FILE FORMATS TO INDEX:")
        formats = ['.txt', '.pdf', '.json', '.csv', '.xlsx']
        self.selected_formats = []
        
        for fmt in formats:
            choice = input(f"  Include {fmt} files? (y/n): ").lower()
            if choice == 'y':
                self.selected_formats.append(fmt)
        
        print(f"\n✅ Selected: {self.selected_formats}")
        return self.selected_formats
    
    def build_index(self, folder_path="data"):
        """Build the inverted index from all files in folder"""
        print(f"\n📂 Indexing folder: {folder_path}")
        
        # Reset everything
        self.inverted_index = {}
        self.documents = {}
        self.doc_counter = 0
        
        if not os.path.exists(folder_path):
            print(f"❌ Folder '{folder_path}' not found!")
            return False
        
        # Walk through all files
        files_indexed = 0
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                if ext in self.selected_formats:
                    print(f"  📄 Indexing: {file}")
                    success = self.index_file(file_path, ext)
                    if success:
                        files_indexed += 1
        
        # Save index to disk
        self.save_index()
        print(f"\n✅ Indexed {files_indexed} files!")
        self.print_summary()
        return True
    
    def index_file(self, file_path, ext):
        """Extract text and add to index"""
        try:
            # Get content using appropriate handler
            handler = HANDLERS.get(ext)
            if not handler:
                return False
            
            content = handler(file_path)
            if not content or len(content.strip()) < 10:
                print(f"    ⚠️ No content extracted")
                return False
            
            # Get file info
            stat = os.stat(file_path)
            mod_date = datetime.fromtimestamp(stat.st_mtime)
            file_type = ext[1:].upper()  # Remove dot, make uppercase
            
            # Store document
            doc_id = self.doc_counter
            self.documents[doc_id] = {
                'path': file_path,
                'filename': os.path.basename(file_path),
                'type': file_type,
                'date': mod_date.strftime("%Y-%m-%d %H:%M:%S"),
                'timestamp': stat.st_mtime,
                'content': content
            }
            
            # Tokenize and add to inverted index
            self.tokenize_and_index(doc_id, content)
            
            self.doc_counter += 1
            return True
            
        except Exception as e:
            print(f"    ⚠️ Error: {e}")
            return False
    
    def tokenize_and_index(self, doc_id, text):
        """Enhanced tokenization with better filtering for meaningful content"""
        # Normalize text to lowercase
        text = text.lower()
        
        # Find words: letters, apostrophes, minimum 3 characters
        # This excludes pure numbers and short words
        words = re.findall(r"\b[a-z']{3,}\b", text)
        
        for position, word in enumerate(words):
            # Skip stop words
            if word in STOP_WORDS:
                continue
            
            # Skip pure numbers (but keep years)
            if word.isdigit():
                num = int(word)
                # Keep only reasonable years (1900-2026) and skip other numbers
                if num < 1900 or num > 2026:
                    continue
            
            # Skip words that are just apostrophes or common noise
            if word in ["''", "`", "'s"]:
                continue
            
            # Initialize if new word
            if word not in self.inverted_index:
                self.inverted_index[word] = {}
            
            # Add position for this document
            if doc_id not in self.inverted_index[word]:
                self.inverted_index[word][doc_id] = []
            
            self.inverted_index[word][doc_id].append(position)
    
    def save_index(self):
        """Save index to JSON file"""
        os.makedirs("index_data", exist_ok=True)
        
        # Convert for JSON serialization
        data = {
            'inverted_index': self.inverted_index,
            'documents': self.documents,
            'doc_counter': self.doc_counter
        }
        
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, default=str, ensure_ascii=False)
    
    def load_index(self):
        """Load index from disk"""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.inverted_index = data['inverted_index']
                    self.documents = data['documents']
                    self.doc_counter = data['doc_counter']
                return True
            except Exception as e:
                print(f"⚠️ Error loading index: {e}")
                return False
        return False
    
    def print_summary(self):
        """Show index summary stats"""
        print("\n📊 INDEX SUMMARY:")
        print(f"   Total documents: {self.doc_counter}")
        
        # Breakdown by type
        type_counts = {}
        for doc in self.documents.values():
            t = doc['type']
            type_counts[t] = type_counts.get(t, 0) + 1
        
        print("   By file type:")
        for t, count in sorted(type_counts.items()):
            print(f"      {t}: {count}")
        
        # Top 10 terms (by document frequency)
        if self.inverted_index:
            terms = sorted(self.inverted_index.items(), 
                           key=lambda x: len(x[1]), reverse=True)[:10]
            print("   Top 10 terms by document frequency:")
            for word, docs in terms:
                print(f"      '{word}': {len(docs)} docs")
        else:
            print("   No terms indexed yet")
        
        # Vocabulary size
        print(f"   Unique terms in index: {len(self.inverted_index)}")
    
    def get_document_count(self):
        """Return number of indexed documents"""
        return self.doc_counter
    
    def get_document(self, doc_id):
        """Return document by ID"""
        return self.documents.get(doc_id)
    
    def get_all_documents(self):
        """Return all documents"""
        return self.documents
    
    def get_term_posting(self, term):
        """Get posting list for a term"""
        return self.inverted_index.get(term.lower(), {})
    
    def get_all_terms(self):
        """Return all terms in index"""
        return list(self.inverted_index.keys())
    