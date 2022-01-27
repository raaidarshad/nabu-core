# Nabu
This repo contains all the code to run the data processing side of Nabu.

## ETL
This project heavily uses Dagster for scheduling and coordination of pipeline runs. Note: The code needs to be updated
to use the latest version/syntax from Dagster, but this "legacy" syntax still works.

### Install
From `etl`, run `poetry install`.

### Run locally
Project requires a running Postgres instance. Raaid, you have a shortcut set up called `pgrun`, which is
actually: `docker run --rm --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_HOST_AUTH_METHOD=trust 
-p 127.0.0.1:5432:5432/tcp postgres`

Then run `init_db.py` with the correct credentials for the local PostgreSQL instance.

Next, From the project root directory, run `dagit -f etl/repositories.py` in one terminal, then run 
`dagster-daemon run` in another. Go to `http://127.0.0.1:3000` in your browser. Use the UI to turn on schedules
and sensors or manually kick off jobs.

### Run remotely
TODO, but look at `infrastructure/etl/__main__.py` for guidance. You need a Postgres instance to point to,
and otherwise we use the official Dagster Helm chart and pass in appropriate values to point to our Docker image
for the "user code" to deploy.

Docker image is automatically tested and updated from GitHub actions whenever there is a code change.

### Run tests
We use pytest.

For unit tests: `pytest etl/tests/unit`
For integration tests (needs a running Postgres instance): `pytest etl/tests/it`

## Infrastructure
Infrastructure-as-code written with Pulumi in Python. Can reference `infrastructure/etl/__main__.py` for required
pieces.

Any updates to this repo's infrastructure code will automatically check and update the infrastructure in DigitalOcean.

## Models
Pydantic/SQLModel models to have consistent data across pipelines and in the database. Auto-published on merge to
master to PyPi.