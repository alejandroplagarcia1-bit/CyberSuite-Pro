# CyberSuite Pro 🛡️

> **Toolkit Portátil de Auditoría Avanzada, Análisis Forense y Gestión de Licencias**

**CyberSuite Pro** es una suite de ciberseguridad y diagnóstico de sistemas desarrollada en Python. Incorpora una interfaz gráfica moderna de estilo Cyberpunk/Dark Mode basada en **CustomTkinter**, diseñada para realizar auditorías en tiempo real sobre hardware, tráfico de red, procesos del sistema y gestión de licencias corporativas.

---

## 🏗️ Arquitectura del Proyecto

El proyecto está estructurado modularmente para separar la lógica de negocio, las conexiones de base de datos y los módulos de análisis:

```text
CARPETA CS/
├── config/
│   └── settings.py          # Configuración de MongoDB, credenciales y parámetros
├── database/
│   └── mongo_manager.py     # Gestión de conexiones, sesiones y logs de auditoría
├── modules/
│   ├── network_scanner.py   # Detección de interfaces Wi-Fi, escáner TCP y tráfico
│   ├── disk_analyzer.py     # Análisis de particiones y búsqueda exhaustiva de archivos
│   └── process_monitor.py   # Inspección de RAM, PID y patrones de ejecución
├── ui/
│   └── gui_main.py          # Interfaz gráfica principal con CustomTkinter
├── main.py                  # Edición Standard (Gestión de auditorías y sesiones)
├── mainpro.py               # Edición Pro (Panel Admin & Gestión de 100 Clientes)
└── requirements.txt         # Lista de dependencias (customtkinter, pymongo, psutil)



⚡ Ediciones del Software
1. Versión Standard (main.py)
Diseñada para uso operativo en campo por parte de auditores:

Control de Sesiones: Registro de inicio y fin de auditoría por cliente.

Persistencia Híbrida: Guarda eventos en MongoDB (audit_suite_db). Si no detecta una instancia activa, conmuta automáticamente a Modo Offline.

Herramientas de Diagnóstico: Acceso a escaneo de disco, análisis de puertos TCP y monitoreo de procesos.

2. Versión Pro / Panel Admin (mainpro.py)
Diseñada para administración corporativa y supervisión de licencias:

Panel de Control de Licencias: Monitor de alquileres para 100 grandes empresas (Global, Europa y LATAM) organizadas en planes de 3, 6 y 12 meses.

Filtros Inteligentes: Clasificación en tiempo real de licencias (Activas, Próximas a vencer en 15 días o Expiradas).

Acceso Directo: Ejecución de herramientas de diagnóstico sin restricciones de clave temporal.

3. Versión Portable / Executable
Compilada mediante PyInstaller en un único ejecutable autónomo (CyberSuite_Portable.exe), optimizado para ejecutarse desde pendrives USB en cualquier equipo Windows sin necesidad de instalación previa.

🔍 Funcionalidades Técnicas
💾 Análisis Exhaustivo de Disco: Detección de unidades montadas mediante llamadas al kernel (psutil). Lectura física de archivos sin límites para localizar ejecutables y scripts sospechosos (.exe, .bat, .vbs, .ps1, .scr, .dll).

📡 Auditoría de Red y Conexiones Salientes: Escaneo activo de puertos TCP críticos (21, 22, 80, 443, 3389, 27017, etc.) vía socket. Inspección en vivo de conexiones salientes asociando IP remota, puerto local y PID del proceso emisor.

🛡️ Inspector de Procesos: Monitoreo en tiempo real de lectura de memoria y marcas de advertencia (⚠️ [REVISAR]) sobre binarios de riesgo potencial (cmd.exe, powershell.exe, netcat, wireshark).

🔒 Cero Rastreo de Credenciales: Las contraseñas de red o Wi-Fi ingresadas en los módulos de auditoría son de naturaleza volátil y jamás se persisten en disco ni base de datos.

🚀 Requisitos e Instalación
1. Instalar dependencias
Asegúrate de tener Python 3.10+ instalado y ejecuta:

bash
pip install -r requirements.txt

2. Ejecución desde código fuente
Para la versión Standard:
bash
python main.py

Para la versión Pro (Admin):

bash
python mainpro.py

Compilación con PyInstaller
El proyecto incluye archivos .spec prediseñados para empaquetar los ejecutables con soporte nativo de recursos de customtkinter:

Compilar Versión Standard:

bash
pyinstaller main.spec

Compilar Versión Pro:

pyinstaller mainpro.spec

Compilar Versión Portable (Single File):

bash
pyinstaller CyberSuite_Portable.spec

Los binarios generados se ubicarán automáticamente dentro de la carpeta dist/.

📋 Nota de Compatibilidad
Windows: Compatible con Windows 10 y Windows 11. Lee el hardware, la memoria y la red del equipo anfitrión en tiempo real.

MongoDB: Opcional. Si el servicio de MongoDB no está iniciado en localhost:27017, la aplicación continuará funcionando normalmente en modo local.
```
