import socket, pyodbc, jsonpickle, json
from dataclasses import dataclass

PATH = '127.0.0.1'
PORT = 12345

server = 'localhost'
database = 'TestsBase'
username = ''
password = ''
dsn = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Trusted_Connection=yes;'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((PATH, PORT))
server.listen(1)

print("Server is running...")
try:
   conn, addr = server.accept()

   print(f"Connection from {addr} has been established!")
except ConnectionError:
   print("Client can't connect to server")

@dataclass
class User:
   login: str
   password: str
   age: int
   action: str


buffer = ""

while True:
   try:
    data = conn.recv(1024)

    if not data:
       print("Server closinng...")
       break
    
    buffer += data.decode()

    try:
       
       parsed = json.loads(buffer)

       user = User (
          login = parsed.get("login"),
          password = parsed.get("password"),
          age=int(parsed.get("age", 0)) if parsed.get("age") else 0,
          action=parsed.get("action")
       )

       print(f"User: {user}")

       # Adding User to DataBase
       conn_bd = pyodbc.connect(dsn)
       cursor = conn_bd.cursor()
       if user.action == 'Register':

          cursor.execute("INSERT INTO Users ([Login], [Password], [Age]) VALUES (?, ?, ?)",
          user.login,
          user.password,
          user.age) 
          
          conn_bd.commit()
          print("User was inserted into database!")

          cursor.close()
          conn_bd.close()
       else:
        print('Login')


    except Exception as e:
       print(f"Error: {e}")

   except Exception as e:
      print(f"Error: {e}")

server.close()