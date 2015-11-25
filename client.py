import sys, yaml, time
sys.path.append('gen-py')

from baltimore import Baltimore

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# Load up the config
with open("config.yml", 'r') as configFile:
    conf = yaml.load(configFile)

try:

    # Make socket
    transport = TSocket.TSocket(conf['server'], 9090)

    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)

    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    # Create a client to use the protocol encoder
    client = Baltimore.Client(protocol)

    # Connect!
    transport.open()

    client.heartbeat()
    print 'Sent heartbeat.'

    amplifierState = client.amplifierState()
    print 'Amplifier is: ' + ('On' if amplifierState else 'Off')

    hourChimeState = client.hourChimeState()
    print 'Hourly chimes are: ' + ('On' if hourChimeState else 'Off')

    while True:

        fileName = raw_input("What to play?")

        # BELLS!
        client.play(fileName)

        raw_input("Stop?")

        # Stop!
        client.stop()

    # Close!
    transport.close()

except Thrift.TException, tx:
    print '%s' % (tx.message)
