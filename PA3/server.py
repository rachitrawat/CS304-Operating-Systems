import os
import socket
import hashlib

# create an INET, STREAMing server socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a port
serversocket.bind(('10.1.17.16', 3005))
# become a server socket and queue up to 5 requests
serversocket.listen(5)

print("Server is running!")

# initialize an index
index = {}

# max recv bytes size
BYTES_RECV = 1024


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# flag 1
def retrieve_from_storage(filename):
    port_no = index[filename][0]
    file_size = index[filename][1]
    md5_hash = index[filename][2]

    # create a socket object
    server_as_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to storage node
    server_as_client_socket.connect(('10.1.22.140', port_no))
    print("Connected to storage node at port %s." % port_no)

    # notify storage node to begin download process
    server_as_client_socket.send(("1".encode('ascii')))

    # encode filename size as 16 bit binary
    fname_size_b = bin(len(filename))[2:].zfill(16)

    # send file name size & filename to server
    server_as_client_socket.send(fname_size_b.encode('ascii'))
    server_as_client_socket.send(filename.encode('ascii'))

    # encode filesize as 32 bit binary
    fsize_b = bin(file_size)[2:].zfill(32)
    server_as_client_socket.send(fsize_b.encode('ascii'))

    print("Retrieving file %s from storage node..." % filename)
    f = open("server_tmp/" + filename, 'wb')

    while file_size >= BYTES_RECV:
        buff = bytearray()
        while len(buff) < BYTES_RECV:
            buff.extend(server_as_client_socket.recv(BYTES_RECV - len(buff)))
        f.write(buff)
        file_size -= BYTES_RECV
    if file_size > 0:
        buff = bytearray()
        while len(buff) < file_size:
            buff.extend(server_as_client_socket.recv(file_size - len(buff)))
        f.write(buff)

    f.close()

    print("Download finished of %s!" % filename)

    # verify hash
    if md5("server_tmp/" + filename) == md5_hash:
        print("Hash verified.")
    else:
        print("Hash mismatch.")

    server_as_client_socket.close()
    print("Disconnected from storage node.")


# flag 0
def upload_to_storage(filename):
    port_no = index[filename][0]
    file_size = index[filename][1]

    # create a socket object
    server_as_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to storage node
    server_as_client_socket.connect(('10.1.22.140', port_no))
    print("Connected to storage node at port %s." % port_no)

    # notify storage node to begin upload process
    server_as_client_socket.send(("0".encode('ascii')))

    # encode filename size as 16 bit binary
    fname_size_b = bin(len(filename))[2:].zfill(16)

    # send file name size & filename to server
    server_as_client_socket.send(fname_size_b.encode('ascii'))
    server_as_client_socket.send(filename.encode('ascii'))

    # encode & send filesize as 32 bit binary
    fsize_b = bin(file_size)[2:].zfill(32)
    server_as_client_socket.send(fsize_b.encode('ascii'))

    print("Uploading file %s to storage node." % filename)
    f = open("server_tmp/" + filename, 'rb')

    while file_size >= BYTES_RECV:
        l = f.read(BYTES_RECV)
        server_as_client_socket.send(l)
        file_size -= BYTES_RECV

    if file_size > 0:
        l = f.read(file_size)
        server_as_client_socket.send(l)

    f.close()
    print("Upload finished of %s!" % filename)
    server_as_client_socket.close()
    print("Disconnected from storage node.")
    os.remove("server_tmp/" + filename)
    print("Deleted file %s from server." % filename)


def update_index(filename, file_extension, file_size, md5_hash):
    # index filename with port numbers of respective storage nodes
    if file_extension == ".pdf":
        port_no = 4001
    elif file_extension == ".txt":
        port_no = 4002
    elif file_extension == ".mp3":
        port_no = 4003
    else:
        port_no = 4004

    index[filename] = [port_no, file_size, md5_hash]
    # upload file to storage_node
    upload_to_storage(filename)


while True:
    # establish a connection
    clientsocket, addr = serversocket.accept()
    print("\nGot a connection from! %s" % str(addr))

    # get client choice
    choice = clientsocket.recv(1).decode('ascii')

    if choice == "1":
        while True:
            # recv file name size & file name
            fname_size_b = clientsocket.recv(16).decode('ascii')

            if fname_size_b == '':
                print("Client disconnected!")
                clientsocket.close()
                break

            fname_size = int(fname_size_b, 2)
            filename = clientsocket.recv(fname_size).decode('ascii')

            # recv file size
            fsize_b = clientsocket.recv(32).decode('ascii')
            fsize = int(fsize_b, 2)

            # recv hash
            md5_hash = clientsocket.recv(32).decode('ascii')

            print("\nReceiving file %s from client..." % filename)
            f = open("server_tmp/" + filename, 'wb')
            file_size = fsize

            while file_size >= BYTES_RECV:
                buff = bytearray()
                while len(buff) < BYTES_RECV:
                    buff.extend(clientsocket.recv(BYTES_RECV - len(buff)))
                f.write(buff)
                file_size -= BYTES_RECV

            if file_size > 0:
                buff = bytearray()
                while len(buff) < file_size:
                    buff.extend(clientsocket.recv(file_size - len(buff)))
                f.write(buff)

            f.close()

            print("File %s received from client!" % filename)

            # verify hash
            if md5("server_tmp/" + filename) == md5_hash:
                print("Hash verified.")
            else:
                print("Hash mismatch.")

            file_size = fsize
            file_name, file_extension = os.path.splitext(filename)
            update_index(filename, file_extension, file_size, md5_hash)
            clientsocket.send("1".encode('ascii'))

    elif choice == "2":
        while True:
            # if index non-empty
            if index:
                # notify client that index exists
                clientsocket.send(("1".encode('ascii')))

                print("\nSending index...")
                index_str = "\n".join(index.keys())
                index_str_size_b = bin(len(index_str))[2:].zfill(16)

                # send index str size & index str to server
                clientsocket.send(index_str_size_b.encode('ascii'))
                clientsocket.send(index_str.encode('ascii'))

                # recv file name size & file name
                fname_size_b = clientsocket.recv(16).decode('ascii')
                # in case client abruptly disconnects
                if fname_size_b == '':
                    print("Client disconnected!")
                    clientsocket.close()
                    break
                fname_size = int(fname_size_b, 2)
                filename = clientsocket.recv(fname_size).decode('ascii')
                file_choice = filename

                if file_choice not in index:
                    print("File %s not in index!" % file_choice)
                    # notify client that file does not exist in index
                    clientsocket.send(("0".encode('ascii')))
                else:
                    # notify client that file exists in index
                    clientsocket.send(("1".encode('ascii')))

                    # Retrieve from storage
                    retrieve_from_storage(file_choice)
                    file_size = int(index[file_choice][1])

                    # encode filesize as 32 bit binary
                    fsize_b = bin(file_size)[2:].zfill(32)
                    clientsocket.send(fsize_b.encode('ascii'))

                    # send md5 hash
                    clientsocket.send(index[filename][2].encode('ascii'))

                    print("Sending file %s to client..." % file_choice)
                    f = open("server_tmp/" + file_choice, 'rb')

                    while file_size >= BYTES_RECV:
                        l = f.read(BYTES_RECV)
                        clientsocket.send(l)
                        file_size -= BYTES_RECV

                    if file_size > 0:
                        l = f.read(file_size)
                        clientsocket.send(l)

                    f.close()

                    print("File %s sent to client!" % file_choice)
                    os.remove("server_tmp/" + file_choice)
                    print("Deleted file %s from server." % file_choice)

            else:
                print("\nNo synced files!")
                # notify client that no index exists
                clientsocket.send(("0".encode('ascii')))
                print("Client disconnected!")
                clientsocket.close()
                break

    else:
        print("Invalid choice by client.")
        print("Client disconnected!")
        clientsocket.close()
