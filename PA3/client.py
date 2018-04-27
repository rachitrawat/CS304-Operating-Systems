import socket
import os

import inotify.adapters

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connection to hostname on the port
s.connect((socket.gethostname(), 3001))

# Only log events the following events:
# file moved to/from
# file modified
log_events_list = [['IN_MOVED_TO'], ['IN_CLOSE_WRITE'], ['IN_MOVED_FROM']]


def _main():
    # receive initial messages from server
    print("Server: " + s.recv(1024).decode('ascii'))

    choice = input()
    s.send(choice.encode('ascii'))

    if choice == "1":

        i = inotify.adapters.Inotify()

        i.add_watch('/home/su/PycharmProjects/Operating-Systems/PA3/watch_folder')

        for event in i.event_gen(yield_nones=False):
            (_, type_names, path, filename) = event

            # ignore filename = .goutputstream* ['IN_CLOSE_WRITE'] is sufficient
            if filename != '' and ".goutputstream" not in filename and type_names in log_events_list:

                file_size = 0

                # don't calculate file size when event is FILE MOVED FROM
                if type_names == ['IN_MOVED_FROM']:
                    log_send = "{};{}".format(filename, ''.join(type_names), file_size)
                else:
                    file_size = int(os.stat("watch_folder/" + filename).st_size)
                    log_send = "{};{};{}".format(filename, ''.join(type_names), file_size)

                # send log to server
                s.send(log_send.encode('ascii'))

                if type_names == ['IN_CLOSE_WRITE'] or type_names == ['IN_MOVED_TO']:
                    f = open("watch_folder/" + filename, 'rb')
                    print('Uploading file %s... ' % filename)

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
        print("Server: " + s.recv(1024).decode('ascii'))


if __name__ == '__main__':
    _main()
