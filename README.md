# CLIP Image Search

## Demo

Please download and extract the reference dataset (`val2014`) under `static`.

```sh
make run-local
```

The first startup will take some time, as it needs to setup the database and download the CLIP model. Then navigate to `localhost:8000` in the browser for the app.

![demo.jpg](demo.jpg)

As for API doc, go to `localhost:8000/docs`.

## Tech Stack

- CLIP, runs on PyTorch
  - PyTorch does not have the best performance but it gets the job done
  - If we are serious we should have a seprate inference service that has a group of workers on a faster runtime, a queue and a load balance policy
- FastAPI for API endpoints
  - Easy prototyping
  - Great Async performance
  - Serialization and validation are fast after moving to PydanticV2
  - If you are building API from scratch in Python, there really is no better option
  - For this demo, we also use FastAPI to serve files, but in the real world this should be done by somthing like Nginx
- SQLModel for ORM
  - SQLAlchemy but with Pydantic Model that can do validation!
  - The pydantic validation coupled with a static type checker is really a nice DevEx
  - SQLModel also help hiding some of SQLAlchemy's infamous complexity
  - But the async engine lacks doc and is full of pitfalls...
  - To be honest, all Python ORMs sucks... we need something like Prisma...
  - And we have no other option, except go all-in django, but we are building an API, django just has too much functionality and complexity for this simple purpose
- Alembic for migration
  - I mean, there's only one option if you are using SQLAlchemy
- Postgres with pgvector extension
  - You won't want to do np.dot with a 1 million rows matrix...
  - There's lots of database that have vector search, another good and lightweight option I can think of is DuckDB with vector extension, should be great for experimenting
  - Yet we also need to record user rating, let's just stay with a relational database like PG
- HTMX and serveral extentions for the frontend
  - I don't want to setup a full-blown typescript project just for this simple demo
  - HTMX is simple, everythings are just HTML tag and attributes
  - And I personallay really like HTMX, it lets you do HATEOS, the cleanest way to build a web app (but may be limited in functionality)
- Pytest for testing
  - No one want to use the JUnit inspired unittest nowdays...
  - Pytest also has a great plugin ecosystem!
- Ruff for linting
  - It's fast, way faster than all other alternatives
  - The ruleset is built-in and comprehensive, you don't need th huntdown the flake8 extensions anymore!
- Pyright for type checking
  - Faster than mypy
  - Most people use VSCode, and VSCode's Python LSP also uses Pyright, haveing the save checker as the IDE streamlined the DevEx
- Pre-commit for annoying people
  - You should not passed! Before fixing this and that and ...
  - Thankfully most things can be auto-fixed

## API

There are only two endpoints.

### GET `/api/search`

The text query is passed in the url parameter (just like google search). But if we want to let user input super looooong query or even upload a text file, this endpoint better be a `POST` and pass query in the body.

### PATCH `/rating/{search_log_id}`

From the database and ORM perspective, to be "restful" we should have a endpoint `/searchlog/{search_log_id}`, but I will argue that an API client doesn't really need to know the exact structure of the database, straight up mapping the schema to the API is just lazy design.

As for this demo the client have no interest in CRUD the search log, having a dedicated route just for rating makes the API surface smaller and more ergonomics.

## Developent

Run the stack in docker compose watch mode.

```sh
make run-dev
```

Then enter the dev shell in the container.

```sh
docker compose exec api bash
```

Start the API server.

```sh
fastapi run --reload app/main.py
```

Compile a migartion.

```sh
alembic revision --autogenerate -m "hope this won't break our client's dat"
```

Run tests.

```sh
pytest .
```

## References

- [FastAPI](https://github.com/fastapi/fastapi) and [Pydantic](https://github.com/pydantic/pydantic) ([core](https://github.com/pydantic/pydantic-core) is written in Rust, fast fast!)
- [FastAPI template](https://github.com/fastapi/full-stack-fastapi-template)
- [pgvector](https://github.com/pgvector/pgvector) and its [Python intergration](https://github.com/pgvector/pgvector-python)
- [SQLModel](https://sqlmodel.tiangolo.com/), I like the design, but I don't like the underlying async SQLAlchemy
- [HTMX](https://github.com/bigskysoftware/htmx)
- [pytest](https://github.com/pytest-dev/pytest)
- [ruff](https://github.com/astral-sh/ruff)
- [pyright](https://github.com/microsoft/pyright)
- [pre-commit](https://github.com/pre-commit/pre-commit)
