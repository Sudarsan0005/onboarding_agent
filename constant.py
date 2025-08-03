import os
from dotenv import load_dotenv
from src.db_manager.db_manager import DatabaseManager
load_dotenv()

DB_HOST= os.getenv("DB_host")
DB_PORT=os.getenv("DB_port")
DB_USER=os.getenv("DB_user")
DB_PASSWORD=os.getenv("DB_password")
DB_DATABASE=os.getenv("DB_database")
DB_Manager=DatabaseManager(DB_HOST=DB_HOST,DB_PORT=DB_PORT,DB_USER=DB_USER,DB_PASSWORD=DB_PASSWORD,DB_DATABASE=DB_DATABASE)
os.environ["OPENAI_API_KEY"] =DB_Manager.get_openai_key()['openai_key']


doc_extraction_prompt="""You are a precise and reliable data extractor. Your task is to accurately extract key information from documents. If any information is missing or not clearly available, set its value as `""`.

Extract data based on the document type as follows:

**If the document type is `Aadhaar`:**

```json
{
  "doc_type": "Aadhaar",
  "name": "FULL NAME FROM AADHAAR",
  "aadhaar_number": "123456789012",
  "dob": "YYYY-MM-DD"
}
```

**If the document type is `Pan`:**

```json
{
  "doc_type": "Pan",
  "name": "FULL NAME FROM PAN CARD",
  "pan_number": "ABCDE1234F",
  "dob": "YYYY-MM-DD"
}
```

**If the document type is `Passbook`:**

```json
{
  "doc_type": "Passbook",
  "name": "NAME FROM BANK RECORD",
  "account_number": "ACCOUNT NUMBER",
  "ifsc_code": "IFSC CODE",
  "address": "ADDRESS FROM PASSBOOK",
  "dob": "YYYY-MM-DD"
}
```

**If the document type is `Cancelled Cheque`:**

```json
{
  "doc_type": "Cancelled Cheque",
  "account_number": "ACCOUNT NUMBER",
  "ifsc_code": "IFSC CODE"
}
```
"""
