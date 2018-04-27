import socket
import os

# create an INET, STREAMing server socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a port
serversocket.bind((socket.gethostname(), 3002))
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
            os.remove(file_name)
        except KeyError:
            print("File %s does not exist in the index." % file_name)


while True:
    # establish a connection
    clientsocket, addr = serversocket.accept()
    print("Got a connection from %s" % str(addr))
    # send welcome message
    clientsocket.send(("Welcome! Choose an option:\n1. Sync Files\n2. Re-download Files".encode('ascii')))
    choice = clientsocket.recv(8).decode('ascii')

    if choice == "1":
        while True:
            client_log = clientsocket.recv(1024).decode('ascii')
            sync_query = client_log.split(';')
            file_name = sync_query[0]
            event_name = sync_query[1]
            update(file_name, event_name)

            if event_name == 'IN_MOVED_TO' or event_name == 'IN_CLOSE_WRITE':
                print("\nReceiving file %s..." % file_name)
                f = open(file_name, 'wb')
                file_size = int(sync_query[2])

                while file_size >= 1024:
                    l = clientsocket.recv(1024)
                    f.write(l)
                    file_size -= 1024
                if file_size > 0:
                    l = clientsocket.recv(file_size)
                    f.write(l)

                f.close()
                print("File %s synced!" % file_name)
                clientsocket.send(("Server: Sync Successful!").encode('ascii'))

    elif choice == "2":
        print("Sending index...")
        clientsocket.send((" ".join(index.keys()).encode('ascii')))
