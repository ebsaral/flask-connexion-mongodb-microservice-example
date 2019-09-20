from ..settings import MONGO_CLIENT, MONGO_DB_NAME, MONGO_COLLECTION_NAME


class MongoModel(dict):
    """
    This Model wraps a Mongo document into a python dictionary
    Works with a parent class with a defined "collection"
    """
    ID_KEY = "id"
    MONGO_ID_KEY = "_id"

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, *args, **kwargs):
        super(MongoModel, self).__init__(*args, **kwargs)
        self._verify_id()

    def _verify_id(self):
        if self._id and not self.id:
            self.id = self._id
        if not self.id:
            raise AttributeError("You need to have the model with an 'id'")

    def pop_keys(self, keys):
        target_dict = self.copy()
        for key in keys:
            if key in target_dict:
                target_dict.pop(key)
        return target_dict

    def mongo(self):
        new_dict = self.pop_keys([self.ID_KEY])
        new_dict[self.MONGO_ID_KEY] = self.id
        return new_dict

    def pure(self):
        new_dict = self.pop_keys([self.ID_KEY, self.MONGO_ID_KEY])
        return new_dict

    def serialize(self):
        new_dict = self.pop_keys([self.MONGO_ID_KEY])
        return new_dict

    def get_object(self):
        return self.collection.find_one({self.MONGO_ID_KEY: self.id})

    def reload(self, obj=None):
        target_obj = obj or self.get_object()
        if target_obj:
            self.update(target_obj)
            if self.MONGO_ID_KEY in target_obj:
                self._id = target_obj[self.MONGO_ID_KEY]
        return self

    def save_with(self, obj=None):
        if obj:
            self.collection.update_one({self.MONGO_ID_KEY: self.id},
                                       {"$set": self.mongo()})
            self.reload()
        else:
            inserted_obj = self.collection.insert_one(self.mongo())
            self._id = inserted_obj.inserted_id
        return self

    def save(self):
        self._verify_id()
        obj = self.get_object()

        if self._id:
            self.reload(obj=obj)
        else:
            self.save_with(obj)
        return self.serialize()

    def remove(self):
        self.save()  # TODO: This is an overload. Refactor this.
        self.collection.delete_one({"_id": self._id})
        self.clear()
        return self


class EventDocument(MongoModel):
    collection = MONGO_CLIENT[MONGO_DB_NAME][MONGO_COLLECTION_NAME]

    @staticmethod
    def remove_all():
        return EventDocument.collection.delete_many({})

    @staticmethod
    def count_all():
        return EventDocument.collection.count_documents({})
