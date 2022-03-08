"""A DigitalOcean Python Pulumi program"""

from pulumi import Config, Output, ResourceOptions, get_stack
import pulumi_digitalocean as do
from pulumi_kubernetes import Provider, ProviderArgs
from pulumi_kubernetes.core.v1 import Namespace, Secret, SecretInitArgs
from pulumi_kubernetes.meta.v1 import ObjectMetaArgs
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs

region = "nyc3"
config = Config()
stack = get_stack()

### UTILS ###


def format_name(initial_name: str) -> str:
    if stack != "prod":
        # if not prod, we want to be explicit about what env we're in
        out_name = f"{stack}-{initial_name}"
    else:
        # just use the provided name for prod
        out_name = initial_name
    return out_name


###############
### STORAGE ###
###############


# need to explicitly pass spaces access information, so we need a specific provider
do_provider = do.Provider("do-provider",
                          args=do.ProviderArgs(
                              spaces_access_id=config.require_secret("spaces_access"),
                              spaces_secret_key=config.require_secret("spaces_secret")
                          ))
do_opts = ResourceOptions(provider=do_provider)

# create bucket
bucket_name = format_name("ptb-bucket")
space = do.SpacesBucket(bucket_name,
                        acl="public-read",
                        name=bucket_name,
                        region=region,
                        opts=do_opts
                        )

################
### DATABASE ###
################

# create a db cluster, dbs, and users
db_cluster = do.DatabaseCluster(format_name("ptb-postgres"),
                                engine="pg",
                                node_count=config.require_int("db_node_count"),
                                region=region,
                                size=config.require("db_size"),
                                version="13")

db_dagster = do.DatabaseDb("db_dagster", cluster_id=db_cluster.id)
db_etl = do.DatabaseDb("db_etl", cluster_id=db_cluster.id)
db_user_dagster = do.DatabaseUser("db_user_dagster", cluster_id=db_cluster.id)
db_user_etl = do.DatabaseUser("db_user_etl", cluster_id=db_cluster.id)
db_user_monitor = do.DatabaseUser("db_user_monitor", cluster_id=db_cluster.id)
db_user_api = do.DatabaseUser("db_user_api", cluster_id=db_cluster.id)

# create db conn strings for each user to the right db
db_cluster_port = db_cluster.port.apply(lambda port: str(port))
db_conn_etl = Output.concat("postgresql://", db_user_etl.name, ":", db_user_etl.password, "@", db_cluster.private_host,
                            ":", db_cluster_port, "/", db_etl.name)
db_conn_api = Output.concat("postgresql://", db_user_api.name, ":", db_user_api.password, "@", db_cluster.private_host,
                            ":", db_cluster_port, "/", db_etl.name)


##################
### KUBERNETES ###
##################

# create a k8s cluster and node pools
k8s = do.KubernetesCluster(format_name("ptb-k8s"),
                           region=region,
                           version=config.require("k8s_version"),
                           node_pool=do.KubernetesClusterNodePoolArgs(
                               name="main-pool",
                               size=config.require("k8s_size"),
                               min_nodes=config.require_int("k8s_min_nodes"),
                               max_nodes=config.require_int("k8s_max_nodes"),
                               auto_scale=True
                           ),
                           opts=ResourceOptions(depends_on=[db_cluster, db_user_etl, db_user_api]))

kube_provider = Provider(format_name("ptb-k8s-provider"), args=ProviderArgs(kubeconfig=k8s.kube_configs[0].raw_config))
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
api_secret_name = "api-db-secret"
api_secret_key = "DB_CONNECTION_STRING"
api_secret = Secret("api-db-secret",
                    args=SecretInitArgs(
                        string_data={
                            api_secret_key: db_conn_api
                        },
                        metadata=ObjectMetaArgs(name=api_secret_name)
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

#####################
### HELM RELEASES ###
#####################

# nginx ingress controller
nginx_release_args = ReleaseArgs(
    name="nginx-ingress",
    chart="ingress-nginx",
    repository_opts=RepositoryOptsArgs(repo="https://kubernetes.github.io/ingress-nginx"),
    version="4.0.17"
)

nginx_release = Release("nginx-ingress-controller",
                        args=nginx_release_args,
                        opts=ResourceOptions(provider=kube_provider, depends_on=k8s))

# cert manager

# create a namespace before the helm release
cert_manager_ns = Namespace("cert-manager-ns", opts=ResourceOptions(provider=kube_provider, depends_on=k8s))


cert_manager_release_args = ReleaseArgs(
    name="cert-manager",
    chart="cert-manager",
    repository_opts=RepositoryOptsArgs(repo="https://charts.jetstack.io"),
    version="1.7.1",
    values={"installCRDs": True},
    namespace=cert_manager_ns.id
)

cert_manager_release = Release("cert-manager",
                               args=cert_manager_release_args,
                               opts=ResourceOptions(provider=kube_provider, depends_on=cert_manager_ns))

# issuer

issuer_secret = "letsencrypt-key"
issuer_name = "letsencrypt"

issuer_release_args = ReleaseArgs(
    name="cert-issuer",
    chart="./helm_charts/issuer",
    version="0.1.0",
    values={
        "name": issuer_name,
        "secretName": issuer_secret
    }
)

issuer_release = Release("cert-issuer",
                         args=issuer_release_args,
                         opts=ResourceOptions(provider=kube_provider, depends_on=[cert_manager_release, nginx_release]))

# dagster
dagster_release_args = ReleaseArgs(
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
                        "tag": config.require("dagster_tag"),
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
            "annotations": {"cert-manager.io/cluster-issuer": issuer_name},
            "ingressClassName": "nginx",
            "dagit": {
                "host": format_name("dagster.nabu.news"),
                "path": "/",
                "pathType": "Prefix",
                "tls": {
                    "enabled": True,
                    "secretName": issuer_secret
                }
            }
        }
    }
)

dagster_release = Release("ptb",
                          args=dagster_release_args,
                          opts=ResourceOptions(provider=kube_provider,
                                               depends_on=[issuer_release, etl_secret, db_user_dagster]))

# api server
api_host = format_name("api.nabu.news")

api_release_args = ReleaseArgs(
    name="api-server",
    chart="../../api/helm/nabu-api",
    version="0.1.0",
    values={
        "server": {
            "dbSecret": {
                "name": api_secret_name,
                "key": api_secret_key
            }
        },
        "image": {
            "version": config.require("api_tag")
        },
        "imagePullSecrets": [{"name": docker_secret_name}],
        "ingress": {
            "annotations": {"cert-manager.io/cluster-issuer": issuer_name},
            "hosts": [{
                "host": api_host,
                "paths": [{
                    "pathType": "Prefix",
                    "path": "/"
                }]
            }],
            "tls": [{
                "secretName": issuer_secret,
                "hosts": [api_host]
            }]
        }
    }
)

api_release = Release("api-server",
                      args=api_release_args,
                      opts=ResourceOptions(provider=kube_provider,
                                           depends_on=[issuer_release, api_secret, db_user_api]))
