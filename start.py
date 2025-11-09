#!/usr/bin/env python3
"""
FIN-DASH Application Startup Script
====================================

This script starts both the backend (FastAPI) and frontend (Vite) servers
for the FIN-DASH personal finance dashboard application.

Usage:
    python start.py              # Start both backend and frontend
    python start.py --backend    # Start backend only
    python start.py --frontend   # Start frontend only
    python start.py --help       # Show help message

Requirements:
    - Python 3.8+
    - Node.js 16+
    - Virtual environment in backend/venv (will be created if missing)
    - Node modules installed (will be installed if missing)
"""

import os
import sys
import subprocess
import time
import platform
import argparse
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(message):
    """Print a formatted header message."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(message):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_info(message):
    """Print an info message."""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


def print_warning(message):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def print_error(message):
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.absolute()


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print_info("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_node_installed():
    """Check if Node.js is installed."""
    print_info("Checking Node.js installation...")
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print_success(f"Node.js {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print_error("Node.js not found. Please install Node.js 16+ from https://nodejs.org/")
    return False


def setup_backend_venv():
    """Set up Python virtual environment for backend."""
    project_root = get_project_root()
    backend_dir = project_root / "backend"
    venv_dir = backend_dir / "venv"
    
    if venv_dir.exists():
        print_success("Virtual environment already exists")
        return True
    
    print_info("Creating virtual environment...")
    try:
        subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], check=True)
        print_success("Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False


def install_backend_dependencies():
    """Install backend Python dependencies."""
    project_root = get_project_root()
    backend_dir = project_root / "backend"
    venv_dir = backend_dir / "venv"
    requirements_file = backend_dir / "requirements.txt"
    
    # Determine pip executable path based on OS
    if platform.system() == "Windows":
        pip_executable = venv_dir / "Scripts" / "pip.exe"
    else:
        pip_executable = venv_dir / "bin" / "pip"
    
    if not pip_executable.exists():
        print_error("Virtual environment pip not found")
        return False
    
    print_info("Installing backend dependencies...")
    try:
        subprocess.run(
            [str(pip_executable), 'install', '-r', str(requirements_file)],
            check=True,
            cwd=str(backend_dir)
        )
        print_success("Backend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install backend dependencies: {e}")
        return False


def install_frontend_dependencies():
    """Install frontend Node.js dependencies."""
    project_root = get_project_root()
    node_modules = project_root / "node_modules"

    if node_modules.exists():
        print_success("Node modules already installed")
        return True

    print_info("Installing frontend dependencies (this may take a few minutes)...")
    try:
        # Use shell=True on Windows to find npm.cmd
        subprocess.run(['npm', 'install'], check=True, cwd=str(project_root), shell=True)
        print_success("Frontend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install frontend dependencies: {e}")
        return False


def start_backend():
    """Start the FastAPI backend server."""
    project_root = get_project_root()
    backend_dir = project_root / "backend"
    venv_dir = backend_dir / "venv"

    # Determine python executable path based on OS
    if platform.system() == "Windows":
        python_executable = venv_dir / "Scripts" / "python.exe"
    else:
        python_executable = venv_dir / "bin" / "python"

    print_info("Starting backend server on http://127.0.0.1:8777...")

    try:
        # Start backend in a new process
        # Use START command on Windows to open in new window
        if platform.system() == "Windows":
            # Use cmd /c start to open in new window
            process = subprocess.Popen(
                f'start "FIN-DASH Backend" /D "{backend_dir}" "{python_executable}" app.py',
                shell=True
            )
        else:
            process = subprocess.Popen(
                [str(python_executable), 'app.py'],
                cwd=str(backend_dir)
            )

        # Wait for backend to start and check if it's actually serving
        print_info("Waiting for FastAPI to start...")
        max_wait = 10  # Maximum 10 seconds
        start_time = time.time()

        while time.time() - start_time < max_wait:
            # Try to connect to the backend server
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', 8777))
                sock.close()

                if result == 0:
                    # Port is open, server is running
                    print_success("Backend server started successfully")
                    print_info("Backend API: http://127.0.0.1:8777")
                    print_info("API Docs: http://127.0.0.1:8777/docs")
                    return process
            except:
                pass

            time.sleep(0.5)

        # Timeout - server didn't start in time
        print_warning("Backend server is taking longer than expected to start")
        print_info("The server may still be starting. Check the backend console window.")
        return process

    except Exception as e:
        print_error(f"Failed to start backend: {e}")
        return None


def check_port_available(port):
    """Check if a port is available (not in use)."""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result != 0  # Port is available if connection fails
    except:
        return True


def find_frontend_port():
    """Find which port the frontend is actually running on."""
    # Check common Vite ports in order
    ports_to_check = [8080, 5173, 8081, 8082, 8083]

    for port in ports_to_check:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()

            if result == 0:
                return port
        except:
            pass

    return None


def start_frontend():
    """Start the Vite frontend development server."""
    project_root = get_project_root()

    # Check if port 8080 is available
    if not check_port_available(8080):
        print_warning("Port 8080 is already in use. Vite may start on a different port (8081, 8082, etc.)")

    print_info("Starting frontend server (configured for port 8080)...")

    try:
        # Start frontend in a new process
        # Use START command on Windows to open in new window
        if platform.system() == "Windows":
            # Use cmd /c start to open in new window
            process = subprocess.Popen(
                f'start "FIN-DASH Frontend" /D "{project_root}" npm run dev',
                shell=True
            )
        else:
            process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd=str(project_root)
            )

        # Wait for Vite to start and check if it's actually serving
        print_info("Waiting for Vite to start (this may take a few seconds)...")
        max_wait = 15  # Maximum 15 seconds
        start_time = time.time()

        frontend_port = None
        while time.time() - start_time < max_wait:
            # Try to find which port Vite is running on
            frontend_port = find_frontend_port()

            if frontend_port:
                # Port is open, server is running
                print_success("Frontend server started successfully")
                if frontend_port != 8080:
                    print_warning(f"Frontend is running on port {frontend_port} (not 8080 - port was in use)")
                print_info(f"Frontend: http://localhost:{frontend_port}")
                return process

            time.sleep(0.5)

        # Timeout - server didn't start in time
        print_warning("Frontend server is taking longer than expected to start")
        print_info("The server may still be starting. Check the frontend console window.")
        print_info("Frontend should be available at: http://localhost:8080 (or 8081/8082 if port was in use)")
        return process

    except Exception as e:
        print_error(f"Failed to start frontend: {e}")
        return None


def main():
    """Main function to start the application."""
    parser = argparse.ArgumentParser(
        description='Start the FIN-DASH application',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start.py              Start both backend and frontend
  python start.py --backend    Start backend only
  python start.py --frontend   Start frontend only
        """
    )
    parser.add_argument('--backend', action='store_true', help='Start backend only')
    parser.add_argument('--frontend', action='store_true', help='Start frontend only')
    
    args = parser.parse_args()
    
    # If no specific option, start both
    start_both = not (args.backend or args.frontend)
    
    print_header("FIN-DASH Application Startup")
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if args.frontend or start_both:
        if not check_node_installed():
            sys.exit(1)
    
    # Setup backend
    if args.backend or start_both:
        print_header("Setting Up Backend")
        
        if not setup_backend_venv():
            sys.exit(1)
        
        if not install_backend_dependencies():
            sys.exit(1)
    
    # Setup frontend
    if args.frontend or start_both:
        print_header("Setting Up Frontend")
        
        if not install_frontend_dependencies():
            sys.exit(1)
    
    # Start servers
    print_header("Starting Servers")
    
    backend_process = None
    frontend_process = None
    
    try:
        if args.backend or start_both:
            backend_process = start_backend()
            if not backend_process:
                sys.exit(1)
        
        if args.frontend or start_both:
            frontend_process = start_frontend()
            if not frontend_process:
                if backend_process:
                    backend_process.terminate()
                sys.exit(1)
        
        # Print success message
        print_header("FIN-DASH is Running!")

        if backend_process:
            print_success("Backend API: http://127.0.0.1:8777")
            print_success("API Docs: http://127.0.0.1:8777/docs")

        if frontend_process:
            # Try to detect the actual frontend port
            frontend_port = find_frontend_port()
            if frontend_port:
                print_success(f"Frontend: http://localhost:{frontend_port}")
                if frontend_port != 8080:
                    print_info(f"Note: Frontend is on port {frontend_port} because port 8080 was in use")
            else:
                print_success("Frontend: http://localhost:8080 (check console window for actual port)")

        if platform.system() == "Windows":
            print(f"\n{Colors.OKCYAN}Two console windows have been opened for backend and frontend.{Colors.ENDC}")
            print(f"{Colors.OKCYAN}Close those windows to stop the servers.{Colors.ENDC}")
            print(f"{Colors.OKCYAN}You can close this window now - the servers will keep running.{Colors.ENDC}\n")
            print(f"{Colors.OKGREEN}Press Enter to exit this script (servers will continue running)...{Colors.ENDC}")
            input()
        else:
            print(f"\n{Colors.OKCYAN}Press Ctrl+C to stop the servers{Colors.ENDC}\n")

            # Keep the script running and monitor processes
            while True:
                time.sleep(1)

                # Check if processes are still running
                if backend_process and backend_process.poll() is not None:
                    print_error("Backend server stopped unexpectedly")
                    break

                if frontend_process and frontend_process.poll() is not None:
                    print_error("Frontend server stopped unexpectedly")
                    break
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Shutting down servers...{Colors.ENDC}")
        
        if backend_process:
            backend_process.terminate()
            print_success("Backend server stopped")
        
        if frontend_process:
            frontend_process.terminate()
            print_success("Frontend server stopped")
        
        print(f"\n{Colors.OKGREEN}FIN-DASH stopped successfully{Colors.ENDC}\n")
    
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        
        if backend_process:
            backend_process.terminate()
        
        if frontend_process:
            frontend_process.terminate()
        
        sys.exit(1)


if __name__ == "__main__":
    main()

