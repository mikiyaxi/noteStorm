
from dotenv import load_dotenv, find_dotenv
import os
import pprint 
from pymongo import MongoClient 
# create a .env file within the same directory
load_dotenv(find_dotenv())


# username 
username = "mikiyaxi"
# connection setup
password = os.environ.get("MONGODB_PASSWD")
# remember to replace the password field: mongodb+srv://mikiyaxi:<password>@cluster0.cfpainh.mongodb.net/?retryWrites=true&w=majority
connection_string = f"mongodb+srv://{username}:{password}@cluster0.cfpainh.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(connection_string)

# collect all the database inside 
dbs = client.list_database_names()

# Get the specific database
movie_db = client['movie']

# List all collections in the database
collections = movie_db.list_collection_names()

# Check and print the collections
if collections:
    print("Existing collections:", collections)
else:
    print("No collections found in the database.")


# Specify the collection
movies_collection = movie_db['general-info']

# Create a new document
new_movie = {
    "title": "Inception",
    "director": "Christopher Nolan",
    "year": 2010
}

# Insert the document
result = movies_collection.insert_one(new_movie)

# Print the ID of the new document
print("Inserted ID:", result.inserted_id)

