import os
import shutil
import platform
import subprocess


def is_windows():
    return platform.system().lower() == "windows"




def compile_scripts():
    """Compile Python scripts to silent .exe using PyInstaller."""
    os.system("pyinstaller --noconsole --onefile gui.py")


def copy_to_start_menu():
    """Copy compiled GUI to Start Menu Programs folder."""
    try:
        source = os.path.join(os.getcwd(), "dist", "gui.exe")
        target_dir = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs")
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, "gui.exe")
        shutil.copy2(source, target_path)
    except Exception:
        pass  # Silently ignore any copy errors


def run_gui():
    """Run the GUI executable silently."""
    try:
        exe_path = os.path.join(os.getcwd(), "dist", "gui.exe")
        subprocess.Popen(exe_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def main():
    if is_windows():
        compile_scripts()
        copy_to_start_menu()
        run_gui()
    else:
        # Optional: run gui.py directly on Linux/macOS
        try:
            subprocess.Popen(["python3", "gui.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass


if __name__ == "__main__":
    main()
