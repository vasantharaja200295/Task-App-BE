from pymongo import MongoClient, ReturnDocument
from dotenv import load_dotenv
import os
import datetime

load_dotenv('.env')


class MongoDB:
    def __init__(self, db_name='test_database', env='dev'):
        if env != 'dev':
            connection_string = os.getenv('MONGO_CONNECTION_ONLINE')
        else:
            connection_string = os.getenv('MONGO_CONNETION_DEV')
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]

    def create_document(self, collection_name, document):
        collection = self.db[collection_name]
        result = collection.insert_one(document)
        return str(result.inserted_id)

    def read_documents(self, collection_name, query={}, projection=None):
        collection = self.db[collection_name]
        documents = collection.find(query, projection)
        return [self._serialize(doc) for doc in documents]

    def read_document(self, collection_name, query, projection=None):
        collection = self.db[collection_name]
        document = collection.find_one(query, projection)
        return self._serialize(document)

    def update_documents(self, collection_name, query, new_values):
        collection = self.db[collection_name]
        result = collection.update_many(query, {"$set": new_values})
        return result.modified_count

    def update_document(self, collection_name, query, new_values):
        collection = self.db[collection_name]
        result = collection.find_one_and_update(
            query, {"$set": new_values}, return_document=ReturnDocument.AFTER)
        return self._serialize(result)

    def delete_documents(self, collection_name, query):
        collection = self.db[collection_name]
        result = collection.delete_many(query)
        return result.deleted_count

    def delete_document(self, collection_name, query):
        collection = self.db[collection_name]
        result = collection.find_one_and_delete(query)
        return self._serialize(result)
    
    def count_documents(self, collection_name, query={}):
        collection = self.db[collection_name]
        return collection.count_documents(query)

    def _serialize(self, document):
        if document is None:
            return None
        if '_id' in document:
            document['_id'] = str(document['_id'])
        for key, value in document.items():
            if isinstance(value, datetime.datetime):
                document[key] = value.isoformat()

        return document