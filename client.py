import socket
from tkinter import *

root = Tk()
root.geometry("500x500")
root.title("Register")

PATH = '127.0.0.1'
PORT = 12345

  
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((PATH, PORT))

response = client.recv(1024).decode()
client.send(response.encode())

root.mainloop()
client.close()