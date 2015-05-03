#!/usr/bin/python

import sys
import mattdaemon

class PokerDaemon(mattdaemon.daemon):
    def run(self, *args, **kwargs):
        # TODO: Add user accounts to "players" table
        while True:
            # Play the game
            pass

if __name__ == "__main__":
    args = {
        "pidfile": "/tmp/poker-daemon.pid",
        "root": False
    }
    daem = PokerDaemon(**args)

    for arg in sys.argv[1:]:
        if arg in ('-v', '--version'):
            print("PokerDaemon: v0.0.1")
        elif arg in ("-h", "--help"):
            print("./{}".format(sys.argv[0]), "start|stop|restart|status")
        elif arg in ("start"):
            print("Starting daemon")
            daem.start()
        elif arg in ("stop"):
            print("Stopping daemon")
            daem.stop()
        elif arg in ("restart"):
            print("Restarting daemon")
            daem.restart()
        elif arg in ("status"):
            if daem.status():
                print("Daemon is running")
            else:
                print("Daemon is not running")
        else:
            print("Unknown argument:", arg)
