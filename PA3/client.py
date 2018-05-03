import socket
import os
import time
import inotify.adapters

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connection to server on the port
s.connect((socket.gethostname(), 3903))

# Only log events the following events:
# files moved in/modified
log_events_list = [['IN_MOVED_TO'], ['IN_CLOSE_WRITE']]

import atexit


def exit_handler():
    print("Closing Socket!")
    s.close()


atexit.register(exit_handler)


def _main():
    # receive initial messages from server
    print("Server: " + s.recv(100).decode('ascii'))

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

                file_size = 0

                file_size = int(os.stat("watch_folder/" + filename).st_size)
                log_send = "{};{};{}".format(filename, ''.join(type_names), file_size)

                # send log to server
                s.send(log_send.encode('ascii'))
                # let client finish sending log
                time.sleep(1)

                if type_names == ['IN_CLOSE_WRITE'] or type_names == ['IN_MOVED_TO']:
                    f = open("watch_folder/" + filename, 'rb')
                    print('\nUploading file %s... ' % filename)

                    while file_size >= 1024:
                        l = f.read(1024)
                        s.send(l)
                        file_size -= 1024

                    if file_size > 0:
                        l = f.read(file_size)
                        s.send(l)

                    f.close()
                    print("Upload finished of %s!" % filename)
                    print(s.recv(1024).decode('ascii'))


    elif choice == "2":
        print("Server file index: \n" + s.recv(1024).decode('ascii'))
        file_choice = input("\nEnter file name to download: ")
        s.send(file_choice.encode('ascii'))
        # receive file size
        file_size = int(s.recv(100).decode('ascii'))

        f = open("download_folder/" + file_choice, 'wb')

        while file_size >= 1024:
            l = s.recv(1024)
            f.write(l)
            file_size -= 1024
        if file_size > 0:
            l = s.recv(file_size)
            f.write(l)

        f.close()
        print("Download finished of %s!" % file_choice)


if __name__ == '__main__':
    _main()
