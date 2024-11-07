docker pull --platform linux/amd64  "registry.suse.com/bci/bci-base:latest"
docker tag "registry.suse.com/bci/bci-base:latest" "containers.cisco.com/iam/bci-base:1.0.0-1"
docker push "containers.cisco.com/iam/bci-base:1.0.0-1"


docker pull --platform linux/amd64  "docker.io/qdrant/qdrant:v1.12.1"
docker tag "docker.io/qdrant/qdrant:v1.12.1" "containers.cisco.com/iam/qdrant:v1.12.1-1"
docker push "containers.cisco.com/iam/qdrant:v1.12.1-1"