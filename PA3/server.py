import socket
import os
import time

# create an INET, STREAMing server socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a port
serversocket.bind((socket.gethostname(), 3902))
# become a server socket and queue up to 5 requests
serversocket.listen(5)

print("Server is running!")

# initialize an index
index = {}


def upload_to_storage(filename, port_no, file_size):
    # create a socket object
    server_as_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to storage node
    server_as_client_socket.connect((socket.gethostname(), port_no))
    print("Connected to storage node at port %s." % port_no)
    # send req type : 1 for file upload
    log_send = "{};{};{}".format(filename, file_size, "1")
    # send file log
    server_as_client_socket.send((log_send).encode('ascii'))
    # wait for server to finish sending log
    time.sleep(1)
    print("Uploading file %s to storage node." % filename)
    f = open("server_tmp/" + filename, 'rb')

    while file_size >= 1024:
        l = f.read(1024)
        server_as_client_socket.send(l)
        file_size -= 1024

    if file_size > 0:
        l = f.read(file_size)
        server_as_client_socket.send(l)

    f.close()
    print("Upload finished of %s!" % filename)
    server_as_client_socket.close()
    print("Disconnected from storage node.")
    os.remove("server_tmp/" + filename)
    print("Deleted file %s from server." % filename)


def update_index(file_name, file_extension, event_name, file_size):
    if event_name == 'IN_MOVED_TO' or event_name == 'IN_CLOSE_WRITE':
        # index filename with port numbers of respective storage nodes
        if file_extension == ".pdf" or file_extension == ".txt" or file_extension == ".py":
            port_no = 4001
        elif file_extension == ".mp3":
            port_no = 4002
        else:
            port_no = 4003

        index[file_name + file_extension] = [port_no, file_size]
        # upload file to storage_node
        upload_to_storage(file_name + file_extension, port_no, file_size)


while True:
    # establish a connection
    clientsocket, addr = serversocket.accept()
    print("Got a connection from! %s" % str(addr))
    # send welcome message
    clientsocket.send(("Welcome! Choose an option:\n1. Sync Files\n2. Re-download Files".encode('ascii')))
    choice = clientsocket.recv(8).decode('ascii')

    if choice == "1":
        while True:
            client_log = clientsocket.recv(100).decode('ascii')
            if client_log == '':
                print("Client disconnected!")
                clientsocket.close()
                break

            sync_query = client_log.split(';')
            file_name = sync_query[0]
            event_name = sync_query[1]

            if event_name == 'IN_MOVED_TO' or event_name == 'IN_CLOSE_WRITE':
                print("\nReceiving file %s from client..." % file_name)
                f = open("server_tmp/" + file_name, 'wb')
                file_size = int(sync_query[2])

                while file_size >= 1024:
                    l = clientsocket.recv(1024)
                    f.write(l)
                    file_size -= 1024
                if file_size > 0:
                    l = clientsocket.recv(file_size)
                    f.write(l)

                f.close()

                print("File %s received from client!" % file_name)

                file_name, file_extension = os.path.splitext(file_name)
                update_index(file_name, file_extension, event_name, file_size)
                clientsocket.send(("Server: Sync Successful!").encode('ascii'))

    # elif choice == "2":
    #     print("Sending index...")
    #     clientsocket.send(("\n".join(index.keys()).encode('ascii')))
    #     file_ch = clientsocket.recv(100).decode('ascii')
    #     print("Sending requested file %s " % file_ch)
    #     # todo send file
    #     # connect to storage node
    #     server_as_client_socket.connect((socket.gethostname(), 4002))
    #     print("Connected to storage node!")
    #     server_as_client_socket.send(("testname").encode('ascii'))
    #     print("Downloading file from storage node...")
    #     str_text = server_as_client_socket.recv(1024).decode('ascii')
    #     # wait a sec before sending to avoid buffer intermix
    #     time.sleep(1)
    #     server_as_client_socket.close()
    #     print("Downloaded from storage node! Sending file to client...")
    #     clientsocket.send(str_text.encode('ascii'))
    #     print("File sent to client!")
    #     clientsocket.close()
