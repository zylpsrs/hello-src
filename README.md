# hello

  注意：k8s/deploy目录下hello、greeter清单文件，其调用greeter的服务时，其URL地址写全了，如greeter-grpc.hello.svc.cluster.local，故假设将其部署到hello命名空间，否则需修改部署清单文件。这里之所以将service名称写完整，其原因是当写短格式名称时，grpc调用服务时，其会进行DNS解析，而本人环境发现其过程相当慢，耗时5s以上。
