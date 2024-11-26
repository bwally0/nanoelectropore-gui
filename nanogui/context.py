from PySide6.QtCore import QObject, Signal
_context_instance = None

class ApplicationContext(QObject):
    """Application context for storing global state."""
    message_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._host = None
        self._port = None
        self._control_bits = 0b00000000
        self._message = "Server stopped."

    def get_host(self) -> str:
        """Get the host address.
        
        returns:
            str: The host address.
        """
        return self._host

    def set_host(self, host: str) -> None:
        """Set the host address.
        
        params:
            host (str): The host address.
        """
        self._host = host
    
    def get_port(self) -> int:
        """Get the port number.
        
        returns:
            int: The port number.
        """
        return self._port
    
    def set_port(self, port: int) -> None:
        """Set the port number.
        
        params:
            port (int): The port number.
        """
        self._port = port
    
    def get_control_bits(self) -> int:
        """Get the control bits as an integer.
        
        returns:
            int: The control bits.
        """
        return self._control_bits

    def set_control_bits(self, bits: list[int]) -> None:
        """Set the control bits.

        params:
            bits (list[int]): The control bits as a list of 8 integers (0 or 1).
        """
        if len(bits) != 8:
            raise ValueError("Control bits must be a list of 8 integers (0 or 1).")
        if not all(bit in (0, 1) for bit in bits):
            raise ValueError("Control bits can only be 0 or 1.")
        
        self._control_bits = int(''.join(map(str, bits)), 2)

    def get_message(self) -> str:
        """Get the current context message.
        
        returns:
            str: Context message.
        """
        return self._message
    
    def set_message(self, message: str) -> None:
        """Set the context message.
        
        params:
            message (str): The message to set.
        """
        self._message = message
        self.message_changed.emit(message)

def get_app_context() -> ApplicationContext:
    """Get the application context.
    
    returns:
        ApplicationContext: The application context singleton.
    """
    global _context_instance
    if _context_instance is None:
        _context_instance = ApplicationContext()
    return _context_instance