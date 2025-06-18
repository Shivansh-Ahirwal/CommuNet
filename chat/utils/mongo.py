# utils/mongo.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

def insert_one(collection_name, data: dict):
    return db[collection_name].insert_one(data)

def find_one(collection_name, query: dict):
    return db[collection_name].find_one(query)

def find_all(collection_name, query: dict = {}):
    return list(db[collection_name].find(query))

def update_one(collection_name, query: dict, update: dict):
    return db[collection_name].update_one(query, {"$set": update})

def delete_one(collection_name, query: dict):
    return db[collection_name].delete_one(query)
