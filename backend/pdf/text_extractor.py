def extract_text_by_page(pdf_path):
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ImportError(
            "pypdf is required to extract PDF text. "
            "Install it with: pip install pypdf"
        ) from exc

    reader = PdfReader(
        str(pdf_path)
    )

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""

        pages.append(
            text.strip()
        )

    return pages
