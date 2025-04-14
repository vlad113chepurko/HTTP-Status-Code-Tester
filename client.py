import socket, json
import tkinter as tk

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

    def createItems(self, isLogin=True):

        for widget in self.parent.winfo_children():
            widget.destroy()

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
            age = e_age.get() if e_age else None
        ))
        submit_btn.grid(column=0, row=row_offset, pady=10)

        toggle_btn = tk.Button(
            self.parent,
            text="Register" if isLogin else "Login",
            command=lambda: self.createItems(not isLogin)
        )
        toggle_btn.grid(column=1, row=row_offset)

    def handleSubmit(self, login, password, age=None):
        data = {
          "login": f"{login}",
          "password": f"{password}"
        }
        if age is not None:
            data["age"] = age

        json_data = json.dumps(data)
        print(f"Data to send: {json_data}")
        client.send(json_data.encode())


forma = Forma(fm)
forma.createItems(isLogin=True)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((PATH, PORT))

root.mainloop()
client.close()