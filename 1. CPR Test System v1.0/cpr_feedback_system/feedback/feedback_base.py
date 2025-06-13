import time
import threading
import queue
import serial
from abc import ABC, abstractmethod
from config import config

class FeedbackMechanism(ABC):
    def __init__(self, device_key):
        cfg = config["feedback"][device_key]
        port = cfg.get("port")
        baud = cfg.get("baud_rate", 115200)

        self.ser = None
        if port:
            try:
                self.ser = serial.Serial(port, baud, timeout=0, write_timeout=0)
                time.sleep(2)
                self.ser.reset_input_buffer()
            except serial.SerialException as e:
                print(f"[{device_key}] warning: can't open {port}: {e}")

        self._tx_q = queue.Queue()
        self._running = True
        self._writer = threading.Thread(target=self._write_loop, daemon=True)
        self._writer.start()

        self._last_cmd = ""
        self.dep_min, self.dep_max = self.get_depth_range_for_target()
        self.err_thresh = cfg.get("error_threshold", 1.0)
        self.focus = config["feedback"].get("focus", "both")

    def _write_loop(self):
        while self._running:
            cmd = self._tx_q.get()
            if cmd is None:
                break
            if self.ser:
                try:
                    self.ser.write((cmd + "\n").encode("utf-8"))
                except Exception as e:
                    print(f"[feedback] send error '{cmd}': {e}")

    def _send_command(self, cmd):
        if cmd != self._last_cmd:
            self._tx_q.put(cmd)
            self._last_cmd = cmd

    def _cleanup(self):
        self._running = False
        self._tx_q.put(None)
        self._writer.join()
        if self.ser:
            self.ser.close()

    def get_depth_range_for_target(self):
        target_label = config["feedback"].get("target")
        mapping = config["depth_sensor"].get("target_to_range_map", {})
        range_key = mapping.get(target_label, None)
        depth_range = config["depth_sensor"].get(range_key, [0, 999])
        print(f"Depth range for {target_label}: {depth_range}")
        return depth_range

    def close(self):
        self._cleanup()

    @abstractmethod
    def give_feedback(self, *, cop=None, target=None, error=None, depth=None, timestamp=None):
        pass
