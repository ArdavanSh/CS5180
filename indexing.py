#-------------------------------------------------------------------------
# AUTHOR: Ardavan Sherafat
# FILENAME: indexing.py
# SPECIFICATION: description of the program
# FOR: CS 5180- Assignment #1
# TIME SPENT: how long it took you to complete the assignment
#-----------------------------------------------------------*/

#Importing some Python libraries
import csv
import numpy as np
from collections import Counter

documents = []

#Reading the data in a csv file
with open('collection.csv', 'r') as csvfile:
  reader = csv.reader(csvfile)
  for i, row in enumerate(reader):
         if i > 0:  # skipping the header
            documents.append (row[0])

#Conducting stopword removal for pronouns/conjunctions. Hint: use a set to define your stopwords.
#--> add your Python code here
stopWords = {"I", "and", "She", "her", "They", "their"}
newDocs = []

for doc in documents:
    tempDoc = doc.split(" ")
    temp = []
    for word in tempDoc:
        if word not in stopWords:
            temp.append(word)
    newDocs.append(temp)

#Conducting stemming. Hint: use a dictionary to map word variations to their stem.
#--> add your Python code here
steeming = {'love':'love', 'loves':'love', 'cats':'cat', 'cat':'cat', 
            'dogs':'dog', 'dog':'dog'}

for doc in newDocs:
    for i in range(len(doc)):
        doc[i] = steeming[doc[i]]

#Identifying the index terms.
#--> add your Python code here
terms = []
seen = set()
termCounter = []
for doc in newDocs:
    termCounter.append(Counter(doc))
    for word in doc:
        if word not in seen:
            terms.append(word)
            seen.add(word)

#Building the document-term matrix by using the tf-idf weights.
#--> add your Python code here
docTermMatrix = np.array([[0.0 for _ in range(len(terms))] for _ in range(len(newDocs))])


for i in range(len(newDocs)):
    docLength = len(newDocs[i])
    for j in range (len(terms)):
        tf = termCounter[i][terms[j]] / docLength
        docTermMatrix[i][j] = tf

D = len(newDocs)
for i in range(len(terms)):
    df = 0
    for j in range(len(newDocs)):
        if terms[i] in termCounter[j]:
            df += 1
    idf = np.log10(abs(D)/df)
    docTermMatrix[:,i] = docTermMatrix[:,i]*idf


# #Printing the document-term matrix.
# #--> add your Python code here

print(docTermMatrix)
