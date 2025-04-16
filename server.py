import socket, pyodbc, json
from dataclasses import dataclass

# server
PATH = '127.0.0.1'
PORT = 12345

# database
server = 'localhost'
database = 'TestsBase'
username = ''
password = ''
dsn = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Trusted_Connection=yes;'

@dataclass
class User:
    login: str
    password: str
    age: int
    action: str

# <---------------------------------------------------------------->
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((PATH, PORT))
server_socket.listen(1)
print("Server is running...")

conn, addr = server_socket.accept()
print(f"Connection from {addr} has been established!")

buffer = ""
# <---------------------------------------------------------------->

while True:
    try:
        data = conn.recv(1024)
        if not data:
            print("Client disconnected. Closing server...")
            break

        buffer += data.decode()
        
        #Loads data from buffer
        try:
            parsed = json.loads(buffer)
            buffer = "" 

            user = User(
                login=parsed.get("login"),
                password=parsed.get("password"),
                age=int(parsed.get("age", 0)) if parsed.get("age") else 0,
                action=parsed.get("action")
            )

            print(f"Received user: {user}")

            conn_bd = pyodbc.connect(dsn)
            cursor = conn_bd.cursor()
            
            # response for send it to client in JSON
            response = {}

            if user.action == 'Register':
                cursor.execute("INSERT INTO Users ([Login], [Password], [Age]) VALUES (?, ?, ?)",
                               (user.login, user.password, user.age))
                conn_bd.commit()
                response = {"status": "success", "message": "User was inserted into database!"}

            # Login   
            else:  
               if user.login == 'admin' and user.password == 'admin':
                  response = {"status": "admin", "message": "You are admin!"}
               else:
                  cursor.execute("SELECT * FROM Users WHERE [Login] = ? AND [Password] = ?",
                                 (user.login, user.password))
                  result = cursor.fetchone()
                  if result:
                     response = {"status": "success", "message": "You were logged in!"}
                  else:
                     response = {"status": "error", "message": "Login or password is incorrect"}

            conn.sendall(json.dumps(response).encode())

            cursor.close()
            conn_bd.close()

        except json.JSONDecodeError:
            continue  
        except Exception as e:
            print(f"Inner error: {e}")
            conn.sendall(json.dumps({"status": "error", "message": str(e)}).encode())

    except Exception as e:
        print(f"Outer error: {e}")
        break

conn.close()
server_socket.close()
