IMAGE_VERSION ?= v1
#IMG ?= registry.ocp.zyl.io:5000/hello:$(IMAGE_VERSION)
IMG ?= core.apps.ocp.zyl.io/hello/hello:$(IMAGE_VERSION)

BUILDAH_FORMAT ?= docker

all:
	podman build -t $(IMG) .
	podman push --authfile ~/pull-secret-2.json $(IMG)
