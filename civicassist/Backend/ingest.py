from pathlib import Path

import chromadb
import fitz
from sentence_transformers import SentenceTransformer


# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
VECTOR_DB_DIR = BASE_DIR / "vector_db"

LEGAL_DIR = DATA_DIR / "legal"
SCHEMES_DIR = DATA_DIR / "schemes"


# -----------------------------
# Settings
# -----------------------------
COLLECTION_NAME = "civicassist"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"


# -----------------------------
# Chunking
# -----------------------------
def split_text(text: str):
    text = text.strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


# -----------------------------
# Read PDF
# -----------------------------
def read_pdf(pdf_path: Path):
    doc = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()

        if text:
            pages.append({
                "page": page_number,
                "text": text
            })

    doc.close()

    return pages


# -----------------------------
# Main ingestion
# -----------------------------
def main():

    print("Loading embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print("Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))

    # Recreate collection
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Existing collection deleted.")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME
    )

    documents = []
    metadatas = []
    ids = []

    total_chunks = 0

    # --------------------------------
    # Process legal + schemes folders
    # --------------------------------
    folders = [
        ("legal", LEGAL_DIR),
        ("scheme", SCHEMES_DIR),
    ]

    for document_type, folder in folders:

        if not folder.exists():
            print(f"Folder not found: {folder}")
            continue

        pdf_files = list(folder.glob("*.pdf"))

        print(
            f"\nProcessing {document_type}: "
            f"{len(pdf_files)} PDF files"
        )

        for pdf_path in pdf_files:

            print(f"  Reading: {pdf_path.name}")

            try:
                pages = read_pdf(pdf_path)

                file_chunk_number = 0

                for page_data in pages:

                    page_number = page_data["page"]
                    text = page_data["text"]

                    chunks = split_text(text)

                    for chunk in chunks:

                        chunk_id = (
                            f"{document_type}_"
                            f"{pdf_path.stem}_"
                            f"p{page_number}_"
                            f"c{file_chunk_number}"
                        )

                        documents.append(chunk)

                        metadatas.append({
                            "document_type": document_type,
                            "source": pdf_path.name,
                            "file_path": str(pdf_path),
                            "page": page_number,
                            "chunk": file_chunk_number,
                        })

                        ids.append(chunk_id)

                        file_chunk_number += 1
                        total_chunks += 1

                print(
                    f"    Added chunks from {pdf_path.name}"
                )

            except Exception as e:
                print(
                    f"    ERROR processing "
                    f"{pdf_path.name}: {e}"
                )

    # --------------------------------
    # Generate embeddings
    # --------------------------------
    print(
        f"\nGenerating embeddings for "
        f"{len(documents)} chunks..."
    )

    embeddings = model.encode(
        documents,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    # --------------------------------
    # Store in ChromaDB
    # --------------------------------
    print("Storing chunks in ChromaDB...")

    BATCH_SIZE = 100

    for start in range(0, len(documents), BATCH_SIZE):

        end = start + BATCH_SIZE

        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            embeddings=embeddings[start:end].tolist(),
            metadatas=metadatas[start:end],
        )

        print(
            f"Stored {min(end, len(documents))}/"
            f"{len(documents)} chunks"
        )

    print("\n==============================")
    print("INGESTION COMPLETE")
    print("==============================")
    print(f"Legal folder   : {LEGAL_DIR}")
    print(f"Schemes folder : {SCHEMES_DIR}")
    print(f"Total chunks   : {collection.count()}")
    print(f"ChromaDB path  : {VECTOR_DB_DIR}")


if __name__ == "__main__":
    main()