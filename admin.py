import socket
from tkinter import *

root = Tk()
root.geometry("500x500")
root.title("Register")

PATH = '127.0.0.1'
PORT = 12345

  
admin = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
admin.connect((PATH, PORT))

response = admin.recv(1024).decode()
admin.send(response.encode())

root.mainloop()
admin.close()