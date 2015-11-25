import sys, pygame
sys.path.append('gen-py')

from baltimore import Baltimore

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from threading import Thread

# This is where we respond to things.

class BaltimoreHandler:

    def __init__(self):
        self.log = {}

    def heartbeat(self):
        print 'Heartbeat received from client!'

    def amplifierState(self):
        print 'Amplifier state request. Replied with: ' + ('On' if amplifierPower else 'Off')
        return amplifierPower

    def hourChimeState(self):
        print 'Hourly chime state request. Replied with: ' + ('On' if hourChime else 'Off')
        return hourChime

    # Load and play the given filename
    def play(self, filename):
        print 'Playing audio file: ' + filename
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

    # Fade the audio out.
    def stop(self):
        print 'Stopping current audio.'
        pygame.mixer.music.fadeout(3000)


# Here are our threads!

# This is the server thread

def serverThread():
    print 'Server initialising...'
    server = thriftServer.serve()
    server.stop()

# Initialise all the Thrift stuff

handler = BaltimoreHandler()
processor = Baltimore.Processor(handler)
transport = TSocket.TServerSocket(port=9090)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

thriftServer = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

# Off we go!

# This is so the loop knows to keep going
serverAlive = True;

# This should be the default state of affairs.
hourChime = False;
amplifierPower = False;

print 'Good morning Baltimore!'

# Initialise the mixer.
pygame.mixer.init()

# Begin threads!
# server = Thread(target = serverThread)

# server.start();

thriftServer.serve()

print 'Goodbye.'
