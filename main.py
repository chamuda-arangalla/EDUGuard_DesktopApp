from src.camera.webcam_processor import WebcamProcessor

def main():
    try:
        processor = WebcamProcessor()
        processor.start()
    except Exception as e:
        print(f"Error: {str(e)}")
        
if __name__ == "__main__":
    main()