import argparse
import threading
from .activity_tracker import ActivityTracker
from .vision_processor import VisionProcessor
from .utils import load_env_variables
import time
import uvicorn
from .chat_api import app as api_app

def run_tracker(compress=False, compress_quality=85, resize_factor=1.0):
    tracker = ActivityTracker(compress=compress, compress_quality=compress_quality, resize_factor=resize_factor)
    print("Starting activity tracking...")
    tracker.run()

def run_processor(strategy="google"):
    processor = VisionProcessor(strategy)
    print("Processing unprocessed activities...")
    try:
        while True:
            processor.process_unprocessed_activities()
            if strategy == "local":
                continue
            time.sleep(10)
    except Exception as e:
        print(f"Error: {str(e)}")
    print("Processing complete.")

def run_api_server(host="0.0.0.0", port=11011):
    uvicorn.run(api_app, host=host, port=port)

def main():
    parser = argparse.ArgumentParser(description="LocalRecall: Activity Tracker and Image Processor")
    parser.add_argument("--track", action="store_true", help="Run activity tracking")
    parser.add_argument("--process", action="store_true", help="Run image processing")
    parser.add_argument("--api", action="store_true", help="Run API server")
    parser.add_argument("--compress", action="store_true", help="Compress screenshots")
    parser.add_argument("--compress-quality", type=int, default=85, choices=range(1, 101), metavar="[1-100]", help="Compression quality (default: 85)")
    parser.add_argument("--resize-factor", type=float, default=1.0, choices=[i/10 for i in range(1, 11)], metavar="[0.1-1.0]", help="Resize factor (default: 1.0)")
    parser.add_argument("--vision-strategy", choices=["google", "local"], default="google", help="Vision processing strategy (default: google)")
    parser.add_argument("--api-host", type=str, default="0.0.0.0", help="API server host (default: 0.0.0.0)")
    parser.add_argument("--api-port", type=int, default=11011, help="API server port (default: 11011)")

    args = parser.parse_args()

    load_env_variables()

    threads = []

    if args.track:
        tracker_thread = threading.Thread(target=run_tracker, kwargs={
            "compress": args.compress,
            "compress_quality": args.compress_quality,
            "resize_factor": args.resize_factor
        })
        threads.append(tracker_thread)

    if args.process:
        processor_thread = threading.Thread(target=run_processor, kwargs={
            "strategy": args.vision_strategy
        })
        threads.append(processor_thread)

    if args.api:
        api_thread = threading.Thread(target=run_api_server, kwargs={
            "host": args.api_host,
            "port": args.api_port
        })
        threads.append(api_thread)

    if not threads:
        print("No action specified. Use --track to start tracking or --process to start processing.")
        return

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
