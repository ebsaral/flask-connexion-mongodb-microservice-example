from connexion import NoContent

from .utils import error, is_valid_uuid
from ..data.models import EventDocument

EVENT_NOT_FOUND = "Event not found"
EVENT_ALREADY_EXISTS = "Event already exists"
EVENT_INVALID_ID = "Invalid ID supplied"


def create(body):
    doc = EventDocument(body)

    if doc.get_object():
        return error(EVENT_ALREADY_EXISTS, 409)

    doc.save()
    return NoContent, 201


# TODO: Add some decorators for validations: less code, such as: @verify_uuid
def get(event_id):
    if not is_valid_uuid(event_id):
        return error(EVENT_INVALID_ID, 400)

    doc = EventDocument(id=event_id)

    if not doc.get_object():
        return error(EVENT_NOT_FOUND, 400)

    return doc.reload().serialize(), 200


def delete(event_id):
    doc = EventDocument(id=event_id)

    if not is_valid_uuid(event_id) or not doc.get_object():
        return error(EVENT_INVALID_ID, 400)

    doc.remove()
    return NoContent, 204
