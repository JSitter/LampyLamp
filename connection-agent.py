import socket
from threading import Thread
import serial
import time

# Listen for incoming connections on port
class portListener:
    messages = []
    shutdown = False
    messageAvailable = False
    port = 0
    listen = True
    host = '192.168.2.105'
    connectionsAccepted = 1
    size = 1024
    color = "0 0 255"
    connection = ""

    def __init__(self, port):

	self.port = int(port)
	self.openConnection()

    #Loop to run on its own thread
    def scanner(self, clientConnection):
	print("Listening on %s:%s" % (self.host, self.port))
	while self.listen:
	    client, addr = clientConnection.accept()
	    data = client.recv(self.size)
	    if data:
		print('received from %s: %s' % (addr[0], data))
		if data=="shutdown":
		    self.closeConnection()
		    return "Shutdown"
		elif data=="color":
		    msg=self.color

		else:

		    self.pushMessage(data)
		    self.color = data
		    msg = data

		client.send(msg.encode())

	    client.close()

    def closeConnection(self):
	print("Shutting Down Server")
	self.listen=False
	self.connection.close()
	self.shutdown = True

    def openConnection(self):

	self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	self.connection.bind((self.host, self.port))
	self.connection.listen(self.connectionsAccepted)


    def pushMessage(self, message):
	self.messageAvailable = True
	self.messages.append(message)


    def getMessage(self):

	if self.messageAvailable:
	    print("Available Messages: %s" % self.messageAvailable)
	    message = self.messages.pop()

	    print("Network Message: " + message)
	    print("Messages in Queue:")
	    print("number of messages: %s" % len(self.messages))

	    if len(self.messages) == 0:
		self.messageAvailable = False
	    return message
#End of Listener Class

class messageControl:

    portListener = ""
    arduino = ""

    def __init__(self, scanner):
	self.portListener = scanner
	print("Opening Serial Port")
	self.arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout = 1)
	time.sleep(1)
	print("Arduino Connection Initializesation Complete")


    def pullMessage(self):

	if self.portListener.messageAvailable:

	    message = self.portListener.getMessage()
	    print(message)
	    return message
	else:
	    return False

    def sendMessage(self):
	print("Send Message Method")
	message = self.pullMessage()



	if message !=False:

	    self.arduinoSend(message)

    def arduinoSend(self, message):

	red, green, blue = message.split(' ')

	command = red + " " + green + " " + blue + "\n"

	self.arduino.write(command)

    def sniffMessages(self):
	    while self.portListener.messageAvailable:
		self.sendMessage() #send message to arduino

    def messageWorker(self):

	while self.portListener.shutdown == False:
	    self.sniffMessages()
	    time.sleep(.1)


# End of MessageControl
    


# Main Program
def Main():
    print("Welcome to Lampylamp version 1.5 alpha!\n")

    run = True
    scannerThread = ""

    network = portListener(34625)

    scannerThread = Thread(target=network.scanner, args=(network.connection,))
    scannerThread.start()

    messageDelivery = messageControl(network)

    print("Hiring Message Worker")
    worker = Thread(target= messageDelivery.messageWorker)
    worker.start()



if __name__ == '__main__':
    Main()

