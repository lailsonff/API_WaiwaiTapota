from factory.validation import Validator
from factory.database import Database
from datetime import datetime

class Palavra(object):
    def __init__(self):
        self.validator = Validator()
        self.db = Database()

        self.collection_name = 'palavras'  # collection name

        self.fields = {
            "wordPort": "string",
            "translationWaiwai": "string",
            "category": "string",
            "meaningPort": "string",
            "meaningWaiwai": "string",
            "synonymPort": "string",
            "synonymWaiwai": "string",
            "approved": "boolean",
            "user": "string"
        }

        self.create_required_fields = [
            "wordPort",
            "translationWaiwai",
            "user"
        ]

        # Fields optional for CREATE
        self.create_optional_fields = [
            "category",
            "meaningPort",
            "meaningWaiwai",
            "synonymPort",
            "synonymWaiwai",
            "approved"
        ]

        # Fields required for UPDATE
        self.update_required_fields = [
        ]

        # Fields optional for UPDATE
        self.update_optional_fields = [
            "updated",
            "created",
            "wordPort",
            "translationWaiwai",
            "category",
            "meaningPort",
            "meaningWaiwai",
            "synonymPort",
            "synonymWaiwai",
            "approved",
            "user"
        ]

    def create(self, word):
        # Validator will throw error if invalid
        word["approved"] = False
        self.validator.validate(word, self.fields, self.create_required_fields, self.create_optional_fields)
        res = self.db.insert(word, self.collection_name)
        return dict(_id=res)

    def find(self, word, *args):  # find all
        if args:
            category= args[0].get("filters[category]")
            wordPort= args[0].get("filters[wordPort]")
            if category:
                word["category"]=category
            elif wordPort: 
                # https://www.mongodb.com/docs/manual/reference/operator/query/regex/
                # https://www.mongodb.com/docs/v4.4/text-search/
                word["wordPort"]=  { "$regex": wordPort, "$options": 'i'}
        return self.db.find(word, self.collection_name)
    def find_by_username(self, username):
        return self.db.find({'user': {'$eq': username}}, self.collection_name)

    def find_by_id(self, id):
        return self.db.find_by_id(id, self.collection_name)

    def update(self, id, word):
        word["updated"] = datetime.now().isoformat()
        self.validator.validate(word, self.fields, self.update_required_fields, self.update_optional_fields)
        return self.db.update(id, word,self.collection_name)

    def delete(self, id):
        return self.db.delete(id, self.collection_name)