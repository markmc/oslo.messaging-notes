

import eventlet

eventlet.monkey_patch(os=False)

import socket

from oslo.config import cfg

from oslo import messaging

_opts = [
    cfg.StrOpt('host', default=socket.gethostname()),
]

CONF = cfg.CONF
CONF.register_opts(_opts)

class Server(object):

    def __init__(self, transport):
        self.target = messaging.Target(topic='testtopic',
                                       server=transport.conf.host,
                                       version='2.5')
        self._server = messaging.get_rpc_server(transport,
                                                self.target,
                                                [self],
                                                executor='eventlet')
        super(Server, self).__init__()

    def start(self):
        self._server.start()

    def test(self, ctxt, arg):
        return arg

transport = messaging.get_transport(CONF, 'fake:///testexchange')

server = Server(transport)
server.start()


class Client(object):

    def __init__(self, transport):
        target = messaging.Target(topic='testtopic', version='2.0')
        self._client = messaging.RPCClient(transport, target)
        super(Client, self).__init__()

    def test(self, ctxt, arg):
        cctxt = self._client.prepare(version='2.5')
        return cctxt.call(ctxt, 'test', arg=arg)


client = Client(transport)
print client.test({'c': 'b'}, 'foo')
