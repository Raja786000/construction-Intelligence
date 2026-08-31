import pymongo
from app.config.settings import settings

class MockCollection:
    def __init__(self, name, db):
        self.name = name
        self.db = db

    def find(self, filter=None, projection=None, *args, **kwargs):
        data = self.db._store.get(self.name, [])
        if filter:
            filtered = []
            for item in data:
                match = True
                for k, v in filter.items():
                    # Handle $in operator
                    if isinstance(v, dict) and "$in" in v:
                        if item.get(k) not in v["$in"]:
                            match = False
                            break
                    elif item.get(k) != v:
                        match = False
                        break
                if match:
                    filtered.append(item)
            return filtered
        return data

    def find_one(self, filter, *args, **kwargs):
        res = self.find(filter)
        return res[0] if res else None

    def insert_one(self, document):
        if "_id" not in document:
            document["_id"] = str(len(self.db._store.get(self.name, [])) + 1)
        self.db._store.setdefault(self.name, []).append(document)
        # return dummy object
        class InsertResult:
            inserted_id = document["_id"]
        return InsertResult()

    def insert_many(self, documents):
        for doc in documents:
            self.insert_one(doc)
        return type('InsertManyResult', (object,), {'inserted_ids': [d.get("_id") for d in documents]})

    def update_one(self, filter, update, upsert=False):
        doc = self.find_one(filter)
        if doc:
            if "$set" in update:
                doc.update(update["$set"])
        elif upsert:
            new_doc = filter.copy()
            if "$set" in update:
                new_doc.update(update["$set"])
            self.insert_one(new_doc)

    def delete_many(self, filter):
        data = self.db._store.get(self.name, [])
        if not filter:
            self.db._store[self.name] = []
            return
        keep = []
        for item in data:
            match = True
            for k, v in filter.items():
                if item.get(k) != v:
                    match = False
                    break
            if not match:
                keep.append(item)
        self.db._store[self.name] = keep

    def count_documents(self, filter):
        return len(self.find(filter))

class MockDatabase:
    def __init__(self):
        self._store = {}

    def __getitem__(self, name):
        return MockCollection(name, self)

# Connect to MongoDB
try:
    print(f"Connecting to MongoDB at: {settings.MONGO_URI}...")
    client = pymongo.MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    db = client[settings.MONGO_DB]
    is_mock_db = False
    print("Successfully connected to MongoDB server!")
except Exception as e:
    print(f"Warning: Failed to connect to MongoDB server ({e}). Falling back to E2E Mock Memory Database.")
    db = MockDatabase()
    is_mock_db = True
