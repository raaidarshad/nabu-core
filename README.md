# Nabu
This repo contains all the code to run the data processing side of Nabu.

[API Base URL](https://api.nabu.news)
[Dagit UI](https://dagster.nabu.news) - Note that this is not publicly accessible

[Website](https://www.nabu.news)
[Website code repository](https://github.com/raaidarshad/nabu-website)
[Firefox Extension](https://addons.mozilla.org/en-US/firefox/addon/nabu/)
[Chrome Extension](https://chrome.google.com/webstore/detail/nabu/bgmcmbjhfdnfaplfiiphlefclhhhnajb)
[Extension code repository](https://github.com/raaidarshad/nabu-browser-extension)

## ETL
This project heavily uses Dagster for scheduling and coordination of pipeline runs. Note: The code needs to be updated
to use the latest version/syntax from Dagster, but this "legacy" syntax still works.

### Install
From `etl`, run `poetry install`.

### Run locally
Project requires a running Postgres instance. Raaid, you have a shortcut set up called `pgrun`, which is
actually: `docker run --rm --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_HOST_AUTH_METHOD=trust 
-p 127.0.0.1:5432:5432/tcp postgres`

Then run `init_db.py` with the correct credentials for the local PostgreSQL instance. (This might not be necessary)

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
For integration tests (needs a running Postgres instance, see instructions above for that): `pytest etl/tests/it`

### Container
todo

### Helm
todo

### Dagit UI
The Dagit UI for Dagster is available to those who have access [here](https://dagster.nabu.news).
The dev UI can be found [here](https://dev-dagster.nabu.news).

## Infrastructure
Infrastructure-as-code written with Pulumi in Python. Can reference `infrastructure/etl/__main__.py` for required
pieces.

Any updates to this repo's infrastructure code will automatically check and update the infrastructure in DigitalOcean.

"Manually" pushing any infrastructure updates can be previewed with `pulumi preview`, and actually pushing the changes 
live can be done with `pulumi up`. Both of these commands should be run from `infrastructure/etl/`.

This project cannot be rebuilt entirely from code, there are some pieces done manually. These pieces are:

- A DigitalOcean account
- An API token for Pulumi to interact with DigitalOcean, set to a stack's config (`pulumi config set digitalocean:token <token> --secret`)
- A Container Registry on Digital Ocean named `ptb` (TODO change to `nabu`)
- A CloudFlare account
- A domain name (currently assumed to be `nabu.news`, which seems like a reasonable assumption that won't change often)
- A CNAME record and A records for www.nabu.news, api.nabu.news, dagster.nabu.news, and their non-production equivalents (for example, dev-dagster.nabu.news)

Additionally, there are other CloudFlare bits that don't touch anything here (including the base www.nabu.news URL).
All the CloudFlare things are managed manually, but there is interplay between the infrastructure and Helm releases with the CloudFlare bits.

## Models
Pydantic/SQLModel models to have consistent data across pipelines and in the database. Auto-published on merge to
master to PyPi.

"Manually" updating ptbmodels requires the following:

- Bump the version in `ptbmodels/pyproject.toml`, line 3
- From `ptbmodels/`, run `poetry publish --build -u {username} -p {password}`

## API
TODO
### Run locally
todo

### Run remotely
todo

### Run tests
todo

### Container
todo

### Helm
todo


## Making changes

#### Need a new or changed table/column?

- Update relevant JSON files (like `etl/db/source.json` or `etl/db/rssfeed.json`)
- Update `ptbmodels/ptbmodels/models.py` as appropriate
- Bump the version in `ptbmodels/pyproject.toml`, line 3
- From `ptbmodels/`, run `poetry publish --build -u {username} -p {password}` (or let the CI/CD autopublish it)
- To use the updates in code: Bump the ptbmodels version in `etl/pyproject.toml`
- To propogate the changes to the DB: From `etl/db/` run `alembic revision --autogenerate -m "revision message"`
- Edit the newly created revision file in `etl/db/alembic/versions/` as needed
- TODO need to set up CD for Alembic revisions
- To propogate the Alembic changes, from `etl/db/alembic/` run `alembic upgrade head`
- Should be good to go!

#### Need to add a new source?

- TODO create an easy way to do this, like filling out a form
- update `etl/db/source.json` with a new entry
- Option A: PR, merge to master, and trigger the latest image, then run the source pipeline manually
- Option B: Manually insert the new source to the table via SQL console

*What about new rss feeds?*
Follow the same steps above for a new rss feed, making sure the source exists and referring to it.

#### Need to add a new DNS record?
todo

#### Need to update the CloudFlare Access controls?
todo