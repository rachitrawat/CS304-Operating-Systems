import os
import socket
import atexit
import inotify.adapters

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connection to server on the port
s.connect((socket.gethostname(), 3904))

# Only log events the following events:
# files moved in/modified
log_events_list = [['IN_MOVED_TO'], ['IN_CLOSE_WRITE']]

# limit recv bytes size to reduce packet errors
BYTES_RECV = 32


# for handling abrupt disconnects
def exit_handler():
    print("Closing Socket!")
    s.close()


atexit.register(exit_handler)


def _main():
    # receive initial messages from server
    print("Server: " + s.recv(61).decode('ascii'))

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
                    print(s.recv(24).decode('ascii'))


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
                    fsize_b = s.recv(32)
                    fsize = int(fsize_b, 2)
                    file_size = fsize

                    print("Downloading file %s..." % file_choice)
                    f = open("download_folder/" + file_choice, 'wb')

                    while file_size >= BYTES_RECV:
                        l = s.recv(BYTES_RECV)
                        f.write(l)
                        file_size -= BYTES_RECV
                    if file_size > 0:
                        l = s.recv(file_size)
                        f.write(l)

                    f.close()
                    print("Download finished of %s!" % file_choice)

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
