from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = FastAPI()

class User(BaseModel):
    id: int
    full_name: str
    password: str
    email: str
    role: str

class Task(BaseModel):
    id: int
    task_time: str
    task_title: str
    task_subject: str
    status: str  # Yeni olarak eklenen status parametresi
    is_deleted: bool = False  # Yeni olarak eklenen is_deleted parametresi

users = []
tasks = []

def send_email(user_email):
    # E-posta gönderen bilgileri
    sender_email = "example@gmail.com"  # Kendi e-posta adresinizi girin
    sender_password = "password"   # E-posta şifrenizi girin

    # E-posta başlık ve içeriği
    subject = "New Task Added"
    body = "Başarılı!"

    # E-posta oluşturma ve biçimlendirme
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = user_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # SMTP sunucusuna bağlanma ve e-posta gönderme
    with smtplib.SMTP('smtp.gmail.com', 587) as server:  # SMTP sunucu bilgilerinizi girin
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, user_email, text)

def login_check(email: str, password: str):
    for user in users:
        if user.email == email and user.password == password:
            return user.role
    return None

@app.post("/add_user/")
def add_user(user: User):
    users.append(user)
    return {"message": "User added successfully"}

@app.post("/add_task/")
def add_task(email: str, password: str, task: Task):
    role = login_check(email, password)
    if not role:
        raise HTTPException(status_code=401, detail="Login failed")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can add tasks")
    tasks.append(task)
    for user in users:
        #send_email(user.email)
        pass
    return {"message": "Task added successfully"}

@app.put("/update_task/{task_id}")
def update_task(email: str, password: str, task_id: int, updated_task: Task):
    role = login_check(email, password)
    if not role:
        raise HTTPException(status_code=401, detail="Login failed")
    if role == "admin":
        for task in tasks:
            if task.id == task_id:
                task.task_time = updated_task.task_time
                task.task_title = updated_task.task_title
                task.task_subject = updated_task.task_subject
                task.status = updated_task.status  # Sadece admin tüm alanları güncelleyebilir
                return {"message": f"Task {task_id} updated successfully"}
    else:
        for task in tasks:
            if task.id == task_id:
                task.status = updated_task.status  # Sadece status alanı güncellenebilir
                return {"message": f"Task {task_id} status updated successfully"}
    raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

@app.delete("/delete_task/{task_id}")
def delete_task(email: str, password: str, task_id: int):
    role = login_check(email, password)
    if not role:
        raise HTTPException(status_code=401, detail="Login failed")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete tasks")
    for task in tasks:
        if task.id == task_id:
            task.is_deleted = True
            return {"message": f"Task {task_id} deleted successfully"}
    raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
