from localrecall import ActivityTracker

def get_compression_settings():
    compress = input("Do you want to compress screenshots? (y/n, default: n): ").lower() == 'y'
    compress_quality = 85
    resize_factor = 1.0
    if compress:
        while True:
            try:
                compress_quality = int(input("Enter compression quality (1-100, default: 85): ") or 85)
                if 1 <= compress_quality <= 100:
                    break
                else:
                    print("Please enter a number between 1 and 100.")
            except ValueError:
                print("Please enter a valid number.")
        
        while True:
            try:
                resize_factor = float(input("Enter resize factor (0.1-1.0, default: 1.0): ") or 1.0)
                if 0.1 <= resize_factor <= 1.0:
                    break
                else:
                    print("Please enter a number between 0.1 and 1.0.")
            except ValueError:
                print("Please enter a valid number.")
    
    return compress, compress_quality, resize_factor

def main():
    compress, compress_quality, resize_factor = get_compression_settings()
    tracker = ActivityTracker(compress=compress, compress_quality=compress_quality, resize_factor=resize_factor)
    tracker.run()

if __name__ == "__main__":
    main()