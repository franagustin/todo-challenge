# Taskinator

Build a TODO list API for users to schedule their tasks.


# How to run?

## Installing dependencies

**Python version**: 3.6+

**This project uses [Poetry](https://python-poetry.org/)**. You should [install](https://python-poetry.org/docs/#installation) it as well.

**Installing python packages (requirements)**
```
poetry install
```

## Migrations

**Making**
```
poetry run python manage.py makemigrations
```

**Running**
```
poetry run python manage.py migrate
```

## Development

```
poetry run python manage.py runserver
```

## WSGI

```
poetry add uwsgi
poetry run uwsgi todo_challenge.wsgi:application
```

## ASGI

```
poetry add daphne
poetry run daphne todo_challenge.asgi:application
```

## Docker

This approach uses daphne and ASGI inside a Docker container.

```
docker build -t taskinator .
docker run -p 8000:80 taskinator
# You may customise the container port as well:
docker run -p 8000:8000 taskinator -p 8000
```


# How to use? (API Reference)

This API has two main endpoints:

## Task Groups

Located at **/api/task-groups/**. A group basically holds related tasks together so they can be, for example, displayed in a single column by a frontend application.

### List
* **Path**: /api/task-groups/
* **Method**: GET
* **Parameters**: None

### Create
* **Path**: /api/task-groups/
* **Method**: POST
* **Parameters**: *Body may be sent either as JSON or multipart form data.*
    * **name**: (*string*) In Body.

### View task group in detail
* **Path**: /api/task-groups/{TASK_GROUP_ID}
* **Method**: GET
* **Parameters**: None

### Update
* **Path**: /api/task-groups/{TASK_GROUP_ID}
* **Method**: PATCH | PUT
* **Parameters**: *Body may be sent either as JSON or multipart form data.*
    * **name**: (*string*) In Body.

### Delete
* **Path**: /api/task-groups/{TASK_GROUP_ID}
* **Method**: DELETE
* **Parameters**: None


## Tasks

Located at **/api/tasks/**. Represents each single item in the TODO list.

### List
* **Path**: /api/tasks/
* **Method**: GET
* **Parameters**:
    * **date**: (*datetime*) Query. Filter a specific creation date.
    * **date__lt**: (*datetime*) Query. Filter by creation date less than.
    * **date__lte**: (*datetime*) Query.  Filter by creation date less than or equal to.
    * **date__gt**: (*datetime*) Query. Filter by creation date greater than.
    * **date__gte**: (*datetime*) Query. Filter by creation date greater than or equal to.
    * **finished**: (*string: true | false*) Query. Display only finished or unfinished tasks.
    * **search**: (*string*) Query. Display only tasks containing this expression in their name or description.

### Create
* **Path**: /api/tasks/
* **Method**: POST
* **Parameters**: *Body may be sent either as JSON or multipart form data.*
    * **name**: (*string*) In Body.
    * **description**: (*string*) In Body.
    * **due_date**: (*datetime*) In Body.

### View task in detail
* **Path**: /api/tasks/{TASK_ID}
* **Method**: GET
* **Parameters**: None

### Update
* **Path**: /api/tasks/{TASK_ID}
* **Method**: PATCH | PUT
* **Parameters**: *Body may be sent either as JSON or multipart form data.*
    * **name**: (*string*) In Body.
    * **description** (*string*) In Body.
    * **due_date** (*datetime*) In Body.

### Delete
* **Path**: /api/tasks/{TASK_ID}
* **Method**: DELETE
* **Parameters**: None


## Authentication

All requests to this API should be authenticated by including a Token in the request headers.

```
Authorization: Token XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```
