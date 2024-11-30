import numpy as np
from pymongo import MongoClient
import pickle


# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  
db = client["hw4"]  
documents_collection = db["documents"]  
inverted_index_collection = db["inverted_index"]  

def rank_documents(query, vectorizer_path, inverted_index_collection):

    # Load the vectorizer
    with open(vectorizer_path, "rb") as file:
        vectorizer = pickle.load(file)

    # Tokenize and transform the query using the vectorizer
    query_vector = vectorizer.transform([query]).toarray()[0]
    query_terms = vectorizer.get_feature_names_out()

    # Get non-zero terms in the query
    query_non_zero_indices = np.nonzero(query_vector)[0]
    query_terms_non_zero = [(query_terms[idx], query_vector[idx]) for idx in query_non_zero_indices]

    # Map query terms to their positions and weights
    matching_docs = {}
    for term, weight in query_terms_non_zero:
        term_data = inverted_index_collection.find_one({"term": term})
        if term_data:
            for doc_info in term_data["docs"]:
                doc_id = doc_info["doc_id"]
                doc_tfidf = doc_info["tfidf"]
                if doc_id not in matching_docs:
                    matching_docs[doc_id] = 0
                matching_docs[doc_id] += weight * doc_tfidf  

    # Fetch embeddings, calculate norms
    document_details = {}
    for doc_id in matching_docs.keys():
        doc = documents_collection.find_one({"_id": doc_id})
        if doc and "embedding" in doc:
            embedding = np.array(doc["embedding"])
            norm = np.linalg.norm(embedding)
            document_details[doc_id] = {
                "text": doc.get("text", ""),
                "norm": norm,
            }
        else:
            document_details[doc_id] = {
                "text": doc.get("text", "") if doc else "",
                "norm": 0
            }

    # Calculate final scores
    ranked_docs = [
        {
            "doc_id": doc_id,
            "score": score / document_details[doc_id]["norm"],
            "text": document_details[doc_id]["text"],
        }
        for doc_id, score in matching_docs.items()
        if document_details[doc_id]["norm"] > 0
    ]

    # Sort documents by score in descending order
    ranked_docs = sorted(ranked_docs, key=lambda x: x["score"], reverse=True)
    return ranked_docs


VECTORIZER_PATH = "tfidf_vectorizer.pkl"

queries = ["nausea and dizziness", "effects", "nausea was reported", "dizziness", "the medication"]

for query in queries:
    ranked_docs = rank_documents(query, VECTORIZER_PATH, inverted_index_collection)

    print("Ranked Documents for query: ", query)
    for doc in ranked_docs:
        print(f"Doc ID: {doc['doc_id']}, Content: {doc["text"]} Score: {doc['score']:.4f}")
    print("\n")

