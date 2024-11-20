from nanogui.context import ApplicationContext

class TCPServer:
    def __init__(self, context: ApplicationContext) -> None:
        self._context = context