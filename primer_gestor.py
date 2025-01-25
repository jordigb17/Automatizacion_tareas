import json
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuración de correo
from_email = ''  # Dirección de correo de la empresa
asunto = 'Recordatorio de tarea'  # Asunto del correo
psw = ''  # Contraseña correo empresa

# Ruta de archivo donde se guradan los empleados 
filename_empleado = '//info_empleados.json'

# Variables globales
empleados = {}  # Información de los empleados


def cargar_empleados():
    """Carga los empleados desde el archivo JSON."""
    try:
        with open(filename_empleado, 'r') as f_obj:
            contenido = json.load(f_obj)
            print('Abriendo archivo de empleados')
            for usuario, correo in contenido.items():
                empleados[usuario] = correo
    except FileNotFoundError:
        with open(filename_empleado, 'w') as f_obj:
            print('Creando nuevo archivo de empleados')


def cargar_tareas(archivo_tareas):
    """Carga las tareas desde el archivo JSON del empleado específico."""
    tareas = []  # Lista local para las tareas del empleado
    try:
        with open(archivo_tareas, 'r') as f_obj:
            contenido = json.load(f_obj)
            print(f'Abriendo archivo de tareas para {archivo_tareas}')
            for linea in contenido:
                tareas.append(linea)
    except Exception:
        with open(archivo_tareas, 'w') as f_obj:
            print(f'Creando nuevo archivo de tareas para {archivo_tareas}')
            json.dump(tareas,f_obj,indent = 2)
    return tareas


def guardar_tareas(archivo_tareas, tareas):
    """Guarda las tareas en el archivo JSON del empleado específico."""
    with open(archivo_tareas, 'w') as f_obj:
        json.dump(tareas, f_obj, indent=2)
        print(f'Tareas de {archivo_tareas} guardadas correctamente')


def añadir_tarea(tareas):
    """Añadir una tarea a la lista y ordenarla."""
    dict_tarea = {}
    dict_tarea['tarea'] = input('Indique la tarea que desea añadir: ')
    dict_tarea['prioridad'] = input('Indique la prioridad de la tarea: \n1. Alta\n2. Media\n3. Baja\nPrioridad: ')
    dict_tarea['vencimiento'] = input('Indique fecha de vencimiento en este formato (dd-mm-yy): ')
    dict_tarea['estado'] = 'Pendiente'
    tareas.append(dict_tarea)
    tareas.sort(key=lambda tarea: (datetime.strptime(tarea['vencimiento'], '%d-%m-%y'), -int(tarea['prioridad'])))
    print('Tarea añadida')


def completar_tarea(tareas):
    """Marca la tarea como completada."""
    
    try:
        numero = int(input('Indique el número de la tarea que ha completado: '))
        if 0 < numero <= len(tareas):
            numero -= 1
            tareas[numero]['estado'] = 'Completada'
            print('Tarea marcada como completada')
        else:
            print('El número indicado no coincide con ninguna tarea')
    except ValueError:
        print('Debe introducir un número')


def eliminar_tarea(tareas):
    """Eliminar tarea de la lista."""
    try:
        numero = int(input('Indique el número de la tarea que desea eliminar: '))
        if 0 < numero <= len(tareas):
            numero -= 1
            del tareas[numero]
            print('Tarea eliminada')
        else:
            print('El número indicado no coincide con ninguna tarea')
    except ValueError:
        print('Debe introducir un número')



def mostrar_tareas(tareas):
    """Muestra las tareas en formato legible."""
    print('--LISTA DE TAREAS--')
    for i, tarea in enumerate(tareas, 1):
        print(f"{i}. Tarea: {tarea['tarea']}")
        print(f"Prioridad: {tarea['prioridad']}")
        print(f"Vencimiento: {tarea['vencimiento']}")
        print(f"Estado: {tarea['estado']}")
        print("-" * 40)


def verificar_recordar():
    """Verifica las tareas pendientes y envía recordatorios por correo."""
    fecha_actual = datetime.now()

    for empleado, to_email  in empleados.items():
        archivo_tareas = f'C:/Users/jordi/OneDrive/Escritorio/CONQUERBLOCKS/archivos_secundarios/empleados/{empleado}.json'
        tareas = cargar_tareas(archivo_tareas)

        for tarea in tareas:
            fecha_vencimiento = datetime.strptime(tarea['vencimiento'], '%d-%m-%y')
            diferencia = fecha_vencimiento - fecha_actual
        
            if timedelta(days=0) <= diferencia <= timedelta(days=1) and tarea['estado'] == 'Pendiente':
                mensaje = f'Hola, recuerda que la tarea "{tarea["tarea"]}" vence el {tarea["vencimiento"]}'
                enviar_correo(to_email, mensaje)


def enviar_correo(to_email, mensaje):
    """Envía un correo de recordatorio."""
    try:
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = asunto
        msg.attach(MIMEText(mensaje, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, psw)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Correo enviado con éxito")
    except Exception as error:
        print(f'Error al enviar el correo: {error}')


def acceso_tareas_user():
    """Permite al usuario acceder a sus tareas."""
    nombre = input('Indique el nombre del empleado seguido de la primera letra de cada apellido: ').lower()
    if nombre not in empleados:
        print('El empleado no está registrado en la base de datos.')
    else:
        to_email = empleados[nombre]
        archivo_tareas = f'/root/Primer-repositorio/{nombre}.json'
        tareas = cargar_tareas(archivo_tareas)
        menu_tareas(tareas, archivo_tareas, to_email)


def guardar_empleados():
    """Guarda los empleados en el archivo JSON."""
    with open(filename_empleado, 'w') as f_obj:
        json.dump(empleados, f_obj, indent=2)
        print('Empleados guardados correctamente')


def añadir_empleado():
    """Añadir un nuevo empleado."""
    usuario = input('Escriba el nombre de usuario seguido de la primera letra de los dos apellidos: ').lower()
    correo = input('Escriba el correo del usuario: ')
    empleados[usuario] = correo
    print('Empleado añadido')


def menu_tareas(tareas, archivo_tareas, to_email):
    """Menú de gestión de tareas."""
    while True:
        print()
        print('---Menú de gestión de tareas---')
        print()
        accion = input('1. Añadir tarea\n2. Completar tarea\n3. Eliminar tarea\n4. Mostrar tareas\n5. Salir\nNúmero: ')
        
        if accion == '1':
            añadir_tarea(tareas)
        elif accion == '2':
            completar_tarea(tareas)
        elif accion == '3':
            eliminar_tarea(tareas)
        elif accion == '4':
            mostrar_tareas(tareas)
        elif accion == '5':
            guardar_tareas(archivo_tareas, tareas)
            break
        else:
            print('Opción no válida')


def menu_principal():
    """Menú principal del programa."""
    while True:
        print()
        print('---Menú principal---')
        print()
        accion = input('1. Añadir empleado\n2. Acceder a tareas\n3. Mostrar empleados\n4. Verificar y recordar\n5. Cerrar aplicación\nNúmero: ')
        
        if accion == '1':
            añadir_empleado()
        elif accion == '2':
            acceso_tareas_user()
        elif accion == '3':
            mostrar_empleados()
        elif accion == '4':
            verificar_recordar()
        elif accion == '5':
            guardar_empleados()
            break
        else:
            print('Opción no válida')


def mostrar_empleados():
    """Muestra la lista de empleados."""
    print()
    print('--LISTA DE EMPLEADOS--')
    print()
    for i, empleado in enumerate(empleados.keys(), 1):
        print(f'{i}. {empleado}')




