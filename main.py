from datetime import datetime, timedelta
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget,QInputDialog, QMessageBox)

# Configuración de correo
EMAIL_CONFIG = {
    'from_email': ' correo del emisor ',
    'password': ' contraseña del correo ',
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'subject': 'Recordatorio de tarea',
}

# Ruta absoluta donde guardar el archivo .json
EMPLOYEE_FILE = '/root/Repositorios/Automatizacion_tareas/info_empleados.json'

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
    
    def add_employee(self):
        """Añade emplados al archivo"""
        username, ok = QInputDialog.getText(None, 'Añadir Empleado', 'Indique el nombre del usuario junto con la primera letra de los apellidos:')
        if ok:
            email, ok = QInputDialog.getText(None, 'Añadir Empleado', 'Introduce el correo del usuario:')
            if ok: 
                self.employees[username.lower()] = email

    def list_employees(self):
        """Lista los empleados guardados"""
        
        employees_text = '\n'.join(f"{i + 1}. {name} - {email}" for i, (name, email) in enumerate(self.employees.items()))
        QMessageBox.information(None, 'Lista de Empleados', employees_text)



class TaskManager:
    """Gestión de tareas."""
    
    def __init__(self, employee_name):
        self.task_file = f'/root/Repositorios/Automatizacion_tareas/{employee_name}.json'
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
    
    def add_task(self):
        """Añade tareas a la lista"""
        task_name, ok = QInputDialog.getText(None, 'Añadir Tarea', 'Indique el nombre de la tarea:')
        if ok:
            priority, ok = QInputDialog.getText(None, 'Añadir Tarea', 'Indique prioridad (1.Alta, 2.Media, 3.Baja):') 
            if ok:
                due_date, ok = QInputDialog.getText(None, 'Añadir Tarea', 'Introduce la fecha de de vencimineto (dd-mm-yy):')
                if ok:                    
                    task = {
                        'task': task_name,
                        'priority': priority,
                        'due_date': due_date,
                        'status': 'Pendiente',
                    }
        self.tasks.append(task)
        self.tasks.sort(key=lambda t: (datetime.strptime(t['due_date'], '%d-%m-%y'), -int(t['priority'])))
        
    
    def complete_task(self):
        """Completa las tareas de la lista"""
        task_index, ok = QInputDialog.getInt(None, 'Añadir Tarea', 'Indique el número de la tarea:')
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index]['status'] = 'Completada'
            print('Tarea marcada como completada.')
        else:
            print('Índice de tarea no válido.')
    
    def delete_task(self):
        """Elimina las tareas de la lista"""
        task_index, ok = QInputDialog.getInt(None, 'Eliminar Tarea', 'Indique el número de la tarea:')
        if 0 <= task_index < len(self.tasks):
            del self.tasks[task_index]
            print('Tarea eliminada correctamente.')
        else:
            print('Índice de tarea no válido.')
    
    def list_tasks(self):
        """Enumera todas las tareas que hay en la lista"""
        tasks_text = '\n'.join(f"{i + 1}. {task['task']} | Prioridad: {task['priority']} | {task['due_date']} | Estado: {task['status']}" for i, task in enumerate(self.tasks))
        QMessageBox.information(None, 'Lista de Tareas', tasks_text)



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


class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()

        self.employee_manager = EmployeeManager(EMPLOYEE_FILE)
        self.email_notifier = EmailNotifier(EMAIL_CONFIG)
        self.reminder_service = ReminderService(self.employee_manager, self.email_notifier)

        # Configuración de la ventana principal
        self.setWindowTitle('Automatización de tareas')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet('background-color: #D5BA98;')
       
        # Configuración del contenedor principal
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Etiqueta de título
        title = QLabel('Bienvenido al gestor de tareas automatizado')
        title.setFont(QFont('Arial', 40, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtítulo
        subtitle = QLabel('Menú principal')
        subtitle.setFont(QFont("Arial", 20))
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Botones organizados en un diseño vertical
        button_layout = QVBoxLayout()
        button_layout.setSpacing(20)

        self.button1 = QPushButton("Añadir empleado")
        self.button1.setStyleSheet("padding: 10px; font-size: 16px; background-color: #000000; color: white; border-radius: 5px;")
        self.button1.clicked.connect(self.employee_manager.add_employee)
        
        self.button2 = QPushButton("Listar empleados")
        self.button2.setStyleSheet("padding: 10px; font-size: 16px; background-color: #000000; color: white; border-radius: 5px;")
        self.button2.clicked.connect(self.employee_manager.list_employees)
        
        self.button3 = QPushButton("Gestionar tareas de un empleado")
        self.button3.setStyleSheet("padding: 10px; font-size: 16px; background-color: #000000; color: white; border-radius: 5px;")
        self.button3.clicked.connect(self.open_task_menu)  

        self.button4 = QPushButton("Verificar y enviar recordatorios")
        self.button4.setStyleSheet("padding: 10px; font-size: 16px; background-color: #000000; color: white; border-radius: 5px;")
        self.button4.clicked.connect(self.reminder_service.check_and_notify)  

        self.button5 = QPushButton("Salir y guardar cambios")
        self.button5.setStyleSheet("padding: 10px; font-size: 16px; background-color: #000000; color: white; border-radius: 5px;")
        self.button5.clicked.connect(self.exit_app)  


        button_layout.addWidget(self.button1)
        button_layout.addWidget(self.button2)
        button_layout.addWidget(self.button3)
        button_layout.addWidget(self.button4)
        button_layout.addWidget(self.button5)
        layout.addLayout(button_layout)

        # Pie de página
        footer = QLabel("© 2025 Mi Aplicación. Todos los derechos reservados.")
        footer.setFont(QFont("Arial", 10))
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: gray;")
        layout.addWidget(footer)

        # Aplicar el diseño al contenedor principal
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_task_menu(self):
        """ Método para abrir la ventana TaskMenu """
        employee_name,ok = QInputDialog.getText(None, 'Accediendo a empleado', 'Indique el nombre del usuario junto con la primera letra de los apellidos:')
        if ok and employee_name in self.employee_manager.employees :
            self.task_manager = TaskManager(employee_name)
            self.task_menu = TaskMenu(employee_name)  # Crear instancia de TaskMenu
            self.task_menu.show()  # Mostrar la ventana
        elif employee_name not in self.employee_manager.employees:
            msg = QMessageBox()
            msg.setWindowTitle("Error")  # Título del mensaje     
            msg.setText("El empleado no está añadido a la lista principal.")  # Contenido del mensaje
            msg.setIcon(QMessageBox.Critical)  # Tipo de mensaje: Error
            msg.setStandardButtons(QMessageBox.Ok)  # Botón de cierre
            msg.exec_()  # Muestra el cuadro de diálogo
    
    def exit_app(self):
        """Método que guarda el archivo.json de los empleado y sale de la app"""
        self.employee_manager.save_employees()
        sys.exit()


class TaskMenu(QWidget):
    def __init__(self,employee_name):
        super().__init__()    
        self.task_manager = TaskManager(employee_name) 
        
        # Configuración de la ventana principal
        self.setWindowTitle('Automatización de tareas')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet('background-color: #D5BA98;')
       
        # Configuración del contenedor principal
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Etiqueta de título
        title = QLabel('Bienvenido al gestor de tareas automatizado')
        title.setFont(QFont('Arial', 40, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtítulo
        subtitle = QLabel(f'Menú de tareas de {employee_name}')
        subtitle.setFont(QFont("Arial", 20))
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Botones organizados en un diseño vertical
        button_layout = QVBoxLayout()
        button_layout.setSpacing(20)

        self.button1 = QPushButton("Añadir tarea")
        self.button1.setStyleSheet("padding: 10px; font-size: 16px; background-color: #000000; color: white; border-radius: 5px;")
        self.button1.clicked.connect(self.task_manager.add_task)

        self.button2 = QPushButton("Completar tarea")
        self.button2.setStyleSheet("padding: 10px; font-size: 16px; background-color: #000000; color: white; border-radius: 5px;")
        self.button2.clicked.connect(self.task_manager.complete_task)

        self.button3 = QPushButton("Eliminar tarea")
        self.button3.setStyleSheet("padding: 10px; font-size: 16px; background-color: #000000; color: white; border-radius: 5px;")
        self.button3.clicked.connect(self.task_manager.delete_task)

        self.button4 = QPushButton("Listar tareas")
        self.button4.setStyleSheet("padding: 10px; font-size: 16px; background-color: #000000; color: white; border-radius: 5px;")
        self.button4.clicked.connect(self.task_manager.list_tasks)

        self.button5 = QPushButton("Volver al menú principal")
        self.button5.setStyleSheet("padding: 10px; font-size: 16px; background-color: #000000; color: white; border-radius: 5px;")
        self.button5.clicked.connect(self.exit_taskmenu)

        button_layout.addWidget(self.button1)
        button_layout.addWidget(self.button2)
        button_layout.addWidget(self.button3)
        button_layout.addWidget(self.button4)
        button_layout.addWidget(self.button5)
        layout.addLayout(button_layout)

        # Pie de página
        footer = QLabel("© 2025 Mi Aplicación. Todos los derechos reservados.")
        footer.setFont(QFont("Arial", 10))
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: gray;")
        layout.addWidget(footer)

        # Aplicar el diseño al contenedor principal
        self.setLayout(layout)
    
    def exit_taskmenu(self):
        self.task_manager.save_tasks()
        self.close()



if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())



