import os
import sys
import socket
import threading
import hashlib
from datetime import datetime
import psutil
import customtkinter as ctk
from pymongo import MongoClient

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CyberSuitePro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CyberSuite Pro — Toolkit Portable (Auditoría Avanzada)")
        self.geometry("1180x760")

        try:
            self.db_client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
            self.db = self.db_client["audit_suite_db"]
            self.db_client.admin.command('ping')
            self.db_status = "Conectado"
        except Exception:
            self.db = None
            self.db_status = "Modo Offline"

        self.active_session_id = None
        self.selected_drive = None
        self.is_sniffing = False

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.lbl_title = ctk.CTkLabel(self.sidebar, text="CYBER SUITE PRO", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_title.pack(padx=20, pady=(20, 10))

        self.lbl_db = ctk.CTkLabel(
            self.sidebar, 
            text=f"DB: {self.db_status}", 
            font=ctk.CTkFont(size=10), 
            text_color="#10b981" if self.db is not None else "#f43f5e"
        )
        self.lbl_db.pack(padx=20, pady=(0, 20))

        self.btn_auth = ctk.CTkButton(self.sidebar, text="🔑 Registro / Clientes", command=self.view_auth)
        self.btn_auth.pack(padx=15, pady=8)

        self.btn_disks = ctk.CTkButton(self.sidebar, text="💾 Análisis Completo Disco", command=self.view_disks)
        self.btn_disks.pack(padx=15, pady=8)

        self.btn_net = ctk.CTkButton(self.sidebar, text="📡 Red, Puertos y Tráfico Out", command=self.view_network)
        self.btn_net.pack(padx=15, pady=8)

        self.btn_sys = ctk.CTkButton(self.sidebar, text="🛡️ Procesos & Malware", command=self.view_system)
        self.btn_sys.pack(padx=15, pady=8)

        self.main_container = ctk.CTkFrame(self, corner_radius=10)
        self.main_container.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        self.view_auth()

    def clear_container(self):
        self.is_sniffing = False
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # VISTA 1: REGISTRO DE CLIENTES Y AUDITORÍAS
    def view_auth(self):
        self.clear_container()
        title = ctk.CTkLabel(self.main_container, text="Control de Sesiones de Auditoría", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=15)

        self.entry_client = ctk.CTkEntry(self.main_container, placeholder_text="ID / Nombre del Cliente u Operación", width=320)
        self.entry_client.pack(pady=8)

        self.entry_cred = ctk.CTkEntry(self.main_container, placeholder_text="Clave Temporal de Sesión", show="*", width=320)
        self.entry_cred.pack(pady=8)

        btn_box = ctk.CTkFrame(self.main_container, fg_color="transparent")
        btn_box.pack(pady=10)

        btn_in = ctk.CTkButton(btn_box, text="Iniciar Sesión", fg_color="#10b981", hover_color="#059669", command=self.client_login)
        btn_in.pack(side="left", padx=10)

        btn_out = ctk.CTkButton(btn_box, text="Cerrar Sesión", fg_color="#f43f5e", hover_color="#e11d48", command=self.client_logout)
        btn_out.pack(side="left", padx=10)

        self.lbl_auth_msg = ctk.CTkLabel(self.main_container, text="Esperando credenciales...", text_color="#94a3b8")
        self.lbl_auth_msg.pack(pady=10)

        self.txt_history = ctk.CTkTextbox(self.main_container, width=700, height=300)
        self.txt_history.pack(pady=10)
        self.refresh_audit_logs()

    def client_login(self):
        client = self.entry_client.get()
        cred = self.entry_cred.get()
        if not client or not cred:
            self.lbl_auth_msg.configure(text="Complete todos los campos.", text_color="#f43f5e")
            return

        cred_hash = hashlib.sha256(cred.encode()).hexdigest()
        session_data = {"client_id": client, "cred_hash": cred_hash[:12], "entry_time": datetime.now(), "exit_time": None, "status": "ACTIVA"}

        if self.db is not None:
            res = self.db.audit_sessions.insert_one(session_data)
            self.active_session_id = res.inserted_id
            self.lbl_auth_msg.configure(text=f"Sesión activa registrada para '{client}'.", text_color="#10b981")
        else:
            self.lbl_auth_msg.configure(text=f"Modo offline: Sesión iniciada para {client}.", text_color="#38bdf8")

        self.refresh_audit_logs()

    def client_logout(self):
        if self.active_session_id and self.db is not None:
            self.db.audit_sessions.update_one({"_id": self.active_session_id}, {"$set": {"exit_time": datetime.now(), "status": "FINALIZADA"}})
            self.active_session_id = None
            self.lbl_auth_msg.configure(text="Sesión finalizada.", text_color="#38bdf8")
        else:
            self.lbl_auth_msg.configure(text="No hay sesión activa.", text_color="#f43f5e")
        self.refresh_audit_logs()

    def refresh_audit_logs(self):
        self.txt_history.delete("1.0", "end")
        self.txt_history.insert("end", "=== REGISTRO DE AUDITORÍAS Y SESIONES ===\n\n")
        if self.db is not None:
            logs = list(self.db.audit_sessions.find().sort("entry_time", -1).limit(10))
            for log in logs:
                entry = log['entry_time'].strftime('%Y-%m-%d %H:%M:%S') if log.get('entry_time') else 'N/A'
                exit_t = log['exit_time'].strftime('%Y-%m-%d %H:%M:%S') if log.get('exit_time') else 'EN CURSO'
                self.txt_history.insert("end", f"▶ Registro: {log['client_id']} | Inicio: {entry} | Fin: {exit_t} | Estado: {log['status']}\n")
        else:
            self.txt_history.insert("end", "[Modo offline activo. Conecte MongoDB para guardar historial].\n")

    # VISTA 2: ESCANEO COMPLETO DE DISCO
    def view_disks(self):
        self.clear_container()
        title = ctk.CTkLabel(self.main_container, text="Análisis Exhaustivo y Completo de Disco", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=10)

        partitions = psutil.disk_partitions()
        drive_list = [p.mountpoint for p in partitions]

        top_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        top_frame.pack(pady=10)

        lbl_select = ctk.CTkLabel(top_frame, text="Unidad:")
        lbl_select.pack(side="left", padx=10)

        self.combo_drives = ctk.CTkComboBox(top_frame, values=drive_list, command=self.on_drive_select)
        self.combo_drives.pack(side="left", padx=10)

        btn_scan_drive = ctk.CTkButton(top_frame, text="Escanear Disco Entero", command=self.start_full_drive_scan)
        btn_scan_drive.pack(side="left", padx=10)

        self.lbl_disk_info = ctk.CTkLabel(self.main_container, text="Seleccione una unidad.", font=ctk.CTkFont(size=12))
        self.lbl_disk_info.pack(pady=5)

        self.txt_disk_log = ctk.CTkTextbox(self.main_container, width=700, height=340)
        self.txt_disk_log.pack(pady=10)

        if drive_list:
            self.on_drive_select(drive_list[0])

    def on_drive_select(self, drive_path):
        self.selected_drive = drive_path
        try:
            usage = psutil.disk_usage(drive_path)
            total_gb = round(usage.total / (1024**3), 2)
            used_gb = round(usage.used / (1024**3), 2)
            free_gb = round(usage.free / (1024**3), 2)
            self.lbl_disk_info.configure(text=f"Unidad [{drive_path}] — Capacidad: {total_gb} GB | Usado: {used_gb} GB ({usage.percent}%) | Libre: {free_gb} GB", text_color="#38bdf8")
        except Exception as e:
            self.lbl_disk_info.configure(text=f"Error leyendo la unidad {drive_path}: {e}", text_color="#f43f5e")

    def start_full_drive_scan(self):
        if not self.selected_drive:
            return
        threading.Thread(target=self._scan_full_drive_worker, daemon=True).start()

    def _scan_full_drive_worker(self):
        self.txt_disk_log.delete("1.0", "end")
        self.txt_disk_log.insert("end", f"[*] INICIANDO ESCANEO COMPLETO SIN LÍMITES EN: {self.selected_drive}\n")
        self.txt_disk_log.insert("end", "[*] Buscando .exe, .bat, .vbs, .ps1, .scr, .dll...\n\n")
        
        suspicious_extensions = ['.exe', '.bat', '.vbs', '.ps1', '.scr', '.dll']
        total_found = 0
        
        for root, dirs, files in os.walk(self.selected_drive):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in suspicious_extensions:
                    full_path = os.path.join(root, file)
                    self.txt_disk_log.insert("end", f"▶ [{ext.upper()}] {full_path}\n")
                    total_found += 1

        self.txt_disk_log.insert("end", f"\n[✓] Escaneo finalizado. Total de ejecutables/scripts detectados: {total_found}\n")

    # VISTA 3: ESCANEO DE PUERTOS Y TRÁFICO SALIENTE
    def view_network(self):
        self.clear_container()
        title = ctk.CTkLabel(self.main_container, text="Auditoría de Red, Puertos y Tráfico Saliente", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=10)

        # Formulario de Credenciales de Red (Volátiles)
        cred_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        cred_frame.pack(pady=5)

        self.entry_wifi_pass = ctk.CTkEntry(cred_frame, placeholder_text="Contraseña Red/Wi-Fi (Volátil)", show="*", width=250)
        self.entry_wifi_pass.pack(side="left", padx=5)

        self.entry_host = ctk.CTkEntry(cred_frame, placeholder_text="IP Objetivo (Ej: 127.0.0.1)", width=180)
        self.entry_host.pack(side="left", padx=5)

        btn_net_scan = ctk.CTkButton(cred_frame, text="Escanear Puertos", command=self.start_port_scan)
        btn_net_scan.pack(side="left", padx=5)

        btn_traffic = ctk.CTkButton(cred_frame, text="Ver Conexiones Salientes", fg_color="#8b5cf6", hover_color="#7c3aed", command=self.monitor_outgoing_connections)
        btn_traffic.pack(side="left", padx=5)

        self.lbl_net_note = ctk.CTkLabel(self.main_container, text="🔒 Nota: Las contraseñas escritas NO se guardan en ningún archivo ni base de datos.", font=ctk.CTkFont(size=11), text_color="#94a3b8")
        self.lbl_net_note.pack(pady=2)

        self.txt_net_log = ctk.CTkTextbox(self.main_container, width=700, height=330)
        self.txt_net_log.pack(pady=10)

    def start_port_scan(self):
        target = self.entry_host.get() or "127.0.0.1"
        threading.Thread(target=self._run_port_scan, args=(target,), daemon=True).start()

    def _run_port_scan(self, host):
        self.txt_net_log.delete("1.0", "end")
        self.txt_net_log.insert("end", f"[*] ESCANEO DE PUERTOS EXTENDIDO EN: {host}\n\n")
        
        ports_to_scan = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
            80: "HTTP", 110: "POP3", 139: "NetBIOS", 443: "HTTPS", 445: "SMB",
            1433: "MSSQL", 3306: "MySQL", 3389: "RDP", 8080: "HTTP-Proxy", 27017: "MongoDB"
        }
        
        open_count = 0
        for port, service in ports_to_scan.items():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            res = s.connect_ex((host, port))
            if res == 0:
                self.txt_net_log.insert("end", f"[+] Puerto {port} ({service}): ABIERTO\n")
                open_count += 1
            else:
                self.txt_net_log.insert("end", f"[-] Puerto {port} ({service}): Cerrado\n")
            s.close()
            
        self.txt_net_log.insert("end", f"\n[*] Escaneo completado. Puertos abiertos detectados: {open_count}\n")

    def monitor_outgoing_connections(self):
        self.txt_net_log.delete("1.0", "end")
        self.txt_net_log.insert("end", "[*] MONITOREANDO CONEXIONES SALIENTES DE RED (PAQUETES / CONEXIONES EXTERNAS)...\n\n")
        
        connections = psutil.net_connections(kind='inet')
        outgoing_count = 0
        
        for conn in connections:
            if conn.status == 'ESTABLISHED' and conn.raddr:
                remote_ip, remote_port = conn.raddr.ip, conn.raddr.port
                local_port = conn.laddr.port
                pid = conn.pid
                
                # Obtener nombre del proceso que envía los datos
                proc_name = "Desconocido"
                if pid:
                    try:
                        proc_name = psutil.Process(pid).name()
                    except Exception:
                        pass

                self.txt_net_log.insert("end", f"🌐 [SALIENTE] Proceso: {proc_name} (PID {pid}) | Puerto Local: {local_port} ➔ Destino Externo: {remote_ip}:{remote_port}\n")
                outgoing_count += 1

        if outgoing_count == 0:
            self.txt_net_log.insert("end", "[i] No se detectan conexiones externas activas en este instante.\n")
        else:
            self.txt_net_log.insert("end", f"\n[✓] Total de conexiones salientes activas hacia el exterior: {outgoing_count}\n")

    # VISTA 4: PROCESOS ACTIVO Y MALWARE
    def view_system(self):
        self.clear_container()
        title = ctk.CTkLabel(self.main_container, text="Inspector de Procesos y Software Sospechoso", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=10)

        btn_proc = ctk.CTkButton(self.main_container, text="Analizar Procesos Activos", command=self.scan_processes)
        btn_proc.pack(pady=5)

        self.txt_sys_log = ctk.CTkTextbox(self.main_container, width=700, height=360)
        self.txt_sys_log.pack(pady=10)

    def scan_processes(self):
        self.txt_sys_log.delete("1.0", "end")
        self.txt_sys_log.insert("end", "[*] Analizando procesos en ejecución...\n\n")
        high_risk_names = ['cmd.exe', 'powershell.exe', 'bash', 'nc', 'netcat', 'wireshark']
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                pname = proc.info['name']
                pid = proc.info['pid']
                mem = round(proc.info['memory_percent'] or 0, 1)
                is_flagged = any(h in pname.lower() for h in high_risk_names)
                flag_tag = "⚠️ [REVISAR]" if is_flagged else "✓ [NORMAL]"
                self.txt_sys_log.insert("end", f"{flag_tag} PID: {pid} | Nombre: {pname} | Memoria: {mem}%\n")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

if __name__ == "__main__":
    app = CyberSuitePro()
    app.mainloop()