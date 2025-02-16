from datetime import datetime, timedelta
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuración de correo
EMAIL_CONFIG = {
    'from_email': ' correo del emisor ', # RELLENAR
    'password': ' contraseña del correo ', # RELLENAR
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'subject': 'Recordatorio de tarea',
}

# Ruta absoluta donde guardar el archivo .json
employee_file = '(poner ruta absoluta) /info_empleados.json' # RELLENAR

class EmailNotifier:
    """Clase para manejar notificaciones por correo."""
    
    def __init__(self, config):
        self.config = config
    
    def send_email(self, to_email, message):
        """Envia el email al usuario correspondiente"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['from_email']
            msg["To"] = to_email
            msg['Subject'] = self.config['subject']
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['from_email'], self.config['password'])
            server.send_message(msg)
            server.quit()
            print(f'Correo enviado a {to_email}')
        except Exception as e:
            print(f'Error al enviar correo: {e}')

def load_employees(employee_file):
        """Abre el archivo.json donde se encuentran los empleados y sus correos"""
        try:
            with open(employee_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            with open(employee_file, 'w') as file:
                json.dump({}, file)
            return {}

def load_tasks(employee):
        """Abre el archivo.json donde se encuentran las tareas"""
        task_file = f'/(poner ruta absoluta)/{employee}.json' # RELLENAR
        try:
            with open(task_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            with open(task_file, 'w') as file:
                json.dump([], file)
            return []
    
def check_and_notify(employees, email_notifier):
    """Repasa todas las tareas de cada usuario, si estan pendientes y falta menos de 1 dia envia el correo"""
    current_date = datetime.now()
    for employee, email in employees.items():
        tasks = load_tasks(employee)
        for task in tasks:
            due_date = datetime.strptime(task['due_date'], '%d-%m-%y')
            if task['status'] == 'Pendiente' and timedelta(0) <= (due_date - current_date) <= timedelta(days=1):
                message = (f"Hola, recuerda que la tarea '{task['task']}' vence el {task['due_date']}.")
                email_notifier.send_email(email, message)


if __name__ == '__main__':
    employees = load_employees(employee_file)
    check_and_notify(employees, EmailNotifier)
