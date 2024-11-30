import pickle
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer

# File path to save the vectorizer
VECTORIZER_PATH = "tfidf_vectorizer.pkl"

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  
db = client["hw4"] 
documents_collection = db["documents"]  
inverted_index_collection = db["inverted_index"]  

# Read documents from MongoDB
documents = list(documents_collection.find())
texts = [doc['text'] for doc in documents]  

# TF-IDF Calculation 
vectorizer = TfidfVectorizer(ngram_range=(1, 3))  
tfidf_matrix = vectorizer.fit_transform(texts)

# Save the vectorizer for later use
with open(VECTORIZER_PATH, "wb") as file:
    pickle.dump(vectorizer, file)

vocabulary = vectorizer.vocabulary_  
feature_names = vectorizer.get_feature_names_out()

# Create the inverted index
inverted_index = {}
for term, pos in vocabulary.items():
    docs_list = []
    for doc_id, doc_vector in enumerate(tfidf_matrix.toarray()):
        tfidf_value = doc_vector[pos]
        if tfidf_value > 0:  
            docs_list.append({"doc_id": documents[doc_id]["_id"], "tfidf": tfidf_value})
    inverted_index[term] = {"pos": pos, "docs": docs_list}

# Prepare data for MongoDB insertion
mongo_data = [
    {"_id": idx, "term": term, "pos": data["pos"], "docs": data["docs"]}
    for idx, (term, data) in enumerate(inverted_index.items())
]

# Insert the inverted index into MongoDB
inverted_index_collection.delete_many({})  # Clear any existing data
inverted_index_collection.insert_many(mongo_data)

# Add TF-IDF matrix as embeddings to documents
for doc_id, doc_vector in enumerate(tfidf_matrix.toarray()):
    documents_collection.update_one(
        {"_id": documents[doc_id]["_id"]}, 
        {"$set": {"embedding": doc_vector.tolist()}}
    )

# Print confirmation
print(f"Inserted {len(mongo_data)} terms into the inverted index collection.")
print(f"TF-IDF embeddings added to {len(documents)} documents.")
print(f"Vectorizer saved to {VECTORIZER_PATH}.")
