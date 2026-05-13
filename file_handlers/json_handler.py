# json_handler.py - Flatten JSON to text
import json

def read_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Flatten all string values into one document
        return flatten_json(data)
    except:
        return ""

def flatten_json(obj, result=""):
    if isinstance(obj, dict):
        for value in obj.values():
            result = flatten_json(value, result)
    elif isinstance(obj, list):
        for item in obj:
            result = flatten_json(item, result)
    elif isinstance(obj, str):
        result += " " + obj
    return result







# # file_handlers/json_handler.py - Improved version
# import json

# def read_json(file_path):
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#         return extract_meaningful_text(data)
#     except Exception as e:
#         print(f"JSON error: {e}")
#         return ""

# def extract_meaningful_text(obj, result=""):
#     """Extract only meaningful text, skip IDs, numbers, short strings"""
    
#     # Skip if None
#     if obj is None:
#         return result
    
#     # Skip numbers and small numbers
#     if isinstance(obj, (int, float)):
#         # Skip IDs and small numbers (likely not meaningful)
#         if obj > 9999 or (isinstance(obj, float) and obj > 9999):
#             result += " " + str(obj)
#         return result
    
#     # Process strings
#     if isinstance(obj, str):
#         # Only add if it's meaningful (not just a single character or number)
#         if len(obj) > 2 and not obj.isdigit():
#             result += " " + obj
#         return result
    
#     # Process dictionaries
#     if isinstance(obj, dict):
#         # Skip metadata fields that contain IDs
#         skip_keys = {'id', 'isbn', 'employee_id', 'transaction_id', 
#                      'ticket_id', 'product_id', 'customer_id'}
        
#         for key, value in obj.items():
#             if key in skip_keys:
#                 continue  # Skip ID fields
#             if key == 'reviews':
#                 result = extract_meaningful_text(value, result)
#             else:
#                 result = extract_meaningful_text(value, result)
#         return result
    
#     # Process lists
#     if isinstance(obj, list):
#         for item in obj:
#             result = extract_meaningful_text(item, result)
#         return result
    
#     # Process booleans
#     if isinstance(obj, bool):
#         return result
    
#     return result






# # json_handler.py - Optimized for nested book data
# import json
# import re

# def read_json(file_path):
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
        
#         text_parts = []
        
#         # Extract metadata
#         if 'metadata' in data:
#             text_parts.append(data['metadata'].get('collection_name', ''))
        
#         # Extract books data
#         if 'books' in data:
#             for book in data['books']:
#                 text_parts.append(extract_book_content(book))
        
#         # Extract statistics (meaningful ones only)
#         if 'statistics' in data:
#             stats = data['statistics']
#             for genre, count in stats.get('genre_distribution', {}).items():
#                 text_parts.append(f"{genre} genre has {count} books")
        
#         return ' '.join(text_parts)
    
#     except Exception as e:
#         print(f"JSON error: {e}")
#         return ""

# def extract_book_content(book):
#     """Extract meaningful text from a single book entry"""
#     parts = []
    
#     # Core fields (skip IDs)
#     if 'title' in book:
#         parts.append(book['title'])
#     if 'author' in book:
#         parts.append(book['author'])
#     if 'publisher' in book:
#         parts.append(book['publisher'])
#     if 'genre' in book:
#         parts.append(book['genre'])
#     if 'description' in book:
#         parts.append(book['description'])
    
#     # Keywords
#     if 'keywords' in book and isinstance(book['keywords'], list):
#         parts.extend(book['keywords'])
    
#     # Reviews (extract comments only)
#     if 'reviews' in book and isinstance(book['reviews'], list):
#         for review in book['reviews']:
#             if 'comment' in review and review['comment']:
#                 parts.append(review['comment'])
    
#     return ' '.join(parts)