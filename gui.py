import sys
import platform
import psutil
import datetime
import socket
import pyttsx3
import getpass
import webbrowser
import requests
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QTabWidget,
    QTimeEdit, QPushButton, QFormLayout, QLineEdit, QTextEdit,
    QScrollArea, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QTimer, QDateTime


class ShutdownGuard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shutdown Guard")
        self.setWindowIcon(QIcon("power.png"))  
        self.setGeometry(300, 150, 850, 650)

        self.set_dark_theme()

        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)

        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #222222, stop:1 #333333);
                color: #eee;
                padding: 14px;
                margin: 5px;
                border-radius: 10px;
                font-family: Consolas, monospace;
                font-size: 14px;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #555555, stop:1 #777777);
                color: #fff;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: none;
                margin-top: 10px;
            }
        """)

        self.sys_tab = self.create_system_info_tab()
        self.time_tab = self.create_set_time_tab()
        self.email_tab = self.create_email_tab()
        self.about_tab = self.create_about_tab()

        self.tabs.addTab(self.sys_tab, "System Info")
        self.tabs.addTab(self.time_tab, "Shutdown Time")
        self.tabs.addTab(self.email_tab, "Email Settings")
        self.tabs.addTab(self.about_tab, "About")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_info)
        self.timer.start(1000)

        self.load_saved_shutdown_time()
        self.load_saved_email_settings()

    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(40, 40, 40))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Highlight, QColor(38, 79, 120))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)

    def create_system_info_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.time_label = QLabel("Loading current time...")
        self.time_label.setFont(QFont("Consolas", 15))
        self.time_label.setStyleSheet("margin-bottom: 10px;")

        self.sys_label = QLabel("Loading system info...")
        self.sys_label.setFont(QFont("Consolas", 11))
        self.sys_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.sys_label.setWordWrap(True)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: #1e1e1e; border: none;")
        scroll.setWidget(self.sys_label)

        layout.addWidget(self.time_label)
        layout.addWidget(scroll)
        tab.setLayout(layout)
        return tab

    def update_system_info(self):
        now = QDateTime.currentDateTime().toString("HH:mm:ss - yyyy/MM/dd")
        self.time_label.setText(f"Current Time: {now}")

        try:
            try:
                ip = requests.get("https://api.myip.com", timeout=2).text
            except:
                ip = "IP info not available"
            uname = platform.uname()
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.datetime.now() - boot_time
            user = getpass.getuser()
            hostname = socket.gethostname()

            cpu_freq = psutil.cpu_freq()
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_cores_physical = psutil.cpu_count(logical=False)
            cpu_cores_logical = psutil.cpu_count()

            mem = psutil.virtual_memory()

            disk_partitions = psutil.disk_partitions()
            disk_info = []
            for p in disk_partitions:
                try:
                    usage = psutil.disk_usage(p.mountpoint)
                    disk_info.append(f"{p.device} [{p.mountpoint}]: "
                                     f"{usage.used//(1024**3)} GB / {usage.total//(1024**3)} GB ({usage.percent}%)")
                except PermissionError:
                    disk_info.append(f"{p.device} [{p.mountpoint}]: Permission Denied")

            net_io = psutil.net_io_counters()
            net_addrs = psutil.net_if_addrs()
            net_info = []
            for iface_name, addrs in net_addrs.items():
                ips = [addr.address for addr in addrs if addr.family == socket.AF_INET]
                if ips:
                    net_info.append(f"{iface_name}: {', '.join(ips)}")

            battery = psutil.sensors_battery()

            users = psutil.users()
            users_info = ", ".join([u.name for u in users]) if users else "No users logged in"

            # Fix for psutil.sensors_temperatures() missing on some systems
            try:
                temps = psutil.sensors_temperatures()
                cpu_temps = temps.get('coretemp') or temps.get('cpu-thermal') or []
                temps_info = ", ".join([f"{t.label}: {t.current}°C" for t in cpu_temps]) if cpu_temps else "No temperature info"
            except AttributeError:
                temps_info = "Temperature info not available on this system"

            info = f"""
System Information
-------------------
OS: {uname.system} {uname.release} ({uname.version})
Architecture: {platform.machine()}
Hostname: {hostname}
User: {user}
Logged-in Users: {users_info}
Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}
Uptime: {str(uptime).split('.')[0]}

CPU Information
----------------
Model: {uname.processor}
Physical Cores: {cpu_cores_physical}
Logical Cores: {cpu_cores_logical}
Max Frequency: {cpu_freq.max:.2f} MHz
Current Frequency: {cpu_freq.current:.2f} MHz
CPU Usage: {cpu_percent} %
Temperatures: {temps_info}

Memory Information
--------------------
Total: {mem.total // (1024**2)} MB
Available: {mem.available // (1024**2)} MB
Used: {mem.used // (1024**2)} MB
Percentage: {mem.percent} %

Disk Information
-----------------
{chr(10).join(disk_info)}

Network Interfaces & IPs
-------------------------
{chr(10).join(net_info)}
{ip.replace("{", "").replace("}", "").replace(",", "\n")}

Network I/O
--------------

Bytes Sent: {net_io.bytes_sent // (1024**2)} MB
Bytes Received: {net_io.bytes_recv // (1024**2)} MB

Battery
----------
{f'{battery.percent}% - Plugged In' if battery and battery.power_plugged else 'On Battery' if battery else 'No Battery Info'}
            """.strip()

            self.sys_label.setText(info)

        except Exception as e:
            self.sys_label.setText(f"Error reading system info:\n{str(e)}")

    def create_set_time_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Choose a time to schedule shutdown:")
        label.setFont(QFont("Segoe UI", 12))
        label.setStyleSheet("margin-bottom: 10px;")

        self.time_picker = QTimeEdit()
        self.time_picker.setDisplayFormat("HH:mm")
        self.time_picker.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
        self.time_picker.setFont(QFont("Segoe UI", 13))

        save_btn = QPushButton("Save Time")
        save_btn.setStyleSheet("background-color: #0078d7; color: white; padding: 10px; font-size: 14px;")
        save_btn.clicked.connect(self.save_shutdown_time)

        layout.addWidget(label)
        layout.addWidget(self.time_picker)
        layout.addWidget(save_btn)

        tab.setLayout(layout)
        return tab

    def save_shutdown_time(self):
        selected_time = self.time_picker.time().toString("HH:mm")
        try:
            with open("shutdown_time.txt", "w") as f:
                f.write(selected_time)
            QMessageBox.information(self, "Saved", f"Shutdown time saved: {selected_time}")
            subprocess.Popen(
                ["python", "offing.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
                )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save shutdown time:\n{e}")

    def load_saved_shutdown_time(self):
        try:
            with open("shutdown_time.txt", "r") as f:
                time_str = f.read().strip()
                if time_str:
                    qtime = QDateTime.fromString(time_str, "HH:mm").time()
                    if qtime.isValid():
                        self.time_picker.setTime(qtime)
        except:
            pass

    def create_email_tab(self):
        tab = QWidget()
        form = QFormLayout()

        self.email_sender_input = QLineEdit()
        self.app_password_input = QLineEdit()
        self.reciver = QLineEdit()

        save_btn = QPushButton("Save Email Settings")
        save_btn.setStyleSheet("background-color: green; color: white; padding: 10px; font-size: 14px;")
        save_btn.clicked.connect(self.save_email_settings)

        form.addRow("Sender Email:", self.email_sender_input)
        form.addRow("App Password:", self.app_password_input)
        form.addRow("Reciver:", self.reciver)
        form.addRow(save_btn)

        tab.setLayout(form)
        return tab

    def save_email_settings(self):
        email_sender = self.email_sender_input.text()
        app_password = self.app_password_input.text()
        reciver = self.reciver.text()

        try:
            with open("email_settings.txt", "w", encoding="utf-8") as f:
                f.write(f"{email_sender}\n{app_password}\n{reciver}")
            QMessageBox.information(self, "Saved", "Email settings saved successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save email settings:\n{e}")

    def load_saved_email_settings(self):
        try:
            with open("email_settings.txt", "r", encoding="utf-8") as f:
                data = f.read()
                lines = data.splitlines()
                if len(lines) >= 3:
                    self.email_input.setText(lines[0].replace("Email: ", ""))
                    self.subject_input.setText(lines[1].replace("Subject: ", ""))
                    self.message_box.setPlainText("\n".join(lines[3:]))
        except:
            pass

    def create_about_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        about_text = """
🔌 Shutdown Guard

A simple utility to schedule PC shutdowns,
monitor system status, and optionally send alerts via email.

Developed with ❤️ by Niproot
Web site: niproot.freehost.io
github: github.com/niproot

        """
        about_label = QLabel(about_text)
        about_label.setFont(QFont("Segoe UI", 13))
        about_label.setStyleSheet("color: #ddd;")
        about_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        about_label.setWordWrap(True)

        layout.addWidget(about_label)
        tab.setLayout(layout)
        return tab


if __name__ == '__main__':
    pyttsx3.speak("welcome")
    webbrowser.open("https://niproot.freehost.io/")
    app = QApplication(sys.argv)
    window = ShutdownGuard()
    window.show()
    sys.exit(app.exec_())
