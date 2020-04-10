IMAGE_VERSION ?= v3
#IMG ?= registry.ocp.zyl.io:5000/greeter:$(IMAGE_VERSION)
IMG ?= core.apps.ocp.zyl.io/hello/greeter:$(IMAGE_VERSION)

BUILDAH_FORMAT ?= docker

all:
	podman build --format docker -t $(IMG) .
	podman push --tls-verify=false --authfile ~/pull-secret-2.json $(IMG)
