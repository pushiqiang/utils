## 给正在运行的Docker容器动态绑定卷组（动态添加Volume）

需求：将物理机的目录`/tmp/test`挂载到正在运行的容器test（test容器id：955138b6c3ed）中的`/src`目录


```
$ chmod +x dynamic_mount_docker_volume
$ docker run --rm -v /usr/local/bin:/target jpetazzo/nsenter
$ ./dynamic_mount_docker_volume 955138b6c3ed /tmp/test /src

```

命令说明：

1. 给dynamic_mount_docker_volume赋可执行权限

2. 下载nsenter 参见：https://github.com/jpetazzo/nsenter

3. 执行脚本给运行的容器挂载卷


## subprocess.Popen 实时获取docker events事件
