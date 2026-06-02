def chunk_text(
    pages,
    chunk_size=1200,
    overlap=200
):
    chunks = []

    current_text = ""
    page_start = None

    for page_number, page_text in enumerate(
        pages,
        start=1
    ):
        if not page_text:
            continue

        if page_start is None:
            page_start = page_number

        page_text = page_text.strip()

        if not current_text:
            current_text = page_text
        else:
            current_text = (
                current_text
                + "\n\n"
                + page_text
            )

        while len(current_text) >= chunk_size:
            chunk = current_text[:chunk_size].strip()

            chunks.append(
                {
                    "page_start": page_start,
                    "page_end": page_number,
                    "text": chunk
                }
            )

            if overlap:
                current_text = current_text[
                    chunk_size - overlap:
                ]
            else:
                current_text = current_text[
                    chunk_size:
                ]

            page_start = page_number

    if current_text.strip():
        chunks.append(
            {
                "page_start": page_start or 1,
                "page_end": len(pages),
                "text": current_text.strip()
            }
        )

    return chunks
