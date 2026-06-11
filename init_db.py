import sys
sys.path.insert(0, '.')
from backend.database.db import initialize_database
from backend.database.pdf_db import initialize_pdf_database
initialize_database()
initialize_pdf_database()
print('[OK] Database ready.')
