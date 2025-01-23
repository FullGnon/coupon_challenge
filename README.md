# Coupon Challenge

For directives see [here](./CHALLENGE.md)

I hope this is easy to understand. Have fun! 😉

## Requirements

This project requires [uv](https://docs.astral.sh/uv/getting-started/installation) to run. Please ensure `uv` is installed on your system before proceeding.

## Getting started

The entry point for the CLI is called `soldes`. After cloning the project, you can execute commands using `uv run`.

**examples**
```bash
uv run soldes [add_coupon|test_product] ...
```

!!! note
The venv will be automatically created and synced based on pyproject.toml.

## Run the API

### Dev mode

#### Requirements:
In order to configure the application in dev mode you need to create a dotfile `.env` containing settings:

```bash
COUPON_CHALLENGE_DB_BACKEND=mongo
COUPON_CHALLENGE_MONGO_DB_URI=mongodb://admin:password@127.0.0.1:27017/
```

To run the API in dev mode, execute the following command:

```bash
uv run --env-file .env fastapi dev src/coupon_challenge/main.py
```
The API will be available at: http://127.0.0.1:8000
Swagger documentation can be accessed at: http://127.0.0.1:8000/docs

This setup provides automatic reloading for easier development and testing.

### Docker mode
To run the API within a docker container use docker:

```bash
docker compose up
```

Everything is already configured to work right away.

That's all folks ;)

## Run the CLI

I implemented a Typer CLI that utilizes the same services as the API. Alternatively, I could have leveraged FastAPI's OpenAPI specification to generate an SDK for interacting with the API.

### Requirements

You have to set the same environement variable as the app in order to use the proper backend:

```bash
COUPON_CHALLENGE_DB_BACKEND=mongo
COUPON_CHALLENGE_MONGO_DB_URI=mongodb://admin:password@127.0.0.1:27017/
```

either set directly this variable or use a dotfile:

```bash
export COUPON_CHALLENGE_DB_BACKEND=mongo
export COUPON_CHALLENGE_MONGO_DB_URI=mongodb://admin:password@127.0.0.1:27017/
uv run soldes coupons --help
# OR 
uv run --env-file .env soldes coupons --help
```

## Running tests

You can run the tests effortlessly using uv by executing the following command:

```bash
uv run pytest
```

## Linting and Formatting the Code

To maintain code quality, it's a good idea to use automated tools for linting and formatting. While a pre-commit hook could handle this automatically, for this challenge, I am running the commands manually.

You can lint and format your code with the following command:

```bash
uvx ruff check --fix && uvx ruff format
```

Additionally, I recommend using mypy to ensure type safety throughout the project.


# Known limitations/bugs
* Update on condition and/or validity remove previous values, the update is not propagated :/

# Time's up !
I do not have more time to implements the complex filtering feature. But I would have:

## Created my own query engine based on Pydantic Model

Note: I would first research whether there is an open-source library that already fulfills this functionality.

### Why
* Database-Agnostic Logic: To not couple the query logic with any database query language, so i can switch db backend as will.
* Reusability: This query engine could be reused as a library anywhere else

### How
```python
# These define simple comparison logic like "equals", "greater or equal", "greater than", ...
class EqOperator:
    """"""
class GeOperator:
    """"""
class GtOperator:
    """"""

# Query object combine multiple predicates or sub-queries to form complex conditions.
class AndQuery:
    """"""
class OrQuery:
    """"""
class NotQuery:
    """"""

class Predicate:
    """ Represents a single logical condition."""
    def __init__(self, field, operator, value):
        self.field = field
        self.operator = operator
        self.value = value # Could be empty 

    def validate_field():
        """Should match a Product attribute"""

# Usage
# Simple Predicate
category_electronics = Predicate("category", EqOperator, "electronics")
price_above_500 = Predicate("price", GtOperator, 500)
not_furniture = NotQuery(Predicate("category", EqOperator, "furniture"))

# We want a electronics product or a expensive product
electronics_or_expensive = OrQuery(category_electronics, price_above_500)

# In the case a product can have many category or the product is expensive 
# we exclude furniture product
query = AndQuery(electronics_or_expensive, not_furniture)

# Test the product upon query
apply_query(query, product)

# For each database backend we should have a converter (sharing a single common interface) in order to use database performance.
```

# Next Steps
* More tests! I know there are some bugs somewhere; it lacks proper edge case tests.
* Add a CI/CD pipeline for better code quality and robustness.
* Add a test coverage report (to the moon!).
* Automate end-to-end/integration tests on nightly deployments (using Terraform, maybe?).
* More documentation! I’ve been in a rush lately and focused on code rather than explaining it.
* Benchmarking to test scalability and suggest an architecture for deployment (load-balancing, backup, ...)
* Security hardening.
* API version management.
* Database version management, with automated migrations if needed.
* And more, there is always something to do