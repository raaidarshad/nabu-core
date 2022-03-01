"""A DigitalOcean Python Pulumi program"""

from pulumi import Config, Output, ResourceOptions
import pulumi_digitalocean as do
from pulumi_kubernetes import Provider, ProviderArgs
from pulumi_kubernetes.core.v1 import Secret, SecretInitArgs
from pulumi_kubernetes.meta.v1 import ObjectMetaArgs
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs

region = "nyc3"
config = Config()

# create bucket
do_provider = do.Provider("do-provider",
                          args=do.ProviderArgs(
                              spaces_access_id=config.require_secret("spaces_access"),
                              spaces_secret_key=config.require_secret("spaces_secret")
                          ))
do_opts = ResourceOptions(provider=do_provider)

bucket_name = "ptb-bucket"
space = do.SpacesBucket("ptb-bucket",
                        acl="public-read",
                        name=bucket_name,
                        region=region,
                        opts=do_opts
                        )

# create a db cluster, dbs, and users
db_cluster = do.DatabaseCluster("ptb-postgres",
                                engine="pg",
                                node_count=1,
                                region=region,
                                size="db-s-1vcpu-2gb",
                                version="13")

db_dagster = do.DatabaseDb("db_dagster", cluster_id=db_cluster.id)
db_etl = do.DatabaseDb("db_etl", cluster_id=db_cluster.id)
db_user_dagster = do.DatabaseUser("db_user_dagster", cluster_id=db_cluster.id)
db_user_etl = do.DatabaseUser("db_user_etl", cluster_id=db_cluster.id)
db_user_monitor = do.DatabaseUser("db_user_monitor", cluster_id=db_cluster.id)

# create db conn strings for each user to the right db
db_cluster_port = db_cluster.port.apply(lambda port: str(port))
db_conn_etl = Output.concat("postgresql://", db_user_etl.name, ":", db_user_etl.password, "@", db_cluster.private_host,
                            ":", db_cluster_port, "/", db_etl.name)
# db_conn_monitor = f"postgresql://{db_user_monitor.name}:{db_user_monitor.password}@{db_cluster.private_host}:{db_cluster.port}/{db_etl.name}"

# create a k8s cluster and node pools
k8s = do.KubernetesCluster("ptb-k8s",
                           region=region,
                           version="1.21.5-do.0",
                           node_pool=do.KubernetesClusterNodePoolArgs(
                               name="main-pool",
                               size="s-2vcpu-4gb",
                               min_nodes=2,
                               max_nodes=3,
                               auto_scale=True
                           ))

kube_provider = Provider("ptb-k8s-provider", args=ProviderArgs(kubeconfig=k8s.kube_configs[0].raw_config))
opts = ResourceOptions(provider=kube_provider)

# put db credentials in secret in cluster
etl_secret_name = "etl-db-secret"
etl_secret = Secret("etl-db-secret",
                    args=SecretInitArgs(
                        string_data={
                            "DB_CONNECTION_STRING": db_conn_etl,
                            "SPACES_REGION": region,
                            "SPACES_ENDPOINT": f"https://{region}.digitaloceanspaces.com",
                            "SPACES_KEY": config.require_secret("spaces_access"),
                            "SPACES_SECRET": config.require_secret("spaces_secret"),
                            "SPACES_BUCKET_NAME": bucket_name
                        },
                        metadata=ObjectMetaArgs(name=etl_secret_name)
                    ), opts=opts)
dagster_secret_name = "dagster-db-secret"
dagster_secret = Secret("dagster-postgresql-secret",
                        args=SecretInitArgs(
                            string_data={"postgresql-password": db_user_dagster.password},
                            metadata=ObjectMetaArgs(name=dagster_secret_name)
                        ), opts=opts)

# put docker credentials in secret in cluster
docker_secret_name = "docker-secret"
ptb_registry = do.ContainerRegistryDockerCredentials("ptb-registry", registry_name="ptb")
docker_secret = Secret("docker-secret",
                       args=SecretInitArgs(
                           type="kubernetes.io/dockerconfigjson",
                           string_data={".dockerconfigjson": ptb_registry.docker_credentials},
                           metadata=ObjectMetaArgs(name=docker_secret_name)
                       ), opts=opts)

# helm

# nginx ingress controller
nginx_release_args = ReleaseArgs(
    name="nginx-ingress",
    chart="ingress-nginx",
    repository_opts=RepositoryOptsArgs(repo="https://kubernetes.github.io/ingress-nginx"),
    version="4.0.17"
)

nginx_release = Release("nginx-ingress-controller", args=nginx_release_args, opts=opts)

# dagster
release_args = ReleaseArgs(
    name="dagster-etl",
    chart="dagster",
    repository_opts=RepositoryOptsArgs(
        repo="https://dagster-io.github.io/helm"
    ),
    version="0.14.2",
    values={
        "global": {"postgresqlSecretName": dagster_secret_name},
        "generatePostgresqlPasswordSecret": False,
        "imagePullSecrets": [{"name": docker_secret_name}],
        "dagster-user-deployments": {
            "deployments": [
                {
                    "name": "etl",
                    "image": {
                        "repository": "registry.digitalocean.com/ptb/etl",
                        "tag": config.require("tag"),
                        "pullPolicy": "Always"
                    },
                    "dagsterApiGrpcArgs": ["-f", "etl/repositories.py"],
                    "port": 3030,
                    "envSecrets": [{"name": etl_secret_name}]
                }
            ],
            "imagePullSecrets": [{"name": docker_secret_name}]
        },
        "runLauncher": {
            "type": "K8sRunLauncher",
            "config": {
                "k8sRunLauncher": {"envSecrets": [{"name": etl_secret_name}]}
            }
        },
        "postgresql": {
            "enabled": False,
            "postgresqlHost": db_cluster.private_host,
            "postgresqlUsername": db_user_dagster.name,
            "postgresqlPassword": db_user_dagster.password,
            "postgresqlDatabase": db_dagster.name,
            "service": {
                "port": db_cluster.port
            }
        },
        "ingress": {
            "enabled": True,
            "ingressClassName": "nginx",
            "readOnlyDagit": {
                "host": "dagster.nabu.news",
                "path": "/",
                "pathType": "Prefix"
            }
        }
    }
)

release = Release("ptb", args=release_args, opts=opts)
