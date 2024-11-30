from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  
db = client["hw4"]  
collection = db["documents"]  

# Documents
documents = [
    {"_id": 1, "text": "After the medication, headache and nausea were reported by the patient."},
    {"_id": 2, "text": "The patient reported nausea and dizziness caused by the medication."},
    {"_id": 3, "text": "Headache and dizziness are common effects of this medication."},
    {"_id": 4, "text": "The medication caused a headache and nausea, but no dizziness was reported."},
]

# Insert documents into the collection
collection.delete_many({})  
result = collection.insert_many(documents)

print("Inserted document IDs:", [doc["_id"] for doc in documents])