# __init__.py
from .txt_handler import read_txt
from .pdf_handler import read_pdf
from .json_handler import read_json
from .csv_handler import read_csv
from .excel_handler import read_excel

HANDLERS = {
    '.txt': read_txt,
    '.pdf': read_pdf,
    '.json': read_json,
    '.csv': read_csv,
    '.xlsx': read_excel,
}