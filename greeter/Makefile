IMAGE_VERSION ?= v3.2
IMG ?= core.apps.ocp.zyl.io/hello/greeter:$(IMAGE_VERSION)

BUILDAH_FORMAT ?= docker

all:
	podman build --no-cache --format docker -t $(IMG) .
	podman push --tls-verify=false --authfile ~/pull-secret-2.json $(IMG)
