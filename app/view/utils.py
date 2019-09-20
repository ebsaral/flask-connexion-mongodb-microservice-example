import uuid


def error(message, code):
    return {"message": message}, code


def is_valid_uuid(uuid_string):
    try:
        uuid.UUID(uuid_string, version=4)
        return True
    except ValueError:
        return False
