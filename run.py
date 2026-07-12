"""Start the FastAPI backend and React frontend with one command."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import time
import webbrowser
from collections.abc import Sequence

API_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"
FRONTEND_DIRECTORY = Path(__file__).parent / "frontend"


def start_process(
    command: Sequence[str],
    cwd: Path | None = None,
) -> subprocess.Popen[bytes]:
    """Start one development process using the active Python environment."""
    return subprocess.Popen(command, cwd=cwd)


def ensure_frontend_dependencies() -> None:
    """Install React dependencies once when the frontend has not been prepared."""
    if (FRONTEND_DIRECTORY / "node_modules").exists():
        return

    print("Installing frontend dependencies...")
    subprocess.run(["npm.cmd", "install"], cwd=FRONTEND_DIRECTORY, check=True)


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
    """Start the complete local application and optionally open the frontend."""
    parser = argparse.ArgumentParser(description="Start the Academic Assistant locally.")
    parser.add_argument("--no-browser", action="store_true")
    arguments = parser.parse_args()

    ensure_frontend_dependencies()
    processes = [
        start_process([sys.executable, "-m", "uvicorn", "app.main:app", "--reload"]),
        start_process(
            ["npm.cmd", "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"],
            cwd=FRONTEND_DIRECTORY,
        ),
    ]

    print("Academic Assistant started:")
    print(f"  Frontend:  {FRONTEND_URL}")
    print(f"  API docs:  {API_URL}/docs")
    print("Press Ctrl+C to stop all services.")

    if not arguments.no_browser:
        time.sleep(2)
        webbrowser.open(FRONTEND_URL)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        stop_processes(processes)


if __name__ == "__main__":
    main()
