# -*- encoding: utf-8 -*-

import datetime
import zerorpc

from functools import partial
from werkzeug._reloader import run_with_reloader


def run_server(rpc_class, host, port):
    server = zerorpc.Server(rpc_class())
    server.bind('tcp://{}:{}'.format(host, port))
    server.run()


def run(rpc_class, host='0.0.0.0', port=4242, autoreload=True):
    """
    Start a rpc server

    :param rpc_class: The rpc service module
    :param host: The host to bind to, for example ``'localhost'``
    :param port: The port for the server.  eg: ``4242``
    :param autoreload: should the server automatically restart the python process if modules were changed?
    """
    main_func = partial(run_server, rpc_class, host, port)
    if autoreload:
        run_with_reloader(main_func)
    else:
        main_func()


class FuncWrapper(object):

    def __init__(self, func):
        self.func = func
        
    def __call__(self, *args, **kwargs):
        result = self.func(*args, **kwargs)
        # print log
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
              self.func.__name__, args, kwargs, result)
        return result

    @property    
    def __name__(self):
        return self.func.__name__


class RPCBaseServer(object):
    """
    RPC service base class

    The final rpc service class must inherit from this class
    """
    def __init__(self):
        super(RPCBaseServer, self).__init__()
        for func_name in dir(self):
            if not func_name.startswith('_'):
                func = getattr(self, func_name)
                if callable(func):
                    setattr(self, func_name, FuncWrapper(func))

