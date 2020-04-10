这里将单体程序改造为3个独立的flask微服务：
 1. hello：前端服务，接收/?helloTo=<value>参数，而后返回欢迎信息给用户
 2. publisher：供hello程序调用，其调用greete服务，而后将其返回的欢迎信息发布到终端并返回给hello
 3. greete：对publisher程序传递过来的信息做格式化处理，添加欢迎信息
