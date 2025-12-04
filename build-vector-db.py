# Refer from https://learn.deeplearning.ai/courses/advanced-retrieval-for-ai/lesson/ukzj4/overview-of-embeddings-based-retrieval
import os
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv
from helper_utils import word_wrap
load_dotenv()


def ingest_pdf(pdf_path, db_path="vectorstore", collection_name="faq"):
    # 1. Document Loading
    # reader = PdfReader("microsoft_annual_report_2022.pdf")
    reader = PdfReader(pdf_path)
    # pdf_texts = [p.extract_text().strip() for p in reader.pages]
    # pdf_texts = [text for text in pdf_texts if text]

    pdf_texts = []
    page_numbers = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pdf_texts.append(text.strip())
            page_numbers.append(i + 1)  # store actual page number

    print(word_wrap(pdf_texts[0]))

    # 2. Splitting and chunking
    character_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=300,
        chunk_overlap=20
    )
    character_split_texts = character_splitter.split_text('\n\n'.join(pdf_texts))

    token_splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=20, tokens_per_chunk=256)

    token_split_texts = []
    for text in character_split_texts:
        token_split_texts += token_splitter.split_text(text)

    print(word_wrap(token_split_texts[0]))
    print(f"\nTotal chunks: {len(token_split_texts)}")

    #3. Vector Database
    embedding_function = SentenceTransformerEmbeddingFunction()
    print(embedding_function([token_split_texts[0]]))

    chroma_client = chromadb.PersistentClient(path=db_path)
    chroma_collection = chroma_client.create_collection(collection_name,
                                                        embedding_function=embedding_function)

    ids = [str(i) for i in range(len(token_split_texts))]

    # Metadata: attach filename + chunk index
    metadatas = [
        {
            "source":pdf_path,
            "chunk_index": i,
        }
        for i in range(len(token_split_texts))
    ]
    chroma_collection.add(ids=ids, documents=token_split_texts, metadatas=metadatas)
    chroma_collection.count()
    print(chroma_collection.count())


    print(f"Ingested {len(token_split_texts)} chunks into {collection_name}")

if __name__ == "__main__":
    ingest_pdf("docs/sq_faq.pdf")




