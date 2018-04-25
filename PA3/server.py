import socket

# create an INET, STREAMing server socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a port
serversocket.bind((socket.gethostname(), 2348))
# become a server socket and queue up to 5 requests
serversocket.listen(5)
print("Server is running!")

while True:
    # establish a connection
    clientsocket, addr = serversocket.accept()
    print("Got a connection from %s" % str(addr))
    while True:
        # send tags list
        clientsocket.send(("Welcome to the server!".encode('ascii')))
        client_log = clientsocket.recv(1024).decode('ascii')
        print(client_log)
