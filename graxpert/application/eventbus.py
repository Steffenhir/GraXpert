class EventBus:
    def __init__(self):
        self.listeners = {}
        # self.loop = asyncio.get_event_loop()

    def add_listener(self, event_name, listener):
        if not self.listeners.get(event_name, None):
            self.listeners[event_name] = [listener]
        else:
            if not listener in self.listeners[event_name]:
                self.listeners[event_name].insert(0, listener)

    def remove_listener(self, event_name, listener):
        self.listeners[event_name].remove(listener)
        if len(self.listeners[event_name]) == 0:
            del self.listeners[event_name]

    def emit(self, event_name, event=None):
        listeners = self.listeners.get(event_name, [])
        for listener in listeners:
            listener(event)


eventbus = EventBus()
