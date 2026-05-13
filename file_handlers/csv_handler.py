# csv_handler.py - CSV to text
import csv

def read_csv(file_path):
    try:
        text = ""
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                text += " ".join(row) + " "
        return text
    except:
        return ""






# # file_handlers/csv_handler.py - Improved
# import csv

# def read_csv(file_path):
#     try:
#         text = []
#         with open(file_path, 'r', encoding='utf-8') as f:
#             reader = csv.reader(f)
#             headers = next(reader)  # Get headers
            
#             # Add headers as searchable context
#             text.append(" ".join(headers))
            
#             for row in reader:
#                 for i, cell in enumerate(row):
#                     # Skip ID columns and numbers
#                     if headers[i].lower() in ['employee_id', 'id', 'email']:
#                         continue
#                     # Only add meaningful text (not just numbers)
#                     if len(cell) > 2 and not cell.isdigit():
#                         text.append(cell)
        
#         return " ".join(text)
#     except Exception as e:
#         print(f"CSV error: {e}")
#         return ""









# # csv_handler.py - Optimized for employee data
# import csv

# def read_csv(file_path):
#     try:
#         text_parts = []
        
#         with open(file_path, 'r', encoding='utf-8') as f:
#             reader = csv.DictReader(f)
            
#             for row in reader:
#                 # Extract meaningful employee info
#                 employee_info = []
                
#                 # Name fields
#                 if row.get('first_name'):
#                     employee_info.append(row['first_name'])
#                 if row.get('last_name'):
#                     employee_info.append(row['last_name'])
                
#                 # Department and position
#                 if row.get('department'):
#                     employee_info.append(row['department'])
#                 if row.get('position'):
#                     employee_info.append(row['position'])
                
#                 # Location and work info
#                 if row.get('location'):
#                     employee_info.append(row['location'])
#                 if row.get('remote_worker'):
#                     employee_info.append(row['remote_worker'])
                
#                 # Education
#                 if row.get('education'):
#                     employee_info.append(row['education'])
                
#                 # Manager (for searchability)
#                 if row.get('manager_name'):
#                     employee_info.append(f"reports to {row['manager_name']}")
                
#                 if employee_info:
#                     text_parts.append(' '.join(employee_info))
        
#         return ' '.join(text_parts)
    
#     except Exception as e:
#         print(f"CSV error: {e}")
#         return ""