IMAGE_VERSION ?= v3.2
#IMG ?= registry.ocp.zyl.io:5000/publisher:$(IMAGE_VERSION)
IMG ?= core.apps.ocp.zyl.io/hello/publisher:$(IMAGE_VERSION)

BUILDAH_FORMAT ?= docker

all:
	podman build --no-cache --format docker -t $(IMG) .
	podman push --tls-verify=false --authfile ~/pull-secret-2.json $(IMG)
