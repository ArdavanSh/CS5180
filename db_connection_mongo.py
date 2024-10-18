from pymongo import MongoClient
import datetime
from collections import Counter, defaultdict
import re
import string


def connectDataBase():

    # Creating a database connection object using pymongo

    DB_NAME = "CPP"
    DB_HOST = "localhost"
    DB_PORT = 27017

    try:

        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]

        return db

    except:
        print("Database not connected successfully")



def createDocument(documents, docId, docText, docTitle, docDate, docCat):

    txt = re.sub(f"[{re.escape(string.punctuation)}]", "", docText.lower()).split()
    wordsCounter = Counter(txt)

    # Convert Counter to a list of dictionaries
    terms_list = [{"term": word, "count": count, "num_chars":len(word)} for word, count in wordsCounter.items()]

    # Value to be inserted
    doc = {
        "_id": docId,
        "title": docTitle,
        "text": docText,
        "num_chars": sum(item["num_chars"] * item["count"] for item in terms_list),
        "date": datetime.datetime.strptime(docDate, "%Y-%m-%d"),
        "category": docCat,
        "terms": terms_list  
    }

    documents.insert_one(doc)


def updateDocument(documents, docId, docText, docTitle, docDate, docCat):

    txt = re.sub(f"[{re.escape(string.punctuation)}]", "", docText.lower()).split()
    wordsCounter = Counter(txt)
    terms_list = [{"term": word, "count": count, "num_chars":len(word)} for word, count in wordsCounter.items()]

    # documents fields to be updated
    doc = {"$set": {"title": docTitle, "text": docText, "num_chars": sum(item["num_chars"] * item["count"] for item in terms_list),
                    "date":datetime.datetime.strptime(docDate, "%Y-%m-%d"), "category":docCat, "terms":terms_list}}

    # Updating the dpcument
    documents.update_one({"_id": docId}, doc)


def deleteDocument(documents, docId):

    # delete the  document
    documents.delete_one({"_id": docId})


def getIndex(documents):

    invertedIndex = defaultdict(list)

    docs = list(documents.find())

    for doc in docs:
        for term in doc["terms"]:  
            key = term["term"]  
            val = term["count"]  
            invertedIndex[key].append((doc["title"], val))  

    sorted_data = [(key, sorted(value)) for key, value in sorted(invertedIndex.items())]
    
    return sorted_data





