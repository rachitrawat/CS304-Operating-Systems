import inotify.adapters
from datetime import datetime

# Only log events the following events:
# file moved to/from
# file modified
log_events_list = [['IN_MOVED_TO'], ['IN_CLOSE_WRITE'], ['IN_MOVED_FROM']]


def _main():
    i = inotify.adapters.Inotify()

    i.add_watch('/home/su/PycharmProjects/Operating-Systems/PA3/watch_folder')

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event

        # ignore filename = .goutputstream* ['IN_CLOSE_WRITE'] is sufficient
        if filename != '' and ".goutputstream" not in filename and type_names in log_events_list:
            print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={} TIME={}".format(
                path, filename, type_names, datetime.now().time()))


if __name__ == '__main__':
    _main()
