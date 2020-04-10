IMAGE_VERSION ?= v3
#IMG ?= registry.ocp.zyl.io:5000/greeter:$(IMAGE_VERSION)
IMG ?= core.apps.ocp.zyl.io/hello/greeter:$(IMAGE_VERSION)

all:
	podman build -t $(IMG) .
	podman push --authfile ~/pull-secret-2.json $(IMG)
