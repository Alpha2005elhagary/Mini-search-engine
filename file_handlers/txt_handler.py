# txt_handler.py - Simple text file reader
def read_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except:
        return ""







# # txt_handler.py - Optimized for technical documentation
# import re

# def read_txt(file_path):
#     try:
#         with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
#             content = f.read()
        
#         # Clean and normalize
#         content = re.sub(r'={3,}', ' ', content)  # Remove separator lines
#         content = re.sub(r'-{3,}', ' ', content)  # Remove dash lines
#         content = re.sub(r'CHAPTER \d+:', ' ', content)  # Remove chapter markers
#         content = re.sub(r'[^\w\s]', ' ', content)  # Remove punctuation
        
#         # Normalize whitespace
#         content = ' '.join(content.split())
        
#         return content
#     except Exception as e:
#         print(f"TXT error: {e}")
#         return ""