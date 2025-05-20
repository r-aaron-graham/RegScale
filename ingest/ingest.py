import tempfile
from langchain.text_splitter import RecursiveCharacterTextSplitter

async def ingest_document(file, config):
    # Save file to disk
    suffix = "." + file.filename.split(".")[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        path = tmp.name

    # Simple text extraction (add PDF/docx logic as needed)
    text = content.decode("utf-8", errors="ignore")
    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=config['chunk_size'], chunk_overlap=config['overlap'])
    chunks = splitter.split_text(text)
    # TODO: Add metadata extraction and index (see services.indexing)
    return chunks
