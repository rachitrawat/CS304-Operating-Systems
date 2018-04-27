import socket
import os

import inotify.adapters

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connection to hostname on the port
s.connect((socket.gethostname(), 2801))

# Only log events the following events:
# file moved to/from
# file modified
log_events_list = [['IN_MOVED_TO'], ['IN_CLOSE_WRITE'], ['IN_MOVED_FROM']]


def _main():
    # receive initial message from server
    print("Connected: " + s.recv(1024).decode('ascii'))

    i = inotify.adapters.Inotify()

    i.add_watch('/home/su/PycharmProjects/Operating-Systems/PA3/watch_folder')

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event

        # ignore filename = .goutputstream* ['IN_CLOSE_WRITE'] is sufficient
        if filename != '' and ".goutputstream" not in filename and type_names in log_events_list:
            log_display = "FILENAME=[{}];EVENT_TYPE={}".format(filename, type_names)
            file_size = int(os.stat("watch_folder/" + filename).st_size)
            log_send = "{};{};{}".format(filename, ''.join(type_names), file_size)
            print(log_display.format(filename, type_names))

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


if __name__ == '__main__':
    _main()
