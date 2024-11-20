class ApplicationContext():
    def __init__(self) -> None:
        self._host = None
        self._port = None
        self._control_bits = 0b00000000

    def get_host(self) -> str:
        return self._host

    def set_host(self, host: str) -> None:
        self._host = host
    
    def get_port(self) -> int:
        return self._port
    
    def set_port(self, port: int) -> None:
        self._port = port
    
    def get_control_bits(self) -> int:
        return self._control_bits

    def set_control_bits(self, bits: list[int]) -> None:
        if len(bits) != 8:
            raise ValueError("Control bits must be a list of 8 integers (0 or 1).")
        if not all(bit in (0, 1) for bit in bits):
            raise ValueError("Control bits can only be 0 or 1.")
        
        self._control_bits = int(''.join(map(str, bits)), 2)