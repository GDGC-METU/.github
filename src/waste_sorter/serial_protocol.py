"""Small newline-delimited USB serial protocol shared with the Uno sketch."""
import time

import serial

LABELS = {"plastic", "paper", "metal", "unknown"}


def encode_sort(label: str) -> bytes:
    normalized = label.lower()
    if normalized not in LABELS:
        raise ValueError(f"Unsupported sorting label: {label}")
    return f"SORT:{normalized.upper()}\n".encode("ascii")


class UnoConnection:
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        self.serial = serial.Serial(port, baudrate=baudrate, timeout=timeout, write_timeout=timeout)
        time.sleep(2.0)
        self.serial.reset_input_buffer()

    def wait_ready(self, timeout: float = 8.0) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            line = self.serial.readline().decode("ascii", errors="ignore").strip()
            if line == "READY":
                return True
        return False

    def send(self, label: str) -> None:
        self.serial.write(encode_sort(label))
        self.serial.flush()

    def close(self) -> None:
        self.serial.close()
