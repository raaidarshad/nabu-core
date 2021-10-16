"""A DigitalOcean Python Pulumi program"""

import pulumi_digitalocean as do


region = "nyc3"

# create a db cluster, dbs, and users
db_cluster = do.DatabaseCluster("postgres",
                                engine="pg",
                                node_count=1,
                                region=region,
                                size="db-s-1vcpu-1gb",
                                version="13")

db_dagster = do.DatabaseDb("db_dagster", cluster_id=db_cluster.id)
db_etl = do.DatabaseDb("db_etl", cluster_id=db_cluster.id)
db_user_dagster = do.DatabaseUser("db_user_dagster", cluster_id=db_cluster.id)
db_user_etl = do.DatabaseUser("db_user_etl", cluster_id=db_cluster.id)
db_user_monitor = do.DatabaseUser("db_user_monitor", cluster_id=db_cluster.id)

# create db conn strings for each user to the right db
db_conn_etl = f"postgresql://{db_user_etl.name}:{db_user_etl.password}@{db_cluster.private_host}:{db_cluster.port}/{db_etl.name}"
db_conn_dagster = f"postgresql://{db_user_dagster.name}:{db_user_dagster.password}@{db_cluster.private_host}:{db_cluster.port}/{db_dagster.name}"
db_conn_monitor = f"postgresql://{db_user_monitor.name}:{db_user_monitor.password}@{db_cluster.private_host}:{db_cluster.port}/{db_etl.name}"

# create a k8s cluster and node pools
k8s = do.KubernetesCluster("main-k8s",
                           region=region,
                           version="1.21.3-do.0",
                           node_pool=do.KubernetesClusterNodePoolArgs(
                               name="main-pool",
                               size="s-1vcpu-2gb",
                               node_count=2
                           ))

# put db credentials in secret in cluster
# Secret("etl-db-secret",args=SecretInitArgs(string_data={"DB_CONNECTION_STRING": db_conn_etl}))
