
## zerorpc 使用

### 打印调用日志

打出所有的调用请求、参数和返回值，或写入日志

### 检测文件改变自动重启

autoreload,更新代码不用重启服务

使用werkzeug的run_with_reloader函数实现

### Usage
```

from utils import RPCBaseServer, run


class YourRPCModule(object):
    def hello(self, message):
        return "Hello %s" % message


class RPCServer(RPCBaseServer, YourRPCModule):
    pass


if __name__ == '__main__':
    run(YourRPCModule)

```


### Example

#### server.py

```
from utils import RPCBaseServer, run


class RPCModuleA(object):
    def show_a(self):
        return "This is RPCModuleA"


class RPCModuleB(object):
    def show_b(self):
        return "This is RPCModuleB"


class RPCModuleC(object):
    def hello(self, message):
        return "Hello %s" % message


class RPCServer(RPCBaseServer, RPCModuleA, RPCModuleB, RPCModuleC):
    pass


if __name__ == '__main__':
    run(RPCServer)

```

#### client.py

```
import zerorpc

c = zerorpc.Client()
c.connect("tcp://127.0.0.1:4242")
print c.hello("RPC")
print c.show_a()
print c.show_b()
```


启动server
```
$ python server.py 
 * Restarting with stat
```

在另外一个终端执行client.py
```
$ python client.py
Hello RPC
This is RPCModuleA
This is RPCModuleB
```

更新server.py文件后

```
$ python server.py 
 * Restarting with stat
('2018-07-17 01:33:53', 'hello', ('RPC',), {}, 'Hello RPC')
('2018-07-17 01:33:53', 'show_a', (), {}, 'This is RPCModuleA')
('2018-07-17 01:33:53', 'show_b', (), {}, 'This is RPCModuleB')
 * Detected change in '/home/root/rpc/server.py', reloading
 * Restarting with stat

```

