# Hello

这里将单体程序改造为3个独立的flask微服务：

 1. hello：前端服务，接收/?helloTo=<value>参数，调用publisher将信息发送出去，调用greeter获取欢迎信息，而后将信息返回给用户
 2. publisher：供hello程序调用，其调用greeter服务，而后将其返回的欢迎信息发布到终端并返回给hello
 3. greeter：对传递过来的信息做格式化处理，添加欢迎信息
