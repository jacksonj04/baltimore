import sys
import pygame
import time
import threading

sys.path.append('gen-py')

from baltimore import Baltimore

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from datetime import datetime

from gpiozero import Energenie

# Variables!
fadeinDelay = 3
fadeoutDelay = 3
heartbeatSilenceCount = 0
clientConnected = False
lastHourChimed = None


# A class to control the amplifier
class AmplifierControl:

    amplifierPower = False
    socket = Energenie(1, amplifierPower)

    def on(self):
        print("Powering up amplifier.")
        self.socket.on()
        self.amplifierPower = True

    def off(self):
        global hourChime
        print("Beginning amplifier power-down sequence.")
        print("Disabling hourly chimes.")
        hourChime = False
        print("Stopping audio.")
        mixer.stopAudio()
        time.sleep(fadeoutDelay)
        print("Powering down amplifier.")
        self.socket.off()
        self.amplifierPower = False
        print("Amplifier off.")


# A class to handle audio output
class AudioMixer:

    def __init__(self):
        pygame.mixer.init()

    def loadAudio(self, filename):
        print("Loading audio file: ") + filename
        pygame.mixer.music.load(filename)

    def playAudio(self, loops=0):
        print("Playing loaded audio file")
        pygame.mixer.music.set_volume(0)
        pygame.mixer.music.play(loops)

        # Fade it up!
        for i in range(0, 100):
            time.sleep(float(fadeinDelay)/100)
            newVolume = i * 0.01
            print("volume is ") + str(newVolume)
            pygame.mixer.music.set_volume(newVolume)

    def stopAudio(self):
        print("Stopping current audio.")
        pygame.mixer.music.fadeout(fadeoutDelay*1000)


# This is where we respond to things.
class BaltimoreHandler:

    def __init__(self):
        self.log = {}

    def heartbeat(self):
        global clientConnected, heartbeatSilenceCount
        heartbeatSilenceCount = 0
        clientConnected = True
        print("Heartbeat received from client!")

    def amplifierOff(self):
        global amplifier
        amplifier.off()

    def amplifierOn(self):
        global amplifier
        amplifier.on()

    def hourChimeOff(self):
        global hourChime
        hourChime = False

    def hourChimeOn(self):
        global hourChime
        hourChime = True

    def amplifierState(self):
        global amplifier
        print("Amplifier state request. Replied with: ") + ('On' if amplifier.amplifierPower else 'Off')
        return amplifier.amplifierPower

    def hourChimeState(self):
        global hourChime
        print("Hourly chime state request. Replied with: ") + ('On' if hourChime else 'Off')
        return hourChime

    # Load the given filename
    def load(self, filename):
        global mixer
        mixer.loadAudio('audio/' + filename)

    # Play the given filename
    def play(self):
        global mixer
        mixer.playAudio(-1)

    # Fade the audio out.
    def stop(self):
        global mixer
        mixer.stopAudio()


# This class looks after things that need to happen regularly, like chimes and
# making sure we still have a client heartbeat.
class tickTockThread(threading.Thread):
    def __init__(self, name='heartbeatThread'):
        self._stopevent = threading.Event()
        self._sleepperiod = 1.0
        threading.Thread.__init__(self, name=name)

    def run(self):
        global heartbeatSilenceCount, clientConnected, hourChime, lastHourChimed
        while not self._stopevent.isSet():

            # Increment the heartbeat silence counter
            heartbeatSilenceCount = heartbeatSilenceCount + 1

            # Make sure there's a client connected. If not, gracefully kill things.
            if (heartbeatSilenceCount > 10 and clientConnected):
                print("Client has disappeared! Powering down amplifier.")
                amplifier.off()
                clientConnected = False

            # Hourly bells!

            if hourChime:

                # Is it the top of the hour, and not the last chimed hour?
                if (datetime.now().minute == 00 and
                        datetime.now().hour != lastHourChimed):
                    hour = datetime.now().hour

                    # Record that we've done this hour, or we'll be bonging all over the shop.
                    lastHourChimed = hour

                    # Calculate the necessary bonging.

                    # Hours come in 24 flavour!
                    if hour >= 12:
                        hour = hour - 12

                    # If the hour is 0 it's either midnight, or noon. Either way it's 12 bongs!
                    if hour == 0:
                        hour = 12

                    print("Chiming the hour! Number of bongs: ") + str(hour)

                    mixer.play('chimes/bong.wav', hour - 1)

            self._stopevent.wait(self._sleepperiod)

    def join(self, timeout=None):
        self._stopevent.set()
        threading.Thread.join(self, timeout)

# Initialise all the Thrift stuff

handler = BaltimoreHandler()
processor = Baltimore.Processor(handler)
transport = TSocket.TServerSocket(port=9090)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

thriftServer = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

# Off we go!

# This should be the default state of affairs.
hourChime = False

print("Good morning Baltimore!")

# Initialise our tasty objects!
amplifier = AmplifierControl()
mixer = AudioMixer()

# Kick off the tick tock thread!
tickTock = tickTockThread()
tickTock.start()

# Tell Thrift to start listening in
thriftServer.serve()

print("Goodbye.")
