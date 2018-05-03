import socket

# create an INET, STREAMing server socket
storagesocket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a port
storagesocket1.bind((socket.gethostname(), 4002))
# become a storage socket and queue up to 5 requests
storagesocket1.listen(5)
print("Storage node 2 is running!")

# initialize an index
index = {}

while True:
    # establish a connection
    serversocket, addr = storagesocket1.accept()
    print("Got a connection from server! %s" % str(addr))
    file_name = serversocket.recv(1024).decode('ascii')
    print("Sending file %s to server..." % file_name)
    serversocket.send((file_name).encode('ascii'))
    serversocket.close()
    print("File Sent! Disconnected from server %s!")
