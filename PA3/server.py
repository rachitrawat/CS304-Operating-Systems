import socket

# create an INET, STREAMing server socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a port
serversocket.bind((socket.gethostname(), 2801))
# become a server socket and queue up to 5 requests
serversocket.listen(5)
print("Server is running!")

# initialize an index
index = {}


def update(file_name, event_name):
    if event_name == 'IN_MOVED_TO' or event_name == 'IN_CLOSE_WRITE':
        index[file_name] = ""

    elif event_name == 'IN_MOVED_FROM':
        try:
            del index[file_name]
        except KeyError:
            print("File %s does not exist in the index." % file_name)


while True:
    # establish a connection
    clientsocket, addr = serversocket.accept()
    print("Got a connection from %s" % str(addr))
    # send welcome message
    clientsocket.send(("Welcome to the server!".encode('ascii')))
    while True:
        client_log = clientsocket.recv(1024).decode('ascii')
        sync_query = client_log.split(';')
        file_name = sync_query[0]
        event_name = sync_query[1]
        print(file_name, event_name)
        update(file_name, event_name)

        if event_name == 'IN_MOVED_TO' or event_name == 'IN_CLOSE_WRITE':
            print("Receiving file %s..." % file_name)
            f = open(file_name, 'wb')
            l = clientsocket.recv(1024)
            while (l):
                f.write(l)
                l = clientsocket.recv(1024)
            f.close()
            print("File %s synced!" % file_name)
            clientsocket.send(("Server: Sync Successful!").encode('ascii'))
            clientsocket.close()
            break
