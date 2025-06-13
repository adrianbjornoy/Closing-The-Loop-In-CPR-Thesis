import argparse
import threading

from utils.plot_matrix import plot_matrix
from utils.plot_depth import plot_depth_stream
from controllers.cpr_controller import CPRController
from feedback.screen_feedback import ScreenFeedback
from config import config

def feedback_mode():
    """ Runs the real-time feedback system. """
    stop_event = threading.Event()
    controller = CPRController(config, stop_event)
    try:
        # start screen feedback in main thread if active
        if isinstance(controller.feedback, ScreenFeedback):
            controller_thread = threading.Thread(target=controller.run, daemon=True)
            controller_thread.start()
            controller.feedback.set_stop_event(stop_event)
            controller.feedback.start()
            controller_thread.join()

        else:
            controller.run()
    except KeyboardInterrupt:
        print("\n🔴 received exit signal")
    finally:
        controller.shutdown()
        from utils.logger import LOG_PATH
        if LOG_PATH:
            print(f"✅ log saved to {LOG_PATH}")


def app():
    """ Determines mode and runs either feedback or plot mode. """
    parser = argparse.ArgumentParser(description="CPR Feedback System")
    parser.add_argument("--mode", choices=["feedback", "plot"], default=config.get("app_mode", "feedback"),
                        help="Choose mode: feedback (default) or plot")
    args = parser.parse_args()

    print(f"STARTING IN MODE: {args.mode}")

    if args.mode == "plot_position":
        plot_matrix()
    elif args.mode == "plot_depth":
        plot_depth_stream()
    elif args.mode == "feedback":
        feedback_mode() 
    else:
        print("Invalid mode")
        return None
    
    return None
