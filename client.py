import sys
import yaml
import time
import Tkinter
import threading

sys.path.append('gen-py')

from baltimore import Baltimore

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from Tkinter import *


def callback():
    print "click!"


class heartbeatThread(threading.Thread):
    def __init__(self, name='heartbeatThread'):
        self._stopevent = threading.Event()
        self._sleepperiod = 3.0
        threading.Thread.__init__(self, name=name)

    def run(self):
        while not self._stopevent.isSet():
            try:
                client.heartbeat()
                print 'Heartbeat: Server alive.'
                connectionStatusString.set('Connected')

            except Thrift.TException, tx:
                connectionStatusString.set('Not Connected')
                print 'Heartbeat: Unable to reach server.'

            root.update_idletasks()

            self._stopevent.wait(self._sleepperiod)

    def join(self, timeout=None):
        self._stopevent.set()
        threading.Thread.join(self, timeout)


def ampOn():
    client.amplifierOn()
    print 'Powering up amplifier.'


def ampOff():
    client.amplifierOff()
    print 'Powering down amplifier.'


def chimesOn():
    client.hourChimeOn()
    print 'Switching hourly chimes on.'


def chimesOff():
    client.hourChimeOff()
    print 'Switching hourly chimes off.'


def loadThreePeal():
    client.load('3peal.mp3')
    print 'Loading three peal bells.'


def loadWeddingPeal():
    client.load('wedding.mp3')
    print 'Loading wedding bells.'

def loadToll():
    client.load('toll.mp3')
    print 'Loading tolling bells.'


def playAudio():
    client.play()
    print 'Playing audio.'


def stopAudio():
    client.stop()
    print 'Stopping audio.'


def refreshStatus():
    ampState = client.amplifierState()
    chimeState = client.hourChimeState()
    ampStatusString.set('Amp On' if ampState else 'Amp Off')
    chimesStatusString.set('Chimes On' if chimeState else 'Chimes Off')
    root.update_idletasks()
    print 'Updating server status.'

# Load up the config
with open("config.yml", 'r') as configFile:
    conf = yaml.load(configFile)

connectedFlag = False

while (not connectedFlag):

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

        # Hooray!
        print 'Connected to server.'
        connectedFlag = True

    except Thrift.TException, tx:
        print '%s' % (tx.message)
        print 'Retrying in 10 seconds.'
        time.sleep(10)

# Made it here? We're connected! Awesome!

# Initialise the window root so we can line up some status strings

root = Tkinter.Tk()

w, h = root.winfo_screenwidth(), root.winfo_screenheight()
# root.overrideredirect(1)
root.geometry("%dx%d+0+0" % (w, h))

connectionStatusString = StringVar()
ampStatusString = StringVar()
chimesStatusString = StringVar()



# Fire off the heartbeat thread.

heartbeat = heartbeatThread()
heartbeat.start()

connectionStatusLabel = Label(root, textvariable=connectionStatusString)
connectionStatusLabel.pack()

ampStatusLabel = Label(root, textvariable=ampStatusString)
ampStatusLabel.pack()

chimesStatusLabel = Label(root, textvariable=chimesStatusString)
chimesStatusLabel.pack()

ampOnButton = Button(root, text="Amp On", command=ampOn)
ampOnButton.pack(fill=BOTH, expand=1)

ampOffButton = Button(root, text="Amp Off", command=ampOff)
ampOffButton.pack(fill=BOTH, expand=1)

# chimesOnButton = Button(root, text="Chimes On", command=chimesOn)
# chimesOnButton.pack(fill=BOTH, expand=1)

# chimesOffButton = Button(root, text="Chimes Off", command=chimesOff)
# chimesOffButton.pack(fill=BOTH, expand=1)

# ampRefreshButton = Button(root, text="Refresh Status", command=refreshStatus)
# ampRefreshButton.pack(fill=BOTH, expand=1)

threePealButton = Button(root, text="Load: Bells: Three Peal", command=loadThreePeal)
threePealButton.pack(fill=BOTH, expand=1)

weddingPealButton = Button(root, text="Load: Bells: Wedding", command=loadWeddingPeal)
weddingPealButton.pack(fill=BOTH, expand=1)

weddingPealButton = Button(root, text="Load: Bells: Toll", command=loadToll)
weddingPealButton.pack(fill=BOTH, expand=1)

playButton = Button(root, text="Play Audio", command=playAudio)
playButton.pack(fill=BOTH, expand=1)

stopButton = Button(root, text="Stop Audio", command=stopAudio)
stopButton.pack(fill=BOTH, expand=1)

# Get the status of things before we start
refreshStatus()

root.mainloop()
