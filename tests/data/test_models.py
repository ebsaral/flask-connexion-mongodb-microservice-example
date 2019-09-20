import pytest

from .. import MongoModel


def test_mongo_model_init_gives_an_exception():
    with pytest.raises(AttributeError):
        MongoModel()


def test_mongo_model_init_success():
    model = MongoModel({"id": "test-id"})
    assert model.id == "test-id"
    model = MongoModel({"id": "test-id2", "foo": "bar"})
    assert model == {"id": "test-id2", "foo": "bar"}
    assert model.id == "test-id2"


def test_mongo_model_can_pop_keys():
    model = MongoModel({"id": "test-id2", "foo": "bar", "xyz": "zrm"})
    new_dict = model.pop_keys(["foo"])
    assert new_dict == {"id": "test-id2", "xyz": "zrm"}
    new_dict = model.pop_keys(["foo", "xyz"])
    assert new_dict == {"id": "test-id2"}


def test_mongo_model_can_return_mongo_dict():
    model = MongoModel({"id": "test-id1", "_id": "dummy"})
    mongo_dict = model.mongo()
    assert mongo_dict == {"_id": "test-id1"}


def test_mongo_model_can_return_pure_dict_without_any_id():
    model = MongoModel({"id": "test-id1", "foo": "bar"})
    pure_dict = model.pure()
    assert pure_dict == {"foo": "bar"}


def test_mongo_model_can_serialize_with_id():
    model = MongoModel({"id": "test-id1", "_id": "dummy", "foo": "bar"})
    serialized_dict = model.serialize()
    assert serialized_dict == {"id": "test-id1", "foo": "bar"}
