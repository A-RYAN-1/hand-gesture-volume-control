"""Start the program hidden at Windows sign-in.

    python tools/startup.py install    write a script into the Startup folder
    python tools/startup.py remove     delete it
    python tools/startup.py status     say whether it is installed

The script runs `pythonw handdetect.py --background`, so no console or preview window appears.
"""
import os
import sys

NAME = "hand-gesture-volume-control.vbs"
MAIN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "handdetect.py")


def startup_folder():
    return os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")


def script_text(pythonw, main):
    """VBScript that runs the program with the window hidden; quotes are doubled inside a VBScript string."""
    command = f'"{pythonw}" "{main}" --background'
    return f'CreateObject("WScript.Shell").Run "{command.replace(chr(34), chr(34) * 2)}", 0, False\r\n'


def pythonw_path():
    path = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(path):
        raise SystemExit(f"pythonw.exe not found next to {sys.executable}")
    return path


def main(argv):
    action = argv[0] if argv else ""
    target = os.path.join(startup_folder(), NAME)
    if action == "install":
        with open(target, "w", encoding="utf-8", newline="") as f:
            f.write(script_text(pythonw_path(), MAIN))
        print(f"Installed: {target}")
    elif action == "remove":
        if os.path.exists(target):
            os.remove(target)
            print(f"Removed: {target}")
        else:
            print("Not installed.")
    elif action == "status":
        print("Installed." if os.path.exists(target) else "Not installed.")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
