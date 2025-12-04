# retriever.py
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb

def retrieve(query, db_path="vectorstore", collection_name="faq", k=5):
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(collection_name)
    # results = collection.query(query_texts=[query], n_results=k)
    # return results['documents'][0]

    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "embeddings"]  # <-- include metadata
    )

    # Each of these is a list of lists (because query_texts could have multiple queries)
    docs = results['documents'][0]
    metadatas = results['metadatas'][0]
    embeddings = results['embeddings'] [0]

    # Return list of (document, metadata) tuples
    return list(zip(docs, metadatas)) # same as the return from "results"
    # return results


def get_sources_for_query(query, k=5):
    """
    Fetch the top-k relevant chunks from your vector database for this query.
    Returns a list of strings.
    """
    sources = retrieve(query, k=k)
    return sources