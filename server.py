import sys
sys.path.append('gen-py')

from baltimore import Baltimore

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class BaltimoreHandler:
  def __init__(self):
    self.log = {}

  def heartbeat(self):
    print 'ping()'

handler = BaltimoreHandler()
processor = Baltimore.Processor(handler)
transport = TSocket.TServerSocket(port=9090)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

print 'Starting the server...'
server.serve()
print 'done.'
