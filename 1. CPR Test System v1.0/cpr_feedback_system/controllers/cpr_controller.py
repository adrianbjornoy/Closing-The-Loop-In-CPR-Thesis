import time

from core.serial_reader import SerialReader
from core.pressure_mat import PressureMat
from core.target_zone import TargetZone
from feedback.strategy import FeedbackStrategy
from utils.compression_tracker import CompressionTracker
from utils.logger import log_event

class CPRController:
    def __init__(self, config, stop_event=None):
        self.stop_event = stop_event
        self.reader = SerialReader()
        self.processor = PressureMat()
        self.target   = TargetZone()
        self.feedback = FeedbackStrategy.create(config)
        self.compression_tracker  = CompressionTracker()
    
    def shutdown(self):
        # send OFF command to deactivate hardware
        if hasattr(self.feedback, "give_feedback"):
            try:
                self.feedback.give_feedback()
            except Exception as e:
                print(f"warning: failed to send OFF command: {e}")

        self.reader.close()
        print("controller shutdown complete")

    def run(self):
        # start timing
        start_time = time.time()
        last_report = start_time

        try:
            while not (self.stop_event and self.stop_event.is_set()):
                # process all available compressions first
                processed_any = False
                while True:
                    comp = self.reader.read_compression()
                    if comp is None:
                        break

                    depth, ts = comp
                    bpm = self.compression_tracker.record_compression()
                    self.feedback.give_feedback(depth=depth, timestamp=ts)
                    log_event(matrix=None, depth=depth, bpm=bpm)
                    processed_any = True

                # process all available matrix frames next
                while True:
                    matrix = self.reader.read_matrix()
                    if matrix is None:
                        break
                    processed, (y_cop, x_cop), patch_mask = self.processor.process(matrix)

                    error = None
                    if y_cop is not None and x_cop is not None:
                        error, _ = self.target.compute_error(y_cop, x_cop)

                    self.feedback.give_feedback(cop=(x_cop, y_cop), target=self.target.get_target(), error=error)
                    log_event(matrix, cop=(x_cop, y_cop), error=error)
                    processed_any = True

                # report elapsed time every 5 seconds
                now = time.time()
                if now - last_report >= 5:
                    elapsed = int(now - start_time)
                    print(f"⏱️ elapsed: {elapsed} seconds")
                    last_report = now
                    
                # only pause if _nothing_ was processed this loop
                if not processed_any:
                    time.sleep(0.01)

        except KeyboardInterrupt:
            pass


