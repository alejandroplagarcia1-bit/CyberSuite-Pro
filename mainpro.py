import os
import sys
import socket
import threading
from datetime import datetime, timedelta
import psutil
import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# BASE DE DATOS DE 100 GRANDES EMPRESAS (GLOBAL, EUROPA, LATAM & ARGENTINA)
EMPRESAS_TOP = [
    # ARGENTINA (LATAM)
    "Mercado Libre", "Globant", "YPF", "Ualá", "Despegar", "Telecom Argentina", "Grupo Financiero Galicia",
    "BBVA Argentina", "Arcor", "Techint", "Bunge Argentina", "Cresud", "Pampa Energía", "TGS",
    "Banco Macro", "Central Puerto", "Loma Negra", "Mirgor", "Holcim Argentina", "Edenor", "Molinos Río de la Plata",
    "Laboratorios Roemmers", "SNC-Lavalin Argentina", "Mastellone Hermanos", "Autopistas del Sol",
    
    # LATAM
    "Petrobras", "Nubank", "Itau Unibanco", "AMX (América Móvil)", "FEMSA", "Grupo Bimbo", "Cemex",
    "Ecopetrol", "Bancolombia", "LATAM Airlines", "Falabella", "Cencosud", "SQM", "Credicorp", "Alicorp",
    "Rappi", "Kavak", "Bitso", "NotCo", "dLocal", "CSN", "JBS", "B3 Brasil", "Vale", "Suzano",

    # EUROPA
    "Telefónica", "Banco Santander", "BBVA", "Inditex", "Iberdrola", "Repsol", "Mercadona", "Seat",
    "SAP", "Siemens", "ASML", "Airbus", "Spotify", "Vodafone", "Deutsche Telekom", "BMW Group",
    "L'Oréal", "LVMH", "Schneider Electric", "TotalEnergies", "Philips", "Nokia", "Ferrari", "Capgemini", "Adyen",

    # GLOBAL / EE.UU.
    "Google (Alphabet)", "Amazon", "Meta (Facebook)", "Instagram", "Netflix", "Microsoft", "Apple", "Tesla",
    "NVIDIA", "AMD", "Intel", "IBM", "Oracle", "Cisco Systems", "Palo Alto Networks", "CrowdStrike",
    "Fortinet", "Cloudflare", "Snowflake", "Datadog", "Sony", "Samsung Electronics", "TSMC", "Alibaba", "Tencent"
]

DURACIONES = ["3 Meses", "6 Meses", "12 Meses", "1 Año"]

class CyberSuiteAdmin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CyberSuite Pro — Panel de Control Administrativo & Auditoría")
        self.geometry("1220x820")

        self.selected_drive = None
        self.clients_db = self.generate_100_clients()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar Admin
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.lbl_title = ctk.CTkLabel(self.sidebar, text="CYBER SUITE PRO\n[PANEL ADMIN]", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_title.pack(padx=20, pady=(20, 10))

        self.lbl_role = ctk.CTkLabel(self.sidebar, text="Modo: Superusuario / Auditor", font=ctk.CTkFont(size=11), text_color="#10b981")
        self.lbl_role.pack(padx=20, pady=(0, 20))

        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="📊 Control de Clientes", command=self.view_dashboard)
        self.btn_dashboard.pack(padx=15, pady=8)

        self.btn_disks = ctk.CTkButton(self.sidebar, text="💾 Análisis de Disco", command=self.view_disks)
        self.btn_disks.pack(padx=15, pady=8)

        self.btn_net = ctk.CTkButton(self.sidebar, text="📡 Red & Puertos", command=self.view_network)
        self.btn_net.pack(padx=15, pady=8)

        self.btn_sys = ctk.CTkButton(self.sidebar, text="🛡️ Procesos Activos", command=self.view_system)
        self.btn_sys.pack(padx=15, pady=8)

        self.main_container = ctk.CTkFrame(self, corner_radius=10)
        self.main_container.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        self.view_dashboard()

    def generate_100_clients(self):
        """Genera 100 clientes divididos equitativamente en 3m, 6m, 12m y 1 año con fechas de vencimiento reales."""
        clients_dict = {}
        now = datetime.now()

        for index, name in enumerate(EMPRESAS_TOP):
            group = index // 25
            duration_str = DURACIONES[group]
            days_map = {"3 Meses": 90, "6 Meses": 180, "12 Meses": 365, "1 Año": 365}
            total_days = days_map[duration_str]

            # Variación de fechas para simular expirados, por vencer y activos
            offset_days = (index % 12) * 20 - 60 
            purchase_date = now - timedelta(days=offset_days)
            expiration_date = purchase_date + timedelta(days=total_days)

            clients_dict[name] = {
                "duration": duration_str,
                "purchase_date": purchase_date,
                "expiration_date": expiration_date,
                "id_license": f"LIC-{name.replace(' ', '').upper()[:4]}-{index+100}"
            }

        return clients_dict

    def clear_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # VISTA 1: CONTROL ADMINISTRATIVO DE CLIENTES Y VENCIMIENTOS
    def view_dashboard(self):
        self.clear_container()
        title = ctk.CTkLabel(self.main_container, text="Panel de Gestión de Alquileres & Licencias de Clientes", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=10)

        # Botones de Filtro Rápido
        btn_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        btn_frame.pack(pady=5)

        btn_all = ctk.CTkButton(btn_frame, text="Ver Todos (100)", width=120, command=lambda: self.render_client_list("TODOS"))
        btn_all.pack(side="left", padx=5)

        btn_warning = ctk.CTkButton(btn_frame, text="⚠️ Próximos a Vencer", fg_color="#f59e0b", hover_color="#d97706", width=150, command=lambda: self.render_client_list("POR_VENCER"))
        btn_warning.pack(side="left", padx=5)

        btn_expired = ctk.CTkButton(btn_frame, text="❌ Licencias Expiradas", fg_color="#f43f5e", hover_color="#e11d48", width=150, command=lambda: self.render_client_list("EXPIRADOS"))
        btn_expired.pack(side="left", padx=5)

        btn_active = ctk.CTkButton(btn_frame, text="✓ Activos", fg_color="#10b981", hover_color="#059669", width=120, command=lambda: self.render_client_list("ACTIVOS"))
        btn_active.pack(side="left", padx=5)

        # Buscador por nombre
        search_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        search_frame.pack(pady=5)

        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Buscar cliente (ej: Mercado Libre, Amazon...)", width=320)
        self.entry_search.pack(side="left", padx=5)

        btn_search = ctk.CTkButton(search_frame, text="Buscar", width=90, command=self.search_client)
        btn_search.pack(side="left", padx=5)

        self.txt_dashboard = ctk.CTkTextbox(self.main_container, width=740, height=450)
        self.txt_dashboard.pack(pady=10)

        self.render_client_list("TODOS")

    def render_client_list(self, filter_type):
        self.txt_dashboard.delete("1.0", "end")
        now = datetime.now()

        header = f"=== INFORME DE ESTADO DE ALQUILERES — FILTRO: {filter_type} ===\n\n"
        self.txt_dashboard.insert("end", header)

        count = 0
        for company, data in self.clients_db.items():
            exp = data["expiration_date"]
            days_left = (exp - now).days

            is_expired = days_left < 0
            is_warning = 0 <= days_left <= 15
            is_active = days_left > 15

            if filter_type == "EXPIRADOS" and not is_expired: continue
            if filter_type == "POR_VENCER" and not is_warning: continue
            if filter_type == "ACTIVOS" and not is_active: continue

            if is_expired:
                status_tag = f"❌ EXPIRADA (Hace {abs(days_left)} días)"
            elif is_warning:
                status_tag = f"⚠️ POR VENCER ({days_left} días restantes)"
            else:
                status_tag = f"✓ ACTIVA ({days_left} días restantes)"

            p_str = data["purchase_date"].strftime('%d/%m/%Y')
            e_str = exp.strftime('%d/%m/%Y')

            line = f"• {company:<28} | Plan: {data['duration']:<8} | Alta: {p_str} | Vence: {e_str} | {status_tag}\n"
            self.txt_dashboard.insert("end", line)
            count += 1

        self.txt_dashboard.insert("end", f"\nTotal de registros encontrados: {count}\n")

    def search_client(self):
        query = self.entry_search.get().strip().lower()
        if not query:
            self.render_client_list("TODOS")
            return

        self.txt_dashboard.delete("1.0", "end")
        self.txt_dashboard.insert("end", f"=== RESULTADOS DE BÚSQUEDA PARA: '{query.upper()}' ===\n\n")

        now = datetime.now()
        found = 0
        for company, data in self.clients_db.items():
            if query in company.lower():
                exp = data["expiration_date"]
                days_left = (exp - now).days
                p_str = data["purchase_date"].strftime('%d/%m/%Y')
                e_str = exp.strftime('%d/%m/%Y')

                status_tag = "❌ EXPIRADA" if days_left < 0 else ("⚠️ POR VENCER" if days_left <= 15 else "✓ ACTIVA")
                line = f"• {company:<28} | Plan: {data['duration']} | Alta: {p_str} | Vence: {e_str} | Días: {days_left} | {status_tag}\n"
                self.txt_dashboard.insert("end", line)
                found += 1

        if found == 0:
            self.txt_dashboard.insert("end", "No se encontró ningún cliente con ese nombre.\n")

    # VISTAS DE HERRAMIENTAS DIRECTAS (SIN RESTRICCIÓN NI CLAVES)
    def view_disks(self):
        self.clear_container()
        title = ctk.CTkLabel(self.main_container, text="Análisis Exhaustivo de Disco Duro", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=10)

        partitions = psutil.disk_partitions()
        drive_list = [p.mountpoint for p in partitions]

        top_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        top_frame.pack(pady=10)

        lbl_select = ctk.CTkLabel(top_frame, text="Unidad:")
        lbl_select.pack(side="left", padx=10)

        self.combo_drives = ctk.CTkComboBox(top_frame, values=drive_list, command=self.on_drive_select)
        self.combo_drives.pack(side="left", padx=10)

        btn_scan = ctk.CTkButton(top_frame, text="Escanear Disco Entero", command=self.start_full_drive_scan)
        btn_scan.pack(side="left", padx=10)

        self.lbl_disk_info = ctk.CTkLabel(self.main_container, text="Seleccione una unidad.", font=ctk.CTkFont(size=12))
        self.lbl_disk_info.pack(pady=5)

        self.txt_disk_log = ctk.CTkTextbox(self.main_container, width=740, height=420)
        self.txt_disk_log.pack(pady=10)

        if drive_list: self.on_drive_select(drive_list[0])

    def on_drive_select(self, drive_path):
        self.selected_drive = drive_path
        try:
            usage = psutil.disk_usage(drive_path)
            total_gb = round(usage.total / (1024**3), 2)
            used_gb = round(usage.used / (1024**3), 2)
            free_gb = round(usage.free / (1024**3), 2)
            self.lbl_disk_info.configure(text=f"Unidad [{drive_path}] — Total: {total_gb} GB | Usado: {used_gb} GB ({usage.percent}%) | Libre: {free_gb} GB", text_color="#38bdf8")
        except Exception as e:
            self.lbl_disk_info.configure(text=f"Error leyendo unidad: {e}", text_color="#f43f5e")

    def start_full_drive_scan(self):
        if not self.selected_drive: return
        threading.Thread(target=self._scan_full_drive_worker, daemon=True).start()

    def _scan_full_drive_worker(self):
        self.txt_disk_log.delete("1.0", "end")
        self.txt_disk_log.insert("end", f"[*] INICIANDO ESCANEO AUDITOR EN UNIDAD: {self.selected_drive}\n\n")
        suspicious_ext = ['.exe', '.bat', '.vbs', '.ps1', '.scr', '.dll']
        total = 0
        for root, dirs, files in os.walk(self.selected_drive):
            for file in files:
                if os.path.splitext(file)[1].lower() in suspicious_ext:
                    self.txt_disk_log.insert("end", f"▶ {os.path.join(root, file)}\n")
                    total += 1
        self.txt_disk_log.insert("end", f"\n[✓] Escaneo finalizado. Total detectados: {total}\n")

    def view_network(self):
        self.clear_container()
        title = ctk.CTkLabel(self.main_container, text="Auditoría de Red, Puertos y Conexiones", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=10)

        cred_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        cred_frame.pack(pady=5)

        self.entry_host = ctk.CTkEntry(cred_frame, placeholder_text="IP Objetivo (Ej: 127.0.0.1)", width=200)
        self.entry_host.pack(side="left", padx=5)

        btn_net_scan = ctk.CTkButton(cred_frame, text="Escanear Puertos", command=self.start_port_scan)
        btn_net_scan.pack(side="left", padx=5)

        btn_traffic = ctk.CTkButton(cred_frame, text="Ver Conexiones Salientes", fg_color="#8b5cf6", hover_color="#7c3aed", command=self.monitor_outgoing_connections)
        btn_traffic.pack(side="left", padx=5)

        self.txt_net_log = ctk.CTkTextbox(self.main_container, width=740, height=420)
        self.txt_net_log.pack(pady=10)

    def start_port_scan(self):
        target = self.entry_host.get() or "127.0.0.1"
        threading.Thread(target=self._run_port_scan, args=(target,), daemon=True).start()

    def _run_port_scan(self, host):
        self.txt_net_log.delete("1.0", "end")
        self.txt_net_log.insert("end", f"[*] ESCANEO DE PUERTOS AUDITOR EN: {host}\n\n")
        ports = {21: "FTP", 22: "SSH", 80: "HTTP", 443: "HTTPS", 3389: "RDP", 27017: "MongoDB"}
        open_c = 0
        for port, service in ports.items():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((host, port)) == 0:
                self.txt_net_log.insert("end", f"[+] Puerto {port} ({service}): ABIERTO\n")
                open_c += 1
            else:
                self.txt_net_log.insert("end", f"[-] Puerto {port} ({service}): Cerrado\n")
            s.close()
        self.txt_net_log.insert("end", f"\n[*] Puertos abiertos: {open_c}\n")

    def monitor_outgoing_connections(self):
        self.txt_net_log.delete("1.0", "end")
        self.txt_net_log.insert("end", "[*] CONEXIONES SALIENTES ACTIVAS DEL SISTEMA:\n\n")
        connections = psutil.net_connections(kind='inet')
        out_c = 0
        for conn in connections:
            if conn.status == 'ESTABLISHED' and conn.raddr:
                pid = conn.pid
                pname = psutil.Process(pid).name() if pid else "Desconocido"
                self.txt_net_log.insert("end", f"🌐 Proceso: {pname} (PID {pid}) ➔ Destino: {conn.raddr.ip}:{conn.raddr.port}\n")
                out_c += 1
        self.txt_net_log.insert("end", f"\n[✓] Total de conexiones salientes: {out_c}\n")

    def view_system(self):
        self.clear_container()
        title = ctk.CTkLabel(self.main_container, text="Inspector de Procesos del Sistema", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=10)

        btn_proc = ctk.CTkButton(self.main_container, text="Analizar Procesos Activos", command=self.scan_processes)
        btn_proc.pack(pady=5)

        self.txt_sys_log = ctk.CTkTextbox(self.main_container, width=740, height=420)
        self.txt_sys_log.pack(pady=10)

    def scan_processes(self):
        self.txt_sys_log.delete("1.0", "end")
        self.txt_sys_log.insert("end", "[*] Analizando procesos del sistema...\n\n")
        high_risk = ['cmd.exe', 'powershell.exe', 'bash', 'nc', 'netcat', 'wireshark']
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                pname = proc.info['name']
                pid = proc.info['pid']
                mem = round(proc.info['memory_percent'] or 0, 1)
                flag = "⚠️ [REVISAR]" if any(h in pname.lower() for h in high_risk) else "✓ [NORMAL]"
                self.txt_sys_log.insert("end", f"{flag} PID: {pid} | Nombre: {pname} | Memoria: {mem}%\n")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

if __name__ == "__main__":
    app = CyberSuiteAdmin()
    app.mainloop()