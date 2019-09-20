#!/usr/bin/env python3
import connexion
import json
import logging

from flask import Response
from werkzeug.exceptions import HTTPException

from app.settings import PORT, DEBUG
from app.view.reports import get as aggregated_report_view
from app.view.events import (get as get_view,
                             create as create_view,
                             delete as delete_view)


def generic_error(exception):
    return Response(
        response=json.dumps({'message': 'Invalid!'}),
        status=406,
        mimetype="application/json",
    )


def get_report(**kwargs):
    logging.info(f"kwargs: {kwargs}")
    return aggregated_report_view(**kwargs)


def create_event(body):
    logging.info(f"body: {body}")
    return create_view(body)


def get_event(event_id):
    logging.info(f"event_id: {event_id}")
    return get_view(event_id)


def delete_event(event_id):
    logging.info(f"event_id: {event_id}")
    return delete_view(event_id)


logging.basicConfig(level=logging.INFO)

app = connexion.App(__name__, specification_dir="swagger/")
app.add_api("spec.yml")
app.add_error_handler(HTTPException, generic_error)

if __name__ == "__main__":
    app.run(port=PORT, debug=DEBUG)  # TODO: Move to settings
