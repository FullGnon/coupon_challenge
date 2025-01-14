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
To run the API in dev mode, execute the following command:

```bash
uv run fastapi dev src/araiko_challenge/main.py
```
The API will be available at: http://127.0.0.1:8000
Swagger documentation can be accessed at: http://127.0.0.1:8000/docs

This setup provides automatic reloading for easier development and testing.

### docker mode
To run the API within a docker container use docker:

```bash
docker compose up
```