class EventHook(object):
    """A class for managing event handlers.
    """
    def __init__(self):
        self._handlers = set()
        
    def addHandler(self, handler):
        self._handlers.add(handler)
        
    def removeHandler(self, handler):
        self._handlers.remove(handler)
        
    def clearHandlers(self):
        self._handlers.clear()
        
    def callHandlers(self, *args, **kwargs):
        for h in self._handlers:
            h(*args, **kwargs)
