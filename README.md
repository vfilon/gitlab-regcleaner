# GITLAB REGISTRY CLEANER

Used code from https://github.com/nzelepukin/kube_gittlab_regcleaner

### Decription
Do you have a Kubernetes cluster and GitLab registry full of unused images? Delete unused images from GitLab and keep images used by apps in Kubernetes.

### Resources
 * `CPU_REQUEST = 0.05`
 * `RAM_REQUEST = 64` Mb
 * `CPU_LIMIT = 0.5`
 * `RAM_LIMIT = 128` Mb

### Local Run
 * `python3.9 start.py`
 
### Build
  * `docker build -t gitlab-regcleaner .`
 
### Environment variables
 * `CI_API_V4_URL=https://gitlab.example.com/api/v4` - The GitLab API v4 root URL
 * `CI_PROJECT_ID=100` - The ID of the current project. This ID is unique across all projects on the GitLab instance
 * `GIT_TOKEN=asdasdasd` - GitLab token (api, read_repository, read_registry)
 * `KUBECONFIG=~/.kube/config` - kubernetes config path (recommended permissions -  get, list, watch)
 * `KUBE_NAMESPACE` - The namespace associated with the project
 * `KUBE_HISTORY=5` - How much images from rollout history you want to keep.
 * `REMOVE_UNUSED_TAGS=false` - false - inspect,  true - remove unused images.
 * `GITLAB_INCLUDE_TAGS` - Regexp mask for the tag included in the deletion
 * `GITLAB_EXCLUDE_TAGS` - Regexp mask for the tag excluded from deletion