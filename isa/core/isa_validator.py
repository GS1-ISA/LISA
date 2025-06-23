import os
import sys
from datetime import datetime

def validate_environment():
    """
    Validates the runtime environment for ISA project.
    Checks for .venv activation, .env file presence, and python-dotenv installation.
    """
    log_file = "isa/logs/venv_issues.log"
    issues = []

    # 1. Check .venv activation
    venv_active = os.environ.get("VIRTUAL_ENV")
    if not venv_active:
        issues.append("ERROR: .venv is not active. Please activate your virtual environment.")
    elif not sys.prefix.startswith(venv_active):
        issues.append(f"ERROR: sys.prefix ({sys.prefix}) does not match VIRTUAL_ENV ({venv_active}).")
    else:
        print(f"INFO: Virtual environment active: {venv_active}")

    # 2. Check .env file presence
    env_file_path = ".env"
    if not os.path.exists(env_file_path):
        issues.append(f"ERROR: .env file not found at {env_file_path}.")
    else:
        print(f"INFO: .env file found at {env_file_path}.")

    # 3. Check python-dotenv installation
    try:
        import dotenv
        print("INFO: python-dotenv is installed.")
    except ImportError:
        issues.append("ERROR: python-dotenv is not installed. Please install it using 'pip install python-dotenv'.")

    if issues:
        with open(log_file, "a") as f:
            f.write(f"[{datetime.now()}] Environment Validation Issues:\n")
            for issue in issues:
                f.write(f"- {issue}\n")
            f.write("\n")
        print(f"WARNING: Environment validation failed. See {log_file} for details.")
        return False
    else:
        print("INFO: Environment validation successful.")
        return True

if __name__ == "__main__":
    print("Running ISA Validator...")
    validation_result = validate_environment()
    if validation_result:
        print("ISA Validator completed successfully.")
    else:
        print("ISA Validator completed with warnings/errors.")