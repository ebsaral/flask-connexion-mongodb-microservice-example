# Flask based microservice example with Connexion and MongoDB

## What is this?

This is an example Flask microservice project built on top of Zalando's Connexion (https://github.com/zalando/connexion) and MongoDB. A microservice should be smaller than this codebase. Since this is an example code, you will see long code blocks to display my knowledge of Python to reviewer.


## How does it work?

- Main entrypoint is `main.py` so you can run `python3 main.py` in your local environment.
- It loads `swagger/spec.yml` and validates parameters (Thanks to Connexion)
- Follows the OpenApi spec as described
- Creates, gets and deletes events (REST Api)
- Creates and returns an aggregated report of events (REST Api)


## Codebase Details

- The layers (architecture) are divided into "Data" (data), "Business" (api) and "View" (view) logics. 
- Check `app/api/query.py` for Class Based example
- Check `app/api/query2.py` if you like functions (shorter) as explained in this video "Stop Writing Classes" 
https://www.youtube.com/watch?v=o9pEzgHorH0
- There is a `settings` file to be used in certain code blocks yet it doesn't cover everything: `app/settings.py`
- `spec.yml` is updated to append "main" as the module name (prefix) in `operationId` attributes. Probably there is a setting for this in Connexion.


## Improvements to do

- Alter the project to be runnable on production (implement gunicorn maybe?)
- Optimize the code for a better memory usage. 
- In production, this microservice might create more connections than necessary to MongoDB. PyMongo has to be integrated with Flask (not done). In a serious environment, I would do some benchmarks to report the improvements.
- Update Dockerfile for production use
- Write `less`, `cleaner` and `faster` code. This code could be shorter as a microservice should be. I didn't have time to iterate over it again and again.  
- Write more tests, especially for `query2.py` :)
- Connect to CircleCI: Run Pylint and CodeCoverage  (**NOTE**: haven't applied to this code yet)


## Assumptions

- `app.data.models.EventDocument` is a class based wrapper of dict to map Mongo documents easily and run commands on it. It assumes that the given object will have either `id` or `_id` parameters. I mostly assumed that given payload will be in the same format.
- Assuming that `PyMongo` (MongoDB) handles edge situations such as inside relations of `group_by` and `sort_by`
- The design principles are demonstrated in several places. It doesn't reflect only one solutions. Different databases or frameworks could be used. I tried to decouple packages from each other so there won't be many dependencies in case of a Python framework change later.
- Assuming that timestamp comparisons doesn't require a conversion of `str` to `datetime` for MongoDB
- **IMPORTANT (TODO)**: Returning aggregated value of "date" in report view is NOT implemented. Lack of time. Therefore since the default behavior is to group by every dimension, please specify some `group_by` value excluding `date`. Grouping by `date` will not give expected response yet.

## Development

Tested and implemented on `Python 3.6.5`

### To run a query (Class based) - TO BE DEPRECATED

This code was written initially in the first implementation. Later, I wanted to `refactor` this code because it was repeating itself a lot and it was long. After the refactor, query2.py was created with function based implementation, yet I have written tests for this Class-Based implementation so I wanted to leave it here as **an example of testing**. After a few iterations, this code `should be deprecated or refactored`.
 
Just an example: 

```
from app.api.query import EventMongoQuery
EventMongoQuery(offset=10, group_by=["valid"]).query()
```
... and so on.

### To run a query (Function based) - SUGGESTED

This function based implementation was written after Class-Based view. It's not complete with a perfect implementation of clean code, yet. I didn't want to spend too much time.

```
from app.api.query2 import run_event_query
from app.data.models import EventDocument

EventDocument.remove_all()
print(f"Total count before: {EventDocument.count_all()}")

for i, event in enumerate(get_events(4, 2)):
    data = EventDocument(event).save()
    print(f"{i+1}: {data}")

print(f"Total count after: {EventDocument.count_all()}")

run_event_query(offset=10, group_by=["valid"])
```
... and so on.

### Run everything

```
sh ./run.sh
```

which works with docker. Works on `localhost:5000` and you can reach swagger at `localhost:5000/ui`


### Test everything

In order to run the tests easily, please run: 
 
`docker-compose exec flask_api pytest`


## Disclaimer

I am running a 10 years old MacBook Pro (`10.11.6` - El Capitan) which `doesn't support Docker`... I had to find another computer to test Docker part, please use at your own risk. :) 

Note: I have wasted many hours because of old computer issues.

Partial copyright: Stylight. 

Written by Emin Buğra Saral - 2019.
