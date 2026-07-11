"""Start the API and Streamlit prototypes with one command."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
import webbrowser
from collections.abc import Sequence

API_URL = "http://127.0.0.1:8000"
CHAT_URL = "http://127.0.0.1:8501"
DASHBOARD_URL = "http://127.0.0.1:8502"


def start_process(command: Sequence[str]) -> subprocess.Popen[bytes]:
    """Start one development process using the active Python environment."""
    return subprocess.Popen(command)


def stop_processes(processes: list[subprocess.Popen[bytes]]) -> None:
    """Stop child processes when the developer ends the local session."""
    for process in processes:
        if process.poll() is None:
            process.terminate()

    for process in processes:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def main() -> None:
    """Start the complete local prototype and optionally open the chat."""
    parser = argparse.ArgumentParser(description="Start the Academic Assistant locally.")
    parser.add_argument("--no-browser", action="store_true")
    arguments = parser.parse_args()

    commands = [
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload"],
        [sys.executable, "-m", "streamlit", "run", "chat/app.py", "--server.port", "8501", "--server.headless", "true"],
        [sys.executable, "-m", "streamlit", "run", "dashboard/app.py", "--server.port", "8502", "--server.headless", "true"],
    ]
    processes = [start_process(command) for command in commands]

    print("Academic Assistant started:")
    print(f"  Chat:      {CHAT_URL}")
    print(f"  Dashboard: {DASHBOARD_URL}")
    print(f"  API docs:  {API_URL}/docs")
    print("Press Ctrl+C to stop all services.")

    if not arguments.no_browser:
        time.sleep(2)
        webbrowser.open(CHAT_URL)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        stop_processes(processes)


if __name__ == "__main__":
    main()
