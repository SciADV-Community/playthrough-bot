# Playthrough-bot

A role bot for visual novel playthrough servers!

## Setup

-   Clone repo
-   Create and set up the environment with `poetry install`.
-   Initialize the config with `poetry run init`.

## Database Management

After making changes to the models, make sure to migrate the database with:
```
poetry run makemigration
poetry run migrate
```

When asked for a message to add to the migration, add a short semantically rich message that describes what the migration is about.

## Testing

To run the tests locally, run `poetry run test`.
