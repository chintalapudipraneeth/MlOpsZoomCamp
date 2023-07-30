#!/usr/bin/env python3
import os
import time

from kubernetes import utils, client, config


def main():
    integrations = os.getenv("INTEGRATION", "0")
    config.load_kube_config()
    k8s_client = client.ApiClient()
    api = client.AppsV1Api()
    yaml_dir = 'k8s/' if integrations == "0" else "integrations"
    yaml_file = f'{yaml_dir}/service-ml-deployment.yaml'
    name = "ml-service-neimv" if integrations == "0"\
        else "ml-fungus-integration-neimv"
    try:
        utils.create_from_directory(k8s_client, yaml_dir, verbose=True)
    except:
        try:
            api.delete_namespaced_deployment(
                name=name,
                namespace="default",
                body=client.V1DeleteOptions(
                    propagation_policy="Foreground", grace_period_seconds=5
                ),
            )
            print(f"\n[INFO] deployment `{name}` deleted.")
            utils.create_from_yaml(k8s_client, yaml_file, verbose=True)
        except:
            time.sleep(90)
            utils.create_from_yaml(k8s_client, yaml_file, verbose=True)


if __name__ == "__main__":
    main()
