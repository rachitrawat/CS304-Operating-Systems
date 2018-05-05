import os
import socket
import atexit
import inotify.adapters
import hashlib

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connection to server on the port
s.connect(('10.1.19.74', 3005))

# Only log events the following events:
# files moved in/modified
log_events_list = [['IN_MOVED_TO'], ['IN_CLOSE_WRITE']]

# max recv bytes size
BYTES_RECV = 1024


# for handling abrupt disconnects
def exit_handler():
    print("Closing Socket!")
    s.close()


atexit.register(exit_handler)


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def _main():
    # print initial messages
    print("Server: Choose an option:\n1. Sync Files\n2. Re-download Files")

    choice = input()
    s.send(choice.encode('ascii'))

    if choice == "1":
        print("Tracking watch_folder...")

        i = inotify.adapters.Inotify()

        i.add_watch('/home/su/PycharmProjects/Operating-Systems/PA3/watch_folder')

        for event in i.event_gen(yield_nones=False):
            (_, type_names, path, filename) = event

            # ignore filename = .goutputstream* ['IN_CLOSE_WRITE'] is sufficient
            if filename != '' and ".goutputstream" not in filename and type_names in log_events_list:

                file_size = int(os.stat("watch_folder/" + filename).st_size)

                # encode filename size as 16 bit binary
                fname_size_b = bin(len(filename))[2:].zfill(16)

                # send file name size & filename to server
                s.send(fname_size_b.encode('ascii'))
                s.send(filename.encode('ascii'))

                # encode filesize as 32 bit binary
                fsize_b = bin(file_size)[2:].zfill(32)
                s.send(fsize_b.encode('ascii'))

                # send 32 bit hash of file
                s.send(md5("watch_folder/" + filename).encode('ascii'))

                if type_names == ['IN_CLOSE_WRITE'] or type_names == ['IN_MOVED_TO']:
                    f = open("watch_folder/" + filename, 'rb')
                    print('\nUploading file %s... ' % filename)

                    while file_size >= BYTES_RECV:
                        l = f.read(BYTES_RECV)
                        s.send(l)
                        file_size -= BYTES_RECV

                    if file_size > 0:
                        l = f.read(file_size)
                        s.send(l)

                    f.close()
                    print("Upload finished of %s!" % filename)

                    server_response = s.recv(1).decode('ascii')
                    if server_response == "1":
                        print("Server: Sync successful")


    elif choice == "2":
        while True:
            flag = s.recv(1).decode('ascii')

            if flag == "1":
                # recv index str size & index
                index_str_size_b = s.recv(16).decode('ascii')
                index_str_size = int(index_str_size_b, 2)
                index_str = s.recv(index_str_size).decode('ascii')

                print("\nServer file index:\n" + index_str)
                file_choice = input("\nEnter file name to download: ")

                # encode filename size as 16 bit binary
                fname_size_b = bin(len(file_choice))[2:].zfill(16)

                # send file name size & filename to server
                s.send(fname_size_b.encode('ascii'))
                s.send(file_choice.encode('ascii'))

                # if file exists or not in index
                flag = s.recv(1).decode('ascii')

                # file exists in server index
                if flag == "1":
                    # recv file size
                    fsize_b = s.recv(32).decode('ascii')
                    fsize = int(fsize_b, 2)
                    file_size = fsize

                    # recv hash
                    md5_hash = s.recv(32).decode('ascii')

                    print("Downloading file %s..." % file_choice)
                    f = open("download_folder/" + file_choice, 'wb')

                    while file_size >= BYTES_RECV:
                        buff = bytearray()
                        while len(buff) < BYTES_RECV:
                            buff.extend(s.recv(BYTES_RECV - len(buff)))
                        f.write(buff)
                        file_size -= BYTES_RECV
                    if file_size > 0:
                        buff = bytearray()
                        while len(buff) < file_size:
                            buff.extend(s.recv(file_size - len(buff)))
                        f.write(buff)

                    f.close()
                    print("Download finished of %s!" % file_choice)

                    # verify hash
                    if md5("download_folder/" + file_choice) == md5_hash:
                        print("Hash verified.")
                    else:
                        print("Hash mismatch.")

                # requested file does not exist in server index
                else:
                    print("\nServer: File %s does not exist in index!" % file_choice)
                    continue

            # empty server index
            else:
                print("\nServer: No synced files!")
                break

    # invalid choice
    else:
        print("\nInvalid choice.")


if __name__ == '__main__':
    _main()
