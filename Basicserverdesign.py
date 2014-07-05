import socket

host = ''                              
port = 51423

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(1)

print "Server is running on this port %d." \
      % port

while 1:
    #Have three variables that are interesting, the incoming socket, incoming address, and incoming file from the client.
    incomingsocket, incomingaddress = s.accept()
    incomingfile = incomingsocket.makefile('rw', 0)
    incomingfile.write("Welcome, " + str(incomingaddress) + "\n")
    incomingfile.write("Please enter a string: ")
    line = incomingfile.readline().strip()
    incomingfile.write("You entered %d characters.\n" % len(line))
    incomingfile.close()
    incomingsocket.close()

