import socket, pyodbc, jsonpickle

PATH = '127.0.0.1'
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((PATH, PORT))
server.listen(1)

print("Server is running...")
try:
   conn, addr = server.accept()

   print(f"Connection from {addr} has been established!")
except ConnectionError:
   print("Client can't connect to server")



server.close()