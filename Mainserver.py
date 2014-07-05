import socket, traceback, os, sys, select
#This class is the server state, depending on what happens with the server different states happen.
class serverstate:
    stdmask = select.POLLERR | select.POLLHUP | select.POLLNVAL
#Initalize the server
    def __init__(mainserver, mastersocket):
        mainserver.p = select.poll()
        mainserver.mastersocket = mastersocket
        mainserver.serverread(mastersocket)
        mainserver.readbuffers = {}
        mainserver.writebuffers = {}
        mainserver.sockets = {mastersocket.fileno(): mastersocket}
#The filesocket class, using sockets for this implementation
    def filesocket(mainserver, mp):
        return mainserver.sockets[mp]
#You can specify whether to watch the client in the server or not and register their credientials
    def watchclient(mainserver,mp):
        mainserver.p.register(mp, select.POLLIN | select.POLLOUT | mainserver.stdmask)
#Or you can choose not to if you wish
    def dontwclient(mainserver, mp):
        mainserver.p.unregister(mp)
#This class reads the data line by line in the filesocket
    def readdata(mainserver, text, originmp):
        for line in text.split("\n"):
            line = line.strip()
            transmittext = str(mainserver.filesocket(originmp).getpeername()) + \
                    ": " + line + "\n"
            for mp in mainserver.writebuffers.keys():
                mainserver.writebuffers[mp] += transmittext
               mainserver.watchclient(mp)
#This class handles establishing a connection, like the connection to your soul man, it's deep.
    def connectionestablish(mainserver, sock):
        mp = sock.fileno()
        mainserver.watchclient(mp)
        mainserver.writebuffers[mp] = "Welcome to the chat server, %s\n" % \
                str(sock.getpeername())
        mainserver.readbuffers[mp] = ""
        mainserver.sockets[mp] = sock
#This is the server read action, it signal the server to read in data
    def serverread(mainserver, mp):
        mainserver.p.register(mp, select.POLLIN | mainserver.stdmask)
#This is the server write action, it will signal the server to write out data
    def serverwrite(mainserver, mp):
        mainserver.p.register(mp, select.POLLOUT | mainserver.stdmask)

    #This is the actual filereading event for the server, given by signal
    def readfileevent(mainserver, mp):
        try:
            mainserver.readbuffers[mp] += mainserver.filesocket(mp).recv(4096)
        except:
            mainserver.terminateserver(mp)

        parts = mainserver.readbuffers[mp].split("SEND")
        if len(parts) < 2:
            return
        elif parts[-1] == '':
            mainserver.readbuffers[mp] = ""
            sendlist = parts[:-1]
        else:
            mainserver.readbuffers[mp] = parts[-1]
            sendlist = parts[:-1]

        for item in sendlist:
            mainserver.readdata(item.strip(), mp)
    #This is the actual filewriting event for the server, given by signal
    def writefileevent(mainserver, mp):
        if not len(mainserver.writebuffers[mp]):
            mainserver.serverread(mp)
            return
        
        try:
            byteswritten = mainserver.filesocket(mp).send(mainserver.writebuffers[mp])
        except:
            mainserver.terminateserver(mp)

        mainserver.writebuffers[mp] = mainserver.writebuffers[mp][byteswritten:]

        if not len(mainserver.writebuffers[mp]):
            mainserver.serverread(mp)
    #If there is an error with the server, this class will execute. Commonly, if the server is already running, it will prompt the user that the address is in use, I haven't experienced any other errors, if you guys do, shoot me a message on the forums.
    def errorserver(mainserver, mp):
        mainserver.terminateserver(mp)
    #The class responsible for terminating the server connection, it will deregister the user and then shutdown the socket connection.
    def terminateserver(mainserver, mp):
        mainserver.dontwclient(mp)
        try:
            mainserver.filesocket(mp).close()
        except:
            pass

        del mainserver.writebuffers[mp]
        del mainserver.sockets[mp]
#Main loop for the program, will initalize the main server, establish a connection, and will either signal a read or write action, else it's an error. 
    def loop(mainserver):
        while 1:
            result = mainserver.p.poll()
            for mp, event in result:
                if mp == mainserver.mastersocket.fileno() and event == select.POLLIN:
                    try:
                        newsock, addr = mainserver.filesocket(mp).accept()
                        newsock.setblocking(0)
                        print "Got connection from", newsock.getpeername()
                        mainserver.connectionestablish(newsock)
                    except:
                        pass
                elif event == select.POLLIN:
                    mainserver.readfileevent(mp)
                elif event == select.POLLOUT:
                    mainserver.writefileevent(mp)
                else:
                    mainserver.errorserver(mp)

host = ''                          
port = 51423

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(1)
s.setblocking(0)

state = serverstate(s)
state.loop()
