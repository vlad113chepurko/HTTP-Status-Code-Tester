import socket, pyodbc, json
from dataclasses import dataclass

PATH = '127.0.0.1'
PORT = 12345

server = 'localhost'
database = 'TestsBase'
dsn = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

@dataclass
class User:
    login: str
    password: str
    age: int
    action: str

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((PATH, PORT))
server_socket.listen(1)
print("Server is running...")

conn, addr = server_socket.accept()
print(f"Connection from {addr} has been established!")

buffer = ""

while True:
    try:
        data = conn.recv(4096)
        if not data:
            print("Client disconnected. Closing server...")
            break

        buffer += data.decode()

        try:
            parsed = json.loads(buffer)
            buffer = ""

            conn_bd = pyodbc.connect(dsn)
            cursor = conn_bd.cursor()

            if parsed.get("action") == "Register":
                cursor.execute("INSERT INTO Users ([Login], [Password], [Age]) VALUES (?, ?, ?)",
                               (parsed["login"], parsed["password"], int(parsed.get("age", 0))))
                conn_bd.commit()
                conn.sendall(json.dumps({"status": "success", "message": "User registered!"}).encode())

            elif parsed.get("action") == "Login":
                if parsed["login"] == "admin" and parsed["password"] == "admin":
                    conn.sendall(json.dumps({"status": "admin", "message": "You are admin!"}).encode())
                else:
                    cursor.execute("SELECT * FROM Users WHERE [Login] = ? AND [Password] = ?",
                                   (parsed["login"], parsed["password"]))
                    result = cursor.fetchone()
                    if result:
                        conn.sendall(json.dumps({"status": "success", "message": "Logged in!"}).encode())
                    else:
                        conn.sendall(json.dumps({"status": "error", "message": "Login or password incorrect"}).encode())

            elif parsed.get("action") == "startTest":
                cursor.execute("SELECT * FROM Questions")
                questions = [{"QuestionId": row.QuestionId, "QuestionText": row.QuestionText} for row in cursor.fetchall()]

                answers = {}
                for q in questions:
                    cursor.execute("SELECT * FROM Answers WHERE QuestionId = ?", (q["QuestionId"],))
                    answers[str(q["QuestionId"])] = [
                        {"AnswerId": row.AnswerId, "AnswerText": row.AnswerText, "isCorrect": bool(row.isCorrect)}
                        for row in cursor.fetchall()
                    ]

                conn.sendall(json.dumps({"status": "ok", "questions": questions, "answers": answers}).encode())

            elif parsed.get("action") == "submitTest":
                answers = parsed.get("answers", {})
                correct_count = 0

                for qid_str, aid in answers.items():
                    cursor.execute("SELECT isCorrect FROM Answers WHERE AnswerId = ?", (aid,))
                    row = cursor.fetchone()
                    is_correct = row.isCorrect if row else False

                    correct_count += int(is_correct)
                    cursor.execute("INSERT INTO AnswerLogs (AnswerId, AnswersStatus) VALUES (?, ?)", (aid, is_correct))

                total = len(answers)
                procent = int((correct_count / total) * 100) if total > 0 else 0

                userId = 1
                testId = 1
                cursor.execute("INSERT INTO Results (UserId, TestId, ResultDate, ProcentOfCorrectAnswers) VALUES (?, ?, GETDATE(), ?)",
                               (userId, testId, procent))
                conn_bd.commit()
                conn.sendall(json.dumps({"status": "ok", "score": procent}).encode())

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
