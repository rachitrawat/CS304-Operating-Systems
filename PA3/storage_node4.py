import socket

# create an INET, STREAMing server socket
storagesocket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a port
storagesocket1.bind((socket.gethostname(), 4004))
# become a storage socket and queue up to 5 requests
storagesocket1.listen(5)
print("Storage node 4 is running!")

# initialize an index
index = {}

while True:
    # establish a connection
    serversocket, addr = storagesocket1.accept()
    print("\nGot a connection from server! %s" % str(addr))

    # receive request type
    server_log = serversocket.recv(100).decode('ascii')
    sync_query = server_log.split(';')
    filename = sync_query[0]
    file_size = int(sync_query[1])
    req_type = sync_query[2]

    # server wants to upload file
    if req_type == "1":
        print("Receiving file %s from server..." % filename)
        f = open("storage_node_4/" + filename, 'wb')
        while file_size >= 1024:
            l = serversocket.recv(1024)
            f.write(l)
            file_size -= 1024
        if file_size > 0:
            l = serversocket.recv(file_size)
            f.write(l)

        f.close()
        print("File %s synced!" % filename)

    # server wants to retrieve file
    elif req_type == "2":
        print("Sending file %s to server..." % filename)
        f = open("storage_node_1/" + filename, 'rb')

        while file_size >= 1024:
            l = f.read(1024)
            serversocket.send(l)
            file_size -= 1024

        if file_size > 0:
            l = f.read(file_size)
            serversocket.send(l)

        f.close()
        print("File %s sent to server!" % filename)

    serversocket.close()
    print("Operation done! Disconnected from server.")
