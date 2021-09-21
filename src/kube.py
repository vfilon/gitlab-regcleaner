import logging
from kubernetes import client, config


def parse_kube(config_file: str, hisory_leghth: int, namespace: str) -> list:
    raw_data = get_images_from_namespace(config_file, namespace)
    image_base = list()
    for app in raw_data:
        image_buffer = list()
        raw_data[app] = {int(i['revision']): i['containers'] for i in raw_data[app]}
        for revision in sorted(raw_data[app].keys())[::-1]:
            if len(image_buffer) < hisory_leghth:
                if raw_data[app][revision] not in image_buffer:
                    image_buffer.append(raw_data[app][revision])
            else:
                break
        for image in image_buffer:
            image_base += image
    return image_base


def get_images_from_namespace(config_file: str, namespace: str) -> dict:
    output = dict()
    config.load_kube_config(config_file=config_file)
    logging.info('Successfully connected to cluster')
    deploy_api = client.AppsV1Api()
    repl = deploy_api.list_namespaced_replica_set(namespace=namespace)
    for replica_set in repl.items:
        namespace = replica_set.metadata.namespace
        if 'app' not in replica_set.metadata.labels:
            app_name = f'{replica_set.spec.template.spec.service_account}-{namespace}'
        else:
            app_name = f'{replica_set.metadata.labels["app"]}-{namespace}'
        if app_name not in output:
            output[app_name] = []
        app_record = dict()
        if 'deployment.kubernetes.io/revision' in replica_set.metadata.annotations:
            app_record['revision'] = replica_set.metadata.annotations['deployment.kubernetes.io/revision']
        app_record['containers'] = list()
        for container in replica_set.spec.template.spec.containers:
            app_record['containers'].append(container.image)
        output[app_name].append(app_record)
    return output
