import time
import sys
import os

# https://stackoverflow.com/a/49007649
class Watcher(object):
    running = True
    refresh_delay_secs = 1

    def __init__(self, watch_file, call_func_on_change=None, *args, **kwargs):
        self._cached_stamp = 0
        self.filename = watch_file
        self.call_func_on_change = call_func_on_change
        self.args = args
        self.kwargs = kwargs

    def look(self):
        stamp = os.stat(self.filename).st_mtime
        if stamp != self._cached_stamp:
            self._cached_stamp = stamp

            if self.call_func_on_change is not None:
                self.call_func_on_change(*self.args, **self.kwargs)
      
    def watch(self):
        while self.running: 
            try: 
                time.sleep(self.refresh_delay_secs) 
                self.look() 
            except KeyboardInterrupt: 
                exit()
                break 
            except FileNotFoundError:
                pass
            except: 
                print('Unhandled error: %s' % sys.exc_info()[0])