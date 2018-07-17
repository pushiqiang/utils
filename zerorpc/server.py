# -*- encoding: utf-8 -*-

import datetime

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

