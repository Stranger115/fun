import logging
from typing import Callable


class _WebHookHandlers(object):
    def __init__(self):
        self._handlers = {}

    def add_handler(self, event_name: str, handler: Callable[[dict], None]) -> None:
        ''' this method is used to register handler function for specified event '''
        logging.info('add webhook handler for event "%s"' % event_name)
        self._handlers.setdefault(event_name, set()).add(handler)

    async def on_event(self, event_name, event):
        logging.info('got event "%s"' % event_name)
        evt_handlers = self._handlers.get(event_name, set())
        if not evt_handlers:
            logging.info('no handler for event "%s"' % event_name)
            return
        for handler in evt_handlers:
            await handler(event)


WebHookHandlers = _WebHookHandlers()
