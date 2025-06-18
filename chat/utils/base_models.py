from pymongo import MongoClient
import os
from datetime import datetime
from dotenv import load_dotenv
from django.db import models

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB_NAME")]

class BaseMongoModel(models.Model):

    collection = None

    class Meta:
        abstract = True

    def insert_one(self, document: dict):
        document["created_at"] = datetime.utcnow()
        return db[self.collection].insert_one(document)

    def find_one(self, filter: dict):
        return db[self.collection].find_one(filter)

    def find_many(self, filter: dict):
        return list(db[self.collection].find(filter))  # cast to list

    def update(self, filter: dict, update: dict):
        update["updated_at"] = datetime.utcnow()
        return db[self.collection].update_one(filter, {"$set": update})

    def delete(self, filter: dict):
        return db[self.collection].delete_one(filter)

    def get_data_by_id(self, _id: str):
        return db[self.collection].find_one({"_id": _id})
