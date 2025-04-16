import socket, json
import tkinter as tk
from tkinter import messagebox

PATH = '127.0.0.1'
PORT = 12345

root = tk.Tk()
root.geometry("400x250")
root.title("Register/Login")


fm = tk.Frame(root)
fm.place(relx=0.5, rely=0.5, anchor='center')

class Forma:
    def __init__(self, parent_frame):
        self.parent = parent_frame

    def destroyWidgets(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

    def createItems(self, isLogin=True):

        self.destroyWidgets()

        # Login
        l_login = tk.Label(self.parent, text="Enter login")
        l_login.grid(column=0, row=0, columnspan=2, pady=5)
        e_login = tk.Entry(self.parent)
        e_login.grid(column=0, row=1, columnspan=2, pady=5)

        # Password
        l_password = tk.Label(self.parent, text="Enter password")
        l_password.grid(column=0, row=2, columnspan=2, pady=5)
        e_password = tk.Entry(self.parent, show="*")
        e_password.grid(column=0, row=3, columnspan=2, pady=5)

        row_offset = 4
        e_age = None
       
        # Register form
        if not isLogin:
            l_age = tk.Label(self.parent, text="Enter age")
            l_age.grid(column=0, row=row_offset, columnspan=2, pady=5)
            e_age = tk.Entry(self.parent)
            e_age.grid(column=0, row=row_offset+1, columnspan=2, pady=5)
            row_offset += 2

        # Buttons
        submit_btn = tk.Button(self.parent, text="Submit", command=lambda: self.handleSubmit(
            login = e_login.get(),
            password = e_password.get(),
            age = e_age.get() if e_age else None,
            action = 'Login' if isLogin else 'Register'
        ))
        submit_btn.grid(column=0, row=row_offset, pady=10)

        toggle_btn = tk.Button(
            self.parent,
            text="Register" if isLogin else "Login",
            command=lambda: self.createItems(not isLogin)
        )
        toggle_btn.grid(column=1, row=row_offset)

    def handleSubmit(self, login, password, action, age=None):
        
        data = {
          "login": f"{login}",
          "password": f"{password}",
          "action": f"{action}"
        }

        if age is not None:
            data["age"] = age

        json_data = json.dumps(data)
        print(f"Data to send: {json_data}")
        client.send(json_data.encode())
        
        # Accept response from server
        try:
            response_data = client.recv(1024).decode()
            response = json.loads(response_data)
            tk.messagebox.showinfo("Server Resp: ", response.get("message", "No message"))
            self.destroyWidgets()
            if response.get("status") == "admin":
                print("You are admin!")
            else:
                print("You are user")
                self.userPanel()
        except Exception as e:
            print(f"Error: {e}")

    def handleStatusTest(self, numbe_test):
        if numbe_test == 1:
            self.destroyWidgets()
            root.title("Test status code 100")
            tk.Label(text="Status code 100 test", font='Arial 12').grid(row=1, column=1)



    def userPanel(self):
        test_1 = tk.Button(self.parent, text="Status code 100", command=lambda:self.handleStatusTest(1))
        test_1.grid(column=0, row=0, pady=10)


forma = Forma(fm)
forma.createItems(isLogin=True)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((PATH, PORT))

root.mainloop()
client.close()