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

def createUser(col, id, name, email):

    # Value to be inserted
    user = {"_id": id,
            "name": name,
            "email": email,
            }

    # Insert the document
    col.insert_one(user)

def updateUser(col, id, name, email):

    # User fields to be updated
    user = {"$set": {"name": name, "email": email} }

    # Updating the user
    col.update_one({"_id": id}, user)

def deleteUser(col, id):

    # Delete the document from the database
    col.delete_one({"_id": id})

def getUser(col, id):

    user = col.find_one({"_id":id})

    if user:
        return str(user['_id']) + " | " + user['name'] + " | " + user['email']
    else:
        return []

def createComment(col, id_user, dateTime, comment):

    # Comments to be included
    comments = {"$push": {"comments": {
                                       "datetime": datetime.datetime.strptime(dateTime, "%m/%d/%Y %H:%M:%S"),
                                       "comment": comment
                                       } }}

    # Updating the user document
    col.update_one({"_id": id_user}, comments)

def updateComment(col, id_user, dateTime, new_comment):

    # User fields to be updated
    comment = {"$set": {"comments.$.comment": new_comment} }

    # Updating the user
    col.update_one({"_id": id_user, "comments.datetime": datetime.datetime.strptime(dateTime, "%m/%d/%Y %H:%M:%S")}, comment)

def deleteComment(col, id_user, dateTime):

    # Comments to be delete
    comments = {"$pull": {"comments": {"datetime": datetime.datetime.strptime(dateTime, "%m/%d/%Y %H:%M:%S")} }}

    # Updating the user document
    col.update_one({"_id": id_user}, comments)

def getChat(col):

    # creating a document for each message
    pipeline = [
                 {"$unwind": { "path": "$comments" }},
                 {"$sort": {"comments.datetime": 1}}
               ]

    comments = col.aggregate(pipeline)

    chat = ""

    for com in comments:
        chat += com['name'] + " | " + com['comments']['comment'] + " | " + str(com['comments']['datetime']) + "\n"

    return chat

# _______________________________________________________________________________________


def createDocument(documents, docId, docText, docTitle, docDate, docCat):

    txt = re.sub(f"[{re.escape(string.punctuation)}]", "", docText.lower()).split()
    wordsCounter = Counter(txt)

    # Convert Counter to a list of dictionaries
    terms_list = [{"term": word, "count": count} for word, count in wordsCounter.items()]

    # Value to be inserted
    doc = {
        "_id": docId,
        "text": docText,
        "title": docTitle,
        "date": datetime.datetime.strptime(docDate, "%Y-%m-%d"),
        "category": docCat,
        "terms": terms_list  
    }

    documents.insert_one(doc)


def updateDocument(documents, docId, docText, docTitle, docDate, docCat):

    txt = re.sub(f"[{re.escape(string.punctuation)}]", "", docText.lower()).split()
    wordsCounter = Counter(txt)
    terms_list = [{"term": word, "count": count} for word, count in wordsCounter.items()]

    # documents fields to be updated
    doc = {"$set": {"text": docText, "title": docTitle, "date":datetime.datetime.strptime(docDate, "%Y-%m-%d"), "category":docCat, "terms":terms_list}}

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


