import socket
import threading

class EventServer:
    def __init__(self, host='localhost', port=12345, parent = None):
        self.systray = parent
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.server_socket.settimeout(1)
        self.running = True
        print("Waiting for connections...")

    def handle_event(self, data):
        print(f"Event received: {data}")

        if data == "bring_to_front":
            self.systray.bring_to_front()
        elif data == "clean":
            self.systray.clean()


    def client_handler(self, conn):
        while self.running:
            data = conn.recv(1024)
            if not data:
                break
            self.handle_event(data.decode())
        conn.close()

    def start(self):
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                print(f"Conectado a {addr}")
                threading.Thread(target=self.client_handler, args=(conn,)).start()
            except socket.timeout:
                continue
            except OSError:
                break

    def stop(self):
        self.running = False
        self.server_socket.close()
        print("Servidor apagado.")



