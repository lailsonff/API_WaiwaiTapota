from datetime import datetime
from pymongo import MongoClient, DESCENDING, ASCENDING, TEXT
from bson import ObjectId
from config import config

from gridfs import GridFS, NoFile
from flask import abort, current_app, request, make_response, jsonify
from werkzeug.wsgi import wrap_file
import mimetypes
from mimetypes import guess_type

# Adicionando tipos pendentes de extensões
mimetypes.add_type('audio/mpeg', '.m4a', strict=True)
mimetypes.add_type('audio/webm;codecs=opus/json', '.weba', strict=True)


class Database(object):
    def __init__(self):
        self.client = MongoClient(config["DB_URL"]+":"+config["DB_PORT"])  # configure db url
        self.db = self.client[config['DB_NAME']]  # configure db name
        self.db["palavras"].create_index([("wordPort", TEXT)], default_language='portuguese')

    def insert(self, element, collection_name):
        # https://stackoverflow.com/questions/2150739/iso-time-iso-8601-in-python
        element["created"] = datetime.now().isoformat()
        element["updated"] = datetime.now().isoformat()
        inserted = self.db[collection_name].insert_one(element)  # insert data to db
        
        return str(inserted.inserted_id)

    def find(self, criteria, collection_name, projection=None, sort=[("updated", DESCENDING)], limit=0, cursor=False ):  # find all from db

        if "_id" in criteria:
            criteria["_id"] = ObjectId(criteria["_id"])

        found = self.db[collection_name].find(filter=criteria, projection=projection, limit=limit, sort=sort)

        if cursor:
            return found

        found = list(found)

        for i in range(len(found)):  # to serialize object id need to convert string
            if "_id" in found[i]:
                found[i]["_id"] = str(found[i]["_id"])

        return found

    def find_by_id(self, id, collection_name):
        found = self.db[collection_name].find_one({"_id": ObjectId(id)})
        
        if found is None:
            abort(404)
        
        if "_id" in found:
             found["_id"] = str(found["_id"])

        return found


    def update(self, id, element, collection_name):
        criteria = {"_id": ObjectId(id)}

        element["updated"] = datetime.now().isoformat()
        set_obj = {"$set": element}  # update value

        updated = self.db[collection_name].update_one(criteria, set_obj)
        if updated.matched_count == 1:
            return element

    def delete(self, id, collection_name):
        deleted = self.db[collection_name].delete_one({"_id": ObjectId(id)})
        return bool(deleted.deleted_count)


    def save_file(self, filename, fileobj, base="fs", content_type=None, oidword=None, user=None, **kwargs):
        if not isinstance(base, str):
            raise TypeError("'base' must be string or unicode")
        if not (hasattr(fileobj, "read") and callable(fileobj.read)):
            raise TypeError("'fileobj' must have read() method")
        if content_type is None:
            # https://docs.python.org/pt-br/3/library/mimetypes.html#mimetypes.add_type
            content_type, _ = guess_type(filename)
        storage = GridFS(self.db, base)
        id = storage.put(fileobj, filename=filename, content_type=content_type, wordOid=oidword, user=user, **kwargs)
        return id

    def delete_file(self, filename, base="fs", content_type=None, oidword=None, **kwargs):
        if not isinstance(base, str):
            raise TypeError("'base' must be string or unicode")
        if content_type is None:
            # https://docs.python.org/pt-br/3/library/mimetypes.html#mimetypes.add_type
            content_type, _ = guess_type(filename)
        storage = GridFS(self.db, base)
        return storage.delete(ObjectId(filename))
        
    def send_file(self, filename, base="fs", version=-1, cache_for=31536000):
        if not isinstance(base, str):
            raise TypeError("'base' must be string or unicode")
        if not isinstance(version, int):
            raise TypeError("'version' must be an integer")
        if not isinstance(cache_for, int):
            raise TypeError("'cache_for' must be an integer")

        storage = GridFS(self.db, base)
        
        try:
            fileobj = storage.find_one({'_id': ObjectId(filename)})
        except NoFile:
            abort(404)
        # mostly copied from flask/helpers.py, with
        # modifications for GridFS
        # https://gist.github.com/hosackm/289814198f43976aff9b
        data = wrap_file(request.environ, fileobj, buffer_size=1024 * 255)
        response = current_app.response_class(
            data,
            mimetype=fileobj.content_type,
            direct_passthrough=True,
        )
        response.content_length = fileobj.length
        response.last_modified = fileobj.upload_date
        # response.set_etag(fileobj.md5)
        response.cache_control.max_age = cache_for
        response.cache_control.public = True
        response.make_conditional(request)
        return response

    # def send_file(self, filename, base="fs", version=-1, cache_for=31536000):
    #     try:
    #         file = GridFS(self.db, base).find_one({"filename": filename})
    #         response = make_response(file.read())
    #         response.mimetype = file.content_type
    #         return response
    #     except NoFile:
    #         abort(404)
