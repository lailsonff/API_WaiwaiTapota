from factory.database import Database

class Upload(object):
    def __init__(self):
        self.db = Database()

        self.collection_name = 'fs.files'  # collection name
    def find(self, word_id=None, content_type=None):  # find all
        """
        word_id: str(ObjectId(''))
        content_type: 'image' || 'audio'            
        """
        filter={
            'contentType': {
                '$regex': content_type
            }, 
            'wordOid': {
                '$eq': word_id
            }
        }
        sort=list({
            'uploadDate': -1
        }.items())
        limit=1
        return self.db.find(filter, self.collection_name, sort=sort, limit=limit)
