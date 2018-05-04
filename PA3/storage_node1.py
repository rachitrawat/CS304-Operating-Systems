import socket

# create an INET, STREAMing server socket
storagesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a port
storagesocket.bind((socket.gethostname(), 4001))
# become a storage socket and queue up to 5 requests
storagesocket.listen(5)
print("Storage node 1 is running!")

while True:
    # establish a connection
    serversocket, addr = storagesocket.accept()
    print("\nGot a connection from server! %s" % str(addr))

    # 0 for server upload, 1 for server download
    req_type = serversocket.recv(1).decode('ascii')

    # recv file name size & file name
    fname_size_b = serversocket.recv(16).decode('ascii')
    fname_size = int(fname_size_b, 2)
    filename = serversocket.recv(fname_size).decode('ascii')

    # recv file size
    fsize_b = serversocket.recv(32)
    fsize = int(fsize_b, 2)
    file_size = fsize

    # server wants to upload file
    if req_type == "0":

        print("Receiving file %s from server..." % filename)
        f = open("storage_node_1/" + filename, 'wb')
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
    elif req_type == "1":
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
