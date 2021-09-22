import os
import re
import time
import logging
from src.async_gitlab import get_registry, del_registry_tags
from src.kube import parse_kube


def show_stat(kube_image_base: set, gitlab_image_base: set, kube_history: int) -> None:
    """Image sorting statistics."""

    text = f'''
    GitLab registry images - {len(gitlab_image_base)}
    Images from kubernetes replicaset rollout history({kube_history} last images) - {len(kube_image_base)}
    Images from kubernetes, found in GitLab - {len(kube_image_base.intersection(gitlab_image_base))}
    Images from kubernetes, not found in GitLab - {len(kube_image_base.difference(gitlab_image_base))}
    Removal candidates - {len(gitlab_image_base.difference(kube_image_base))}
    '''
    logging.info(text)


def show_del_stat(del_image_base: list) -> None:
    """ Minimal deletion statistics """
    output = {'deleted': [], 'forbidden': []}
    for each in del_image_base:
        if '--=Cant delete=--' in each:
            output['forbidden'].append(each)
        else:
            output['deleted'].append(each)
    text = f'''
    Tags deleted - {len(output['deleted'])}
    Cant delete - {len(output['forbidden'])}
    '''
    logging.info(text)


class Timer:
    def __init__(self):
        self.start = time.time()

    def stop(self):
        logging.info(f' ---- Runtime {int(time.time()-self.start)} sec ---- ')


timer = Timer()

# Environment variables

gitlab_api_v4_url = os.environ['CI_API_V4_URL']
gitlab_project_id = int(os.environ['CI_PROJECT_ID'])
gitlab_token = os.environ['GITLAB_REGCLEAN_TOKEN']
gitlab_exclude_tags = os.getenv('GITLAB_EXCLUDE_TAGS', r'')  # ^\d+\.\d+\.\d+$
gitlab_include_tags = os.getenv('GITLAB_INCLUDE_TAGS', r'')  # ^[a-f0-9]{8}$
gitlab_remove_unused_tags = os.getenv("GITLAB_REMOVE_UNUSED_TAGS", 'False').lower() in ('true', '1', 't')

kube_config = os.environ['KUBECONFIG']
kube_namespace = os.environ['KUBE_NAMESPACE']
kube_history = int(os.getenv('KUBE_HISTORY', '5'))

remove_unused_tags = os.getenv("REMOVE_UNUSED_TAGS", 'False').lower() in ('true', '1', 't')
#
headers = {"PRIVATE-TOKEN": gitlab_token}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info(f'Working with {gitlab_api_v4_url}')

gitlab_image_base = get_registry(gitlab_api_v4_url, headers, gitlab_project_id, 5)
if gitlab_include_tags:
    re_include = re.compile(gitlab_include_tags)
    gitlab_image_base = [image for image in gitlab_image_base if re_include.search(image['name'])]
if gitlab_exclude_tags:
    re_exclude = re.compile(gitlab_exclude_tags)
    gitlab_image_base = [image for image in gitlab_image_base if not re_exclude.search(image['name'])]

gitlab_image_base = {image['location']: image['del_url'] for image in gitlab_image_base}

logging.info(f'Successfully finish with {gitlab_api_v4_url}')

kube_image_base = parse_kube(kube_config, kube_history, namespace=kube_namespace)

kube_image_base = set(kube_image_base)
show_stat(kube_image_base, set(gitlab_image_base.keys()), kube_history)

del_candidates = list()
del_candidates_tags = list()
for tag in set(gitlab_image_base.keys()).difference(kube_image_base):
    del_candidates.append(gitlab_image_base[tag])
    del_candidates_tags.append(tag)

logging.info(f'Got {len(del_candidates_tags)} candidates to delete:')
logging.info('\n'.join(del_candidates_tags))

if gitlab_remove_unused_tags:
    logging.info(f'Deleting images')
    del_output = del_registry_tags(del_candidates, headers, 5)
    show_del_stat(del_output)

timer.stop()
