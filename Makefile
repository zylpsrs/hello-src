IMAGE_VERSION ?= v2.0
#IMG ?= registry.ocp.zyl.io:5000/hello:$(IMAGE_VERSION)
IMG ?= core.apps.ocp.zyl.io/hello/hello:$(IMAGE_VERSION)

BUILDAH_FORMAT ?= docker

all:
	podman build --format docker -t $(IMG) .
	podman push --tls-verify=false --authfile ~/pull-secret-2.json $(IMG)
