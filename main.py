from datetime import datetime, timedelta
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuración de correo
EMAIL_CONFIG = {
    'from_email': ' correo del emisor ',
    'password': ' contraseña del correo ',
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'subject': 'Recordatorio de tarea',
}

# Ruta absoluta donde guardar el archivo .json
EMPLOYEE_FILE = '(poner ruta absoluta) /info_empleados.json'

# ------------------------- Clases -------------------------

class EmployeeManager:
    """Gestión de empleados."""
    
    def __init__(self, employee_file):
        self.employee_file = employee_file
        self.employees = self.load_employees()
    
    def load_employees(self):
        """Abre el archivo.json donde se encuentran los empleados y sus correos"""
        try:
            with open(self.employee_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            with open(self.employee_file, 'w') as file:
                json.dump({}, file)
            return {}
    
    def save_employees(self):
        """Guarda el archivo con los empleados"""
        with open(self.employee_file, 'w') as file:
            json.dump(self.employees, file, indent=2)
    
    def add_employee(self, username, email):
        """Añade emplados al archivo"""
        self.employees[username] = email
        print(f'Empleado {username} añadido correctamente.')

    def list_employees(self):
        """Lista los empleados guardados"""
        for i, (username, email) in enumerate(self.employees.items(), start=1):
            print(f"{i}. {username} - {email}")


class TaskManager:
    """Gestión de tareas."""
    
    def __init__(self, employee_name):
        self.task_file = f'/root/Primer-repositorio/{employee_name}.json'
        self.tasks = self.load_tasks()
    
    def load_tasks(self):
        """Abre el archivo.json donde se encuentran las tareas"""
        try:
            with open(self.task_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            with open(self.task_file, 'w') as file:
                json.dump([], file)
            return []
    
    def save_tasks(self):
        """Guarda las tareas en el archivo.json"""
        with open(self.task_file, 'w') as file:
            json.dump(self.tasks, file, indent=2)
    
    def add_task(self, task_name, priority, due_date):
        """Añade tareas a la lista"""
        task = {
            'task': task_name,
            'priority': priority,
            'due_date': due_date,
            'status': 'Pendiente',
        }
        self.tasks.append(task)
        self.tasks.sort(key=lambda t: (datetime.strptime(t['due_date'], '%d-%m-%y'), -int(t['priority'])))
        print('Tarea añadida correctamente.')
    
    def complete_task(self, task_index):
        """Completa las tareas de la lista"""
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index]['status'] = 'Completada'
            print('Tarea marcada como completada.')
        else:
            print('Índice de tarea no válido.')
    
    def delete_task(self, task_index):
        """Elimina las tareas de la lista"""
        if 0 <= task_index < len(self.tasks):
            del self.tasks[task_index]
            print('Tarea eliminada correctamente.')
        else:
            print('Índice de tarea no válido.')
    
    def list_tasks(self):
        """Enumera todas las tareas que hay en la lista"""
        for i, task in enumerate(self.tasks, start=1):
            print(
                f'{i}. {task['task']} | Prioridad: {task['priority']} | '
                f'Vence: {task['due_date']} | Estado: {task['status']}'
            )


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


class ReminderService:
    """Servicio para verificar y enviar recordatorios de tareas."""
    
    def __init__(self, employee_manager, email_notifier):
        self.employee_manager = employee_manager
        self.email_notifier = email_notifier
    
    def check_and_notify(self):
        """Repasa todas las tareas de cada usuario, si estan pendientes y falta menos de 1 dia envia el correo"""
        current_date = datetime.now()
        for employee, email in self.employee_manager.employees.items():
            task_manager = TaskManager(employee)
            for task in task_manager.tasks:
                due_date = datetime.strptime(task['due_date'], '%d-%m-%y')
                if task['status'] == 'Pendiente' and timedelta(0) <= (due_date - current_date) <= timedelta(days=1):
                    message = (f"Hola, recuerda que la tarea '{task['task']}' vence el {task['due_date']}.")
                    self.email_notifier.send_email(email, message)

# ------------------------- Menús -------------------------

def main_menu():
    employee_manager = EmployeeManager(EMPLOYEE_FILE)
    email_notifier = EmailNotifier(EMAIL_CONFIG)
    reminder_service = ReminderService(employee_manager, email_notifier)
    
    while True:
        print('\n--- Menú Principal ---')
        print('1. Añadir empleado')
        print('2. Listar empleados')
        print('3. Gestionar tareas de un empleado')
        print('4. Verificar y enviar recordatorios')
        print('5. Salir')
        
        choice = input('Selecciona una opción: ')
        
        if choice == '1':
            username = input('Indique el nombre del usuario junto con la primera letra de los apellidos: ')
            email = input('Correo del usuario: ')
            employee_manager.add_employee(username.lower(), email)
        elif choice == '2':
            employee_manager.list_employees()
        elif choice == '3':
            username = input('Nombre de usuario: ')
            if username in employee_manager.employees:
                task_menu(username)
            else:
                print('Empleado no encontrado.')
        elif choice == '4':
            reminder_service.check_and_notify()
        elif choice == '5':
            employee_manager.save_employees()
            print('Adiós.')
            break
        else:
            print('Opción no válida.')

def task_menu(username):
    task_manager = TaskManager(username)
    
    while True:
        print('\n--- Menú de Tareas ---')
        print('1. Añadir tarea')
        print('2. Completar tarea')
        print('3. Eliminar tarea')
        print('4. Listar tareas')
        print('5. Volver al menú principal')
        
        choice = input('Selecciona una opción: ')
        
        if choice == '1':
            task_name = input('Descripción de la tarea: ')
            priority = input('Prioridad (1. Alta, 2. Media, 3. Baja): ')
            due_date = input('Fecha de vencimiento (dd-mm-yy): ')
            task_manager.add_task(task_name, priority, due_date)
        elif choice == '2':
            task_manager.list_tasks()
            task_index = int(input('Índice de la tarea a completar: ')) - 1
            task_manager.complete_task(task_index)
        elif choice == '3':
            task_manager.list_tasks()
            task_index = int(input('ndice de la tarea a eliminar: ')) - 1
            task_manager.delete_task(task_index)
        elif choice == '4':
            task_manager.list_tasks()
        elif choice == '5':
            task_manager.save_tasks()
            break
        else:
            print('Opción no válida.')

if __name__ == '__main__':
    main_menu()