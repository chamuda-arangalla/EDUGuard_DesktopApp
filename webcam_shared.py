import cv2
import socket
import struct
import pickle
import signal
import sys

# Handle termination signals (SIGINT, SIGTERM)
def handle_exit(signum, frame):
    print("Termination signal received. Exiting cleanly.")
    cap.release()
    server_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# Socket setup
HOST = '127.0.0.1'
PORT = 9999

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print("Webcam server started. Waiting for connections...")

# Open webcam
cap = cv2.VideoCapture(0)

try:
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from: {addr}")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Serialize the frame
            data = pickle.dumps(frame)
            message = struct.pack("Q", len(data)) + data

            try:
                client_socket.sendall(message)
            except BrokenPipeError:
                break

        client_socket.close()
except KeyboardInterrupt:
    print("Shutting down server.")
finally:
    cap.release()
    server_socket.close()
