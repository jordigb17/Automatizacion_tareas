# **Gestor de Tareas Automatizado**  

¿Tienes una empresa y necesitas gestionar las tareas de tus empleados, asegurándote de que reciban recordatorios antes de su vencimiento? ¡Bienvenido al **Gestor de Tareas Automatizado**!  

## **Capturas de Pantalla**  

### **Menú Principal:**  
![Image](https://github.com/user-attachments/assets/9f076ed0-e94e-445d-be70-9d5a992816d4)  

### **Menú de Gestión de Tareas:**  
![Image](https://github.com/user-attachments/assets/acead94a-a9b6-429f-a752-86b834759605)  

## **Características**  
✅ **Gestión de empleados:** Agrega empleados con un solo clic y almacena sus correos electrónicos.  

✅ **Asignación de tareas:** Asigna tareas con fecha de vencimiento y prioridad. Las tareas se organizan automáticamente en función de su urgencia.  

✅ **Seguimiento de tareas:** Marca tareas como completadas o elimínalas cuando ya no sean necesarias.  

✅ **Recordatorios automatizados:**  
- La función **"Verificar y recordar"** envía un resumen de las tareas **pendientes** con vencimiento al día siguiente a cada empleado.  
- Se puede ejecutar manualmente en cualquier momento o configurar con **crontab** para que se ejecute automáticamente.  

## **Cómo Empezar**  

1️⃣ **Clonar el repositorio**  
   Descarga el código en tu computadora.  

2️⃣ **Instalar Python y dependencias**  
   Asegúrate de tener **Python** instalado junto con las bibliotecas necesarias, que se encuentran listadas al inicio del archivo `main.py`.  

3️⃣ **Configurar el script**  
   Abre `main.py` y edita los campos indicados en los comentarios.  

4️⃣ **Ejecutar el programa**  
   Ejecuta `main.py` y empieza a gestionar las tareas de tu empresa de manera eficiente.  

5️⃣ **Automatizar los recordatorios**  
   - Abre la configuración de tareas programadas con el comando:  
     ```bash
     crontab -e
     ```  
   - Agrega una línea con la ejecución del script en el momento deseado:  
     ```bash
     ***** /usr/bin/python3 /ruta/completa/a/executable_crontab.py
     ```  
     🔹 **Nota:** Los asteriscos representan `(minuto, hora, día del mes, mes, día de la semana)`, en ese orden. Ajusta los valores según la frecuencia deseada.  
   - Guarda y sal.  

## **Licencia**  
Este proyecto está bajo la **Licencia MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.  

