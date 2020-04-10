IMAGE_VERSION ?= v2
IMG ?= registry.ocp.zyl.io:5000/greeter:$(IMAGE_VERSION)

all:
	podman build -t $(IMG) .
	podman push --authfile ~/pull-secret-2.json $(IMG)
