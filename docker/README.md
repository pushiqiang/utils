## 给正在运行的Docker容器动态绑定卷组（动态添加Volume）

需求：将物理机的目录`/tmp/test`挂载到正在运行的容器test（test容器id：955138b6c3ed）中的`/src`目录

1：chmod +x dynamic_mount_docker_volume

2: ./dynamic_mount_docker_volume 955138b6c3ed /tmp/test /src

