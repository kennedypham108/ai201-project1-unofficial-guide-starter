from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from document_pipeline import load_documents, chunk_documents


CHROMA_PATH = Path("chroma_db")
COLLECTION_NAME = "ucsd_dining_reviews"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 4


def create_collection():
    """
    Create a persistent ChromaDB collection.

    The collection is deleted and rebuilt each time this script runs
    so repeated testing does not create duplicate records.
    """
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))

    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    return collection


def build_vector_store():
    """
    Load the cleaned chunks, generate embeddings, and store each chunk
    in ChromaDB with its metadata.
    """
    documents = load_documents()
    chunks = chunk_documents(documents)

    model = SentenceTransformer(EMBEDDING_MODEL)
    collection = create_collection()

    chunk_texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(chunk_texts).tolist()

    collection.add(
        ids=[chunk["id"] for chunk in chunks],
        documents=chunk_texts,
        embeddings=embeddings,
        metadatas=[chunk["metadata"] for chunk in chunks],
    )

    print(f"Loaded chunks: {len(chunks)}")
    print(f"Stored embeddings: {collection.count()}")
    print(f"Embedding model: {EMBEDDING_MODEL}")
    print("=" * 80)

    return collection, model


def retrieve_chunks(
    query: str,
    collection,
    model,
    top_k: int = TOP_K,
) -> list[dict]:
    """
    Embed a user question and retrieve the most relevant chunks.

    ChromaDB returns smaller cosine distances for more similar chunks.
    """
    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved_chunks = []

    for index in range(len(results["ids"][0])):
        retrieved_chunks.append(
            {
                "id": results["ids"][0][index],
                "text": results["documents"][0][index],
                "metadata": results["metadatas"][0][index],
                "distance": results["distances"][0][index],
            }
        )

    return retrieved_chunks


def print_retrieval_results(query: str, results: list[dict]) -> None:
    """
    Print retrieval results so they can be manually checked before
    adding an LLM generation step.
    """
    print(f"QUERY: {query}")
    print("-" * 80)

    for rank, result in enumerate(results, start=1):
        print(f"Rank: {rank}")
        print(f"Distance: {result['distance']:.4f}")
        print(f"Source: {result['metadata']['source']}")
        print("Text:")
        print(result["text"])
        print("-" * 80)

    print()


def run_test_queries(collection, model) -> None:
    """
    Run several questions from the evaluation plan.
    """
    test_queries = [
        "Is UCSD's dining plan unlimited or à la carte?",
        "Where can students use Dining Dollars and how is Triton Cash different?",
        "Why should students save Triton Cash for academic breaks?",
        "Where can I get deep-dish pizza with leftover Dining Dollars?",
        "What ingredients can students buy from campus markets for cooking in a dorm?",
    ]

    for query in test_queries:
        results = retrieve_chunks(query, collection, model)
        print_retrieval_results(query, results)


if __name__ == "__main__":
    vector_store, embedding_model = build_vector_store()
    run_test_queries(vector_store, embedding_model)