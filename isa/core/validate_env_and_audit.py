import os
import sys
import subprocess
from datetime import datetime

LOG_FILE = "isa/logs/venv_issues.log"
ENV_FILE = ".env"

def log_issue(message):
    """Logs an issue message to the specified log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def check_venv_active():
    """Checks if a virtual environment is active."""
    venv_active = os.getenv("VIRTUAL_ENV") is not None and os.getenv("VIRTUAL_ENV") == sys.prefix
    if venv_active:
        print(f"Virtual environment is active: {sys.prefix}")
    else:
        log_issue("Virtual environment is NOT active.")
    return venv_active

def check_python_dotenv_installed():
    """Checks if python-dotenv is installed."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "show", "python-dotenv"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("python-dotenv is installed.")
        return True
    except subprocess.CalledProcessError:
        log_issue("python-dotenv is NOT installed. Please install it using 'pip install python-dotenv'.")
        return False

def check_env_file_loaded():
    """Checks if the .env file is present and loaded."""
    if not os.path.exists(ENV_FILE):
        log_issue(f"'{ENV_FILE}' file is NOT present in the current directory.")
        return False

    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=ENV_FILE)
        print(f"'{ENV_FILE}' file is present and loaded.")
        return True
    except ImportError:
        log_issue("python-dotenv is not installed, cannot verify .env file loading.")
        return False
    except Exception as e:
        log_issue(f"Error loading '{ENV_FILE}' file: {e}")
        return False

def main():
    print("Starting environment validation and .env audit...")
    venv_ok = check_venv_active()
    dotenv_installed = check_python_dotenv_installed()
    env_loaded = False
    if dotenv_installed:
        env_loaded = check_env_file_loaded()

    if venv_ok and dotenv_installed and env_loaded:
        print("Environment validation and .env audit completed successfully.")
    else:
        print("Environment validation and .env audit found issues. Check 'isa/logs/venv_issues.log' for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()