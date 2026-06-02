import sys
from pprint import pprint
from pathlib import Path

from backend.pdf.pdf_ingestor import (
    ingest_pdf
)

from backend.retrieval.pdf_retriever import (
    retrieve_pdf_context
)


if len(sys.argv) < 2:
    print(
        "Usage: python test_real_pdf.py <path-to-pdf>"
    )
    sys.exit(1)

pdf_path = Path(
    sys.argv[1]
)

result = ingest_pdf(
    pdf_path
)

print("INGEST RESULT:")
pprint(
    result
)

chunks = retrieve_pdf_context(
    "deadlock"
)

print("\nRETRIEVED CHUNKS:")
pprint(
    chunks
)
