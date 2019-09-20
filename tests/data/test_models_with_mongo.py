from .. import EventDocument
from .. import MONGO_CLIENT

TEST_COLLECTION = MONGO_CLIENT["test"]["events"]


def destroy_data():
    TEST_COLLECTION.delete_many({})


def create_data():
    destroy_data()
    TEST_COLLECTION.insert_one({"foo1": "bar1", "_id": "testid1"})
    TEST_COLLECTION.insert_one({"foo2": "bar2", "_id": "testid2"})


def setup_module(module):
    EventDocument.collection = TEST_COLLECTION


def teardown_module(module):
    destroy_data()


def test_mongo_model_can_get_object():
    create_data()
    obj = EventDocument({"id": "testid1"}).get_object()
    assert obj == {"foo1": "bar1", "_id": "testid1"}


def test_mongo_model_can_reload_with_object():
    document = EventDocument(
        {"id": "testid1", "xyz": "tzy"}
    ).reload(
        obj={"foo": "bar"}
    )
    assert document == {"id": "testid1", "foo": "bar", "xyz": "tzy"}


def test_mongo_model_can_reload_without_object():
    create_data()
    document = EventDocument({"id": "testid1", "xyz": "tzy"})
    document.reload()
    test_dict = {
        "id": "testid1",
        "_id": "testid1",
        "foo1": "bar1",
        "xyz": "tzy",
    }
    assert document == test_dict


def test_mongo_model_can_save_without_object_to_create():
    document = EventDocument({"id": "testid3", "xyz": "tzy"})
    document.save_with()
    assert document == {"id": "testid3", "_id": "testid3", "xyz": "tzy"}
    test_dict = TEST_COLLECTION.find_one({"_id": "testid3"})
    assert test_dict == {"_id": "testid3", "xyz": "tzy"}


def test_mongo_model_can_save_with_object_to_update():
    document = EventDocument({"id": "testid4", "xyz": "tzy"})
    TEST_COLLECTION.insert_one({"foo1": "bar1", "_id": "testid4"})
    test_obj = document.get_object()
    document.save_with(test_obj)
    test_dict = {
        "id": "testid4",
        "_id": "testid4",
        "foo1": "bar1",
        "xyz": "tzy",
    }
    assert document == test_dict
    test_dict = TEST_COLLECTION.find_one({"_id": "testid4"})
    assert document.get_object() == test_dict


def test_mongo_model_can_save_and_create():
    document = EventDocument({"id": "testid6", "foo": "bar"})
    document.save()
    test_dict = TEST_COLLECTION.find_one({"_id": "testid6"})
    assert document == {"id": "testid6", "_id": "testid6", "foo": "bar"}
    assert test_dict == {"_id": "testid6", "foo": "bar"}


def test_mongo_model_can_remove():
    create_data()
    document = EventDocument({"id": "testid1"})
    document.remove()
    test_dict = TEST_COLLECTION.find_one({"_id": "testid1"})
    assert not document
    assert not test_dict


def test_event_document_can_remove_all():
    create_data()
    assert TEST_COLLECTION.count_documents({}) == 2
    assert EventDocument.collection.count_documents({}) == 2
    EventDocument.remove_all()
    assert TEST_COLLECTION.count_documents({}) == 0
    assert EventDocument.collection.count_documents({}) == 0
