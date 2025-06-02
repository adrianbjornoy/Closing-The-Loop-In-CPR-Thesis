import time
from collections import deque

class CompressionTracker:
    def __init__(self, window_size=3):
        self.timestamps = deque(maxlen=window_size)

    def record_compression(self):
        now = time.time()
        self.timestamps.append(now)
        return self.calculate_bpm()

    def calculate_bpm(self):
        if len(self.timestamps) < 2:
            return None
        intervals = [t2 - t1 for t1, t2 in zip(self.timestamps, list(self.timestamps)[1:])]
        avg_interval = sum(intervals) / len(intervals)
        return 60.0 / avg_interval if avg_interval > 0 else None
