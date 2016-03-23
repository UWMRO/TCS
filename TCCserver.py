"""
run me with twistd -y chatserver.py, and then connect with multiple
telnet clients to port 5501
"""

from twisted.protocols import basic
from twisted.internet import protocol, reactor

#import pmc

class TCCServer(basic.LineReceiver):
    def connectionMade(self):
        self.sendLine("Successfully connected to the TCC Server")
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        self.sendLine("Connection lost")
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        print "received", line
        parser=TCCParser()
        input=parser.parse(line)
        if input != None:
            self.Message(input)

    def message(self, message):
        for client in self.factory.clients:
                self.sendLine(message)

class TCCClient(protocol.ServerFactory):
	protocol = TCCServer
	clients = []


class TCCParser(object):
	def __init__(self):
         print "Entered the parser"
          #self.pmc = pmc.pmc()

	def parse(self, input = None):
		print input
		input = input.split()
		if input[0] == 'slew':
			coords_dict={'ra':input[1],
				'dec':input[2]}
			logread= "Slewing telescope"
			return {'log':logread, 'slew':self.pmc.slew(coords_dict)}

		if input[0]=='focus':
			value=input[1]
			logread= "Focusing telescope"
			return {'log':logread, 'focus':self.pmc.slew(value)}

		if input[0]=='offset':
			RAjog=input[1]
			DECjog=input[2]
			logread="Jogging telescope by offset parameters"
			return {'log':logread, 'offset':self.pmc.offset(RAjog, DECjog)}

		if input[0]=='toggle track':
			tracking=input[1]
			if tracking==True:
				logread= "Turning tracking on"
			elif tracking==False:
				logread= "Turning tracking off"
			return {'log':logread,'track_toggle':self.pmc.track_set(tracking)}

		if input[0]=='set tracking rate':
			RArate=input[1]
			DECrate=input[2]
			logread="Setting RA and DEC tracking rates to specified values"
			return {'log':logread,  'trackingrate':self.pmc.track_setrate(RArate,DECrate)}

		if input[0]=='tracking status':
			return self.pmc.track_status()

if __name__=="__main__":
    reactor.listenTCP(5502,TCCClient())
    reactor.run()

