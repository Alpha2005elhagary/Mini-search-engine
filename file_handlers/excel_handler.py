# excel_handler.py - Excel to text
import pandas as pd

def read_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        text = df.to_string()
        return text
    except:
        return ""









# # file_handlers/excel_handler.py - Improved
# import pandas as pd

# def read_excel(file_path):
#     try:
#         excel_file = pd.ExcelFile(file_path)
#         all_text = []
        
#         for sheet_name in excel_file.sheet_names:
#             df = pd.read_excel(file_path, sheet_name=sheet_name)
            
#             # Skip ID and numeric-only columns
#             skip_columns = ['transaction_id', 'customer_id', 'product_id', 
#                            'employee_id', 'ticket_id', 'feedback_id']
            
#             for col in df.columns:
#                 if col.lower() in skip_columns:
#                     continue
                
#                 # Convert column to string, but filter out numbers
#                 col_values = df[col].astype(str)
                
#                 # Filter: keep only values with length > 2 and not pure numbers
#                 filtered = [str(v) for v in col_values if len(str(v)) > 2 and not str(v).isdigit()]
#                 if filtered:
#                     all_text.append(" ".join(filtered))
        
#         return " ".join(all_text)
#     except Exception as e:
#         print(f"Excel error: {e}")
#         return ""




# # excel_handler.py - Optimized for financial/sales data
# import pandas as pd
# import re

# def read_excel(file_path):
#     try:
#         excel_file = pd.ExcelFile(file_path)
#         all_text = []
        
#         for sheet_name in excel_file.sheet_names:
#             df = pd.read_excel(file_path, sheet_name=sheet_name)
            
#             # Extract meaningful business data
#             sheet_text = extract_sheet_meaningful_content(df, sheet_name)
#             if sheet_text:
#                 all_text.append(sheet_text)
        
#         return ' '.join(all_text)
    
#     except Exception as e:
#         print(f"Excel error: {e}")
#         return ""

# def extract_sheet_meaningful_content(df, sheet_name):
#     """Extract only meaningful business information"""
#     text_parts = []
    
#     # Add sheet context
#     text_parts.append(f"Sheet: {sheet_name}")
    
#     # Define columns that contain meaningful text (not IDs)
#     text_columns = ['Segment', 'Country', 'Product', 'Discount Band', 
#                     'Month Name', 'Product Category', 'Customer City']
    
#     numeric_meaningful = ['Profit', 'Sales', 'Revenue']
    
#     for col in df.columns:
#         col_lower = str(col).lower()
        
#         # Skip ID columns
#         if any(id_word in col_lower for id_word in ['id', 'code', 'number']):
#             continue
        
#         # Handle text columns
#         if col in text_columns or col_lower in ['segment', 'country', 'product', 'category']:
#             unique_values = df[col].dropna().unique()
#             # Take top 10 most common values to avoid repetition
#             for val in list(unique_values)[:10]:
#                 if pd.notna(val) and len(str(val)) > 2:
#                     text_parts.append(str(val))
        
#         # Handle meaningful numeric columns (add context)
#         if col in numeric_meaningful or 'profit' in col_lower or 'sale' in col_lower:
#             # Add summary statistics instead of all rows
#             positive_profit = df[df[col] > 0][col].count() if col in df.columns else 0
#             if positive_profit > 0:
#                 text_parts.append(f"{positive_profit} records with {col}")
    
#     return ' '.join(text_parts)