import serial
import threading
import queue
import numpy as np
from config import config

SERIAL_PORT = config["serial"]["port"]
BAUD_RATE = config["serial"]["baud_rate"]
NUM_ROWS = config["matrix"]["rows"]
NUM_COLS = config["matrix"]["cols"]
MOCK_MODE = config.get("serial", {}).get("mock_mode", False)

class SerialReader:
    def __init__(self):
        self.matrix_queue = queue.Queue()
        self.comp_queue = queue.Queue()
        self.running = True
        self.mock_mode = MOCK_MODE

        if not self.mock_mode:
            try:
                self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                self.thread = threading.Thread(target=self._read_serial, daemon=True)
                self.thread.start()
            except serial.SerialException:
                print(f"Warning: Could not open {SERIAL_PORT}. Running in MOCK mode.")
                self.mock_mode = True

    def _read_serial(self):
        buffer = []
        while self.running:
            try:
                line = self.ser.readline().decode("utf-8").strip()
                if not line:
                    continue

                row_data = line.split(",")

                if len(row_data) == NUM_COLS:
                    buffer.append([float(value) for value in row_data])
                    if len(buffer) == NUM_ROWS:
                        self.matrix_queue.put(np.array(buffer, dtype=float))
                        buffer = []
                elif len(row_data) == 3 and row_data[0] == "D":
                    try:
                        depth = float(row_data[1])
                        timestamp = int(row_data[2])
                        self.comp_queue.put((depth, timestamp))
                    except ValueError:
                        pass
                # ignore garbage silently

            except Exception as e:
                print(f"Serial Read Error: {e}")

    def read_matrix(self):
        try:
            return self.matrix_queue.get_nowait()
        except queue.Empty:
            return None

    def read_compression(self):
        try:
            return self.comp_queue.get_nowait()
        except queue.Empty:
            return None

    def close(self):
        self.running = False
        if not self.mock_mode:
            self.thread.join()
            self.ser.close()
