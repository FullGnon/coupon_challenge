# Araïko Challenge

For directives see [here](./CHALLENGE.md)

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
ARAIKO_CHALLENGE_DB_BACKEND=mongo
ARAIKO_CHALLENGE_MONGO_DB_URI=mongodb://admin:password@127.0.0.1:27017/
```

To run the API in dev mode, execute the following command:

```bash
uv run --env-file .env fastapi dev src/araiko_challenge/main.py
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