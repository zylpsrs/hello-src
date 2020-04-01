IMAGE_VERSION ?= v1
IMG ?= registry.ocp.zyl.io:5000/hello:$(IMAGE_VERSION)

all:
	podman build -t $(IMG) .
	podman push --authfile ~/pull-secret-2.json $(IMG)