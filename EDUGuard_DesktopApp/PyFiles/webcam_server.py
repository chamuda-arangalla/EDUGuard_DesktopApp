import cv2
import socket
import struct
import pickle

# Socket setup
HOST = '127.0.0.1'
PORT = 9999

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Bind the server socket
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print("Webcam server started. Waiting for connections...")
except socket.error as e:
    print(f"Socket error: {e}")
    server_socket.close()
    exit(1)

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    server_socket.close()
    exit(1)

try:
    while True:
        try:
            client_socket, addr = server_socket.accept()
            print(f"Connection from: {addr}")
        except socket.error as e:
            print(f"Error accepting connection: {e}")
            continue

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Error: Failed to capture frame from webcam.")
                    break

                # Serialize the frame
                data = pickle.dumps(frame, protocol=pickle.HIGHEST_PROTOCOL)
                message = struct.pack("Q", len(data)) + data

                try:
                    client_socket.sendall(message)
                except BrokenPipeError:
                    print("Client disconnected.")
                    break

        except Exception as e:
            print(f"Error during frame processing: {e}")
        finally:
            client_socket.close()

except KeyboardInterrupt:
    print("Shutting down server due to KeyboardInterrupt.")
finally:
    cap.release()
    server_socket.close()
    print("Server shut down.")
