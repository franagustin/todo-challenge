FROM python:3.9

RUN pip install poetry
ADD poetry.lock /app/
ADD pyproject.toml /app/
WORKDIR /app/
RUN poetry run pip install daphne
RUN poetry install

ADD . /app/

ENTRYPOINT ["poetry", "run", "daphne", "todo_challenge.asgi:application", "-b", "0.0.0.0", "-p", "80"]
