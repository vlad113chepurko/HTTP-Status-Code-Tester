import socket, json
import tkinter as tk
from tkinter import messagebox

PATH = '127.0.0.1'
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((PATH, PORT))

root = tk.Tk()
root.geometry("400x300")
root.title("Login/Register")

fm = tk.Frame(root)
fm.place(relx=0.5, rely=0.5, anchor='center')

class Forma:
    def __init__(self, parent):
        self.parent = parent

    def destroyWidgets(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

    def createItems(self, isLogin=True):
        self.destroyWidgets()
        tk.Label(self.parent, text="Login").grid(row=0, column=0, columnspan=2)
        login = tk.Entry(self.parent)
        login.grid(row=1, column=0, columnspan=2)

        tk.Label(self.parent, text="Password").grid(row=2, column=0, columnspan=2)
        password = tk.Entry(self.parent, show='*')
        password.grid(row=3, column=0, columnspan=2)

        age = None
        if not isLogin:
            tk.Label(self.parent, text="Age").grid(row=4, column=0, columnspan=2)
            age = tk.Entry(self.parent)
            age.grid(row=5, column=0, columnspan=2)

        def submit():
            data = {
                "login": login.get(),
                "password": password.get(),
                "action": "Login" if isLogin else "Register"
            }
            if age: data["age"] = age.get()
            client.send(json.dumps(data).encode())
            response = json.loads(client.recv(4096).decode())
            messagebox.showinfo("Info", response.get("message"))
            if response.get("status") in ["success", "admin"]:
                self.userPanel()

        tk.Button(self.parent, text="Submit", command=submit).grid(row=6, column=0)
        tk.Button(self.parent, text="Switch", command=lambda: self.createItems(not isLogin)).grid(row=6, column=1)

    def userPanel(self):
        self.destroyWidgets()
        tk.Button(self.parent, text="Start Test", command=self.startTest).pack()

    def startTest(self):
        self.destroyWidgets()
        client.send(json.dumps({"action": "startTest"}).encode())
        resp = json.loads(client.recv(8192).decode())
        self.questions = resp["questions"]
        self.answers = resp["answers"]
        self.index = 0
        self.userAnswers = {}
        self.renderQuestion()

    def renderQuestion(self):
        self.destroyWidgets()
        if self.index >= len(self.questions):
            return self.finishTest()

        q = self.questions[self.index]
        tk.Label(self.parent, text=q["QuestionText"], wraplength=350).pack(pady=5)
        self.ans_var = tk.IntVar()

        for a in self.answers[str(q["QuestionId"])]:
            tk.Radiobutton(self.parent, text=a["AnswerText"], variable=self.ans_var, value=a["AnswerId"]).pack(anchor="w")

        tk.Button(self.parent, text="Next", command=self.nextQuestion).pack(pady=5)

    def nextQuestion(self):
        self.userAnswers[self.questions[self.index]["QuestionId"]] = self.ans_var.get()
        self.index += 1
        self.renderQuestion()

    def finishTest(self):
        client.send(json.dumps({"action": "submitTest", "answers": self.userAnswers}).encode())
        result = json.loads(client.recv(4096).decode())

        if result.get("status") == "ok" and "score" in result:
           messagebox.showinfo("Result", f"Score: {result['score']}%")
        else:
           messagebox.showerror("Error", result.get("message", "Something went wrong"))

        self.userPanel()

forma = Forma(fm)
forma.createItems()

root.protocol("WM_DELETE_WINDOW", lambda: (client.close(), root.destroy()))
root.mainloop()
