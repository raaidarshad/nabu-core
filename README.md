# Nabu
This repo contains all the code to run the data processing side of Nabu.

[API Base URL](https://api.nabu.news)
[Dagit UI](https://dagster.nabu.news) - Note that this is not publicly accessible

[Website](https://www.nabu.news)
[Website code repository](https://github.com/raaidarshad/nabu-website)
[Firefox Extension](https://addons.mozilla.org/en-US/firefox/addon/nabu/)
[Chrome Extension](https://chrome.google.com/webstore/detail/nabu/bgmcmbjhfdnfaplfiiphlefclhhhnajb)
[Extension code repository](https://github.com/raaidarshad/nabu-browser-extension)

Note: Many things referenced here and in the code may have the acronym "ptb" as a part of them. This is because this
project used to be named "pop the bubble".

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

### Run tests
We use pytest.

For unit tests: `pytest etl/tests/unit`
For integration tests (needs a running Postgres instance, see instructions above for that): `pytest etl/tests/it`

### Container
The Docker image is automatically tested and updated from GitHub actions whenever there is a code change. The registry
is located at registry.digitalocean.com/ptb/etl

### Helm
As mentioned above, we use the [official Dagster Helm chart](https://github.com/dagster-io/dagster/tree/master/helm/dagster) to deploy our instance.

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
You need to point the API to a database with a schema as defined in `ptbmodels`. Do so by providing an environment
variable named `DB_CONNECTION_STRING`. The following is an example of running the API server locally from api/api:
`DB_CONNECTION_STRING=my_fake_conn_string uvicorn main:app --reload`

### Run tests
We use pytest.

For all tests: `pytest api/tests`

### Container
The Docker image is automatically tested and updated from GitHub actions whenever there is a code change. The registry
is located at registry.digitalocean.com/ptb/api

### Helm
We have a straightforward Helm chart defined at `api/helm/nabu-api` in this project. It is not published to a Helm
repository anywhere, as the only place it is referred to and released from is also within this project, therefore we
save ourselves the burden of setting up a Helm repository and just point to it locally.

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

- Navigate to the [CloudFlare dashboard](https://dash.cloudflare.com), go to the nabu.news section, and click DNS.
- Click the "add record" button and do what you need!

#### Need to update the CloudFlare Access controls?

- Navigate to the [CloudFlare dashboard](https://dash.cloudflare.com), go to the nabu.news section, and click Access.
- Click the "launch zero trust" button.
- Go to Access -> Applications, and click on the edit button for the target application.
- Make whatever policy, rule, auth, etc. changes are needed.

#### Need a DB user?

- In infrastructure/etl/__main__.py, in the `DATABASE` section, create a new db user.
- You can follow the template of other users: `db_user_new = do.DatabaseUser("db_user_new", cluster_id=db_cluster.id)`
- If needed, create a connection string to store in a k8s secret
- After running `pulumi up` for the desired environment, you will need to [specifically grant](https://www.postgresql.org/docs/13/sql-grant.html) the new user the necessary permissions
- Assuming the user has been granted their necessary permissions, you should be all set!
