# pop the bubble news
A simple RSS feed news dashboard organized into 5 lanes to get the full political spectrum of news in the U.S.

### build
`npm run build` to update JS/HTML/CSS bundles.

### deploy
Simply push/merge to `main` and the CD will deploy it.

### Relevant links
[Cloudflare](https://dash.cloudflare.com/35d8fc094133c9d73ed3fba3fbeb5865/popthebubble.news/analytics/traffic) for DNS and more
[DigitalOcean](https://cloud.digitalocean.com/apps/20a66c8d-5993-4d99-9a78-9acd0b5787f9/deployments?i=589e61) app platform for deployment

# ETL

### Run locally
First set up the db. Raaid, you have a shortcut set up called `pgrun`, which is
actually: `docker run --rm --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_HOST_AUTH_METHOD=trust 
-p 127.0.0.1:5432:5432/tcp postgres`

Then run `init_db.py` with the correct credentials for the local PostgreSQL instance.

Next, From the project root directory, run `dagit -f etl/repositories.py` in one terminal, then run 
`dagster-daemon run` in another. Go to `http://127.0.0.1:3000` in your browser. Use the UI to turn on schedules
and sensors or manually kick off jobs.