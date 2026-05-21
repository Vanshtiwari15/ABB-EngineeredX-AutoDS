#!/usr/bin/env python
"""
AutoDS-LLM Startup Script
Starts FastAPI backend with agent-based workflow
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Start the AutoDS-LLM application."""
    
    # Get project root
    project_root = Path(__file__).parent.resolve()
    
    print("=" * 70)
    print("🤖 AutoDS-LLM - Automated Data Science with Agent-Based Workflow")
    print("=" * 70)
    
    # Check if venv is activated
    if sys.prefix == sys.base_prefix:
        print("\n⚠️  Warning: Virtual environment not detected!")
        print("Please activate your virtual environment first:")
        print("  Windows: .venv\\Scripts\\activate")
        print("  Linux/Mac: source .venv/bin/activate")
    
    # Change to project root
    os.chdir(project_root)
    
    print("\n📦 Project structure verified:")
    required_dirs = ["backend", "frontend", "outputs", "backend/models"]
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        status = "✓" if dir_path.exists() else "✗"
        print(f"  {status} {dir_name}")
    
    # Create necessary directories
    (project_root / "backend" / "models" / "trained_models").mkdir(parents=True, exist_ok=True)
    (project_root / "outputs" / "reports").mkdir(parents=True, exist_ok=True)
    
    print("\n🚀 Starting AutoDS-LLM...")
    print("-" * 70)
    
    try:
        print("\n📡 Starting FastAPI backend on http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        print("\n🌐 Frontend: http://localhost:8000/index.html")
        print("\nPress Ctrl+C to stop the server.\n")
        
        # Start backend
        backend_cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
        ]
        
        subprocess.run(backend_cmd, cwd=str(project_root))
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down AutoDS-LLM...")
        print("Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()


def check_dependencies():
    """Check if required packages are installed"""
    print("📋 Checking dependencies...")
    
    required_modules = ['fastapi', 'uvicorn', 'pandas']
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module} - NOT INSTALLED")
            missing.append(module)

    node_missing = False
    try:
        subprocess.run(['node', '--version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print('  ✓ node')
    except Exception:
        print('  ✗ node - NOT INSTALLED or not on PATH')
        node_missing = True

    if missing or node_missing:
        if missing:
            print(f"\n⚠️  Missing Python packages: {', '.join(missing)}")
        if node_missing:
            print('\n⚠️  Node.js is required for the React frontend.')
        print("Please install dependencies:")
        print(f"  pip install -r backend/requirements.txt")
        print(f"  cd frontend && npm install")
        return False
    
    print("\n✓ All dependencies installed!\n")
    return True


def generate_sample_data():
    """Generate sample datasets"""
    print("📊 Generating sample datasets...")
    
    datasets_script = PROJECT_ROOT / 'datasets' / 'generate_samples.py'
    
    try:
        subprocess.run([sys.executable, str(datasets_script)], check=True)
        print("✓ Sample datasets generated!\n")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to generate sample datasets")
        return False


def start_backend():
    """Start FastAPI backend"""
    print("🚀 Starting Backend (FastAPI)...")
    print("   Running on: http://localhost:8000")
    print("   API Docs: http://localhost:8000/api/docs")
    print("   Health Check: http://localhost:8000/api/health")
    print()
    
    backend_main = PROJECT_ROOT / 'backend' / 'main.py'
    
    cmd = [
        sys.executable,
        '-m',
        'uvicorn',
        'backend.main:app',
        '--host', '0.0.0.0',
        '--port', '8000',
        '--reload'
    ]
    
    try:
        subprocess.Popen(cmd, cwd=str(PROJECT_ROOT))
        print("✓ Backend started in separate process")
        time.sleep(3)  # Give backend time to start
        return True
    except Exception as e:
        print(f"✗ Failed to start backend: {e}")
        return False


def start_frontend():
    """Start React frontend"""
    print("🎨 Starting Frontend (React + Tailwind)...")
    print("   Running on: http://localhost:8501")
    print()
    
    cmd = [
        'npm',
        'run',
        'dev',
    ]
    
    try:
        subprocess.Popen(cmd, cwd=str(PROJECT_ROOT / 'frontend'))
        print("✓ Frontend started in separate process")
        return True
    except Exception as e:
        print(f"✗ Failed to start frontend: {e}")
        return False


def main():
    """Main entry point"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependencies not installed. Exiting.")
        sys.exit(1)
    
    # Generate sample data
    if not generate_sample_data():
        print("\n⚠️  Sample data generation failed, but continuing...")
    
    # Start services
    print("=" * 60)
    print("🎯 STARTING SERVICES")
    print("=" * 60)
    print()
    
    backend_ok = start_backend()
    frontend_ok = start_frontend()
    
    print()
    print("=" * 60)
    print("✨ APPLICATION STARTED")
    print("=" * 60)
    print()
    print("📌 Quick Links:")
    print("   🏠 Dashboard: http://localhost:8501")
    print("   🔌 Backend: http://localhost:8000")
    print("   📚 API Docs: http://localhost:8000/api/docs")
    print()
    print("💡 To stop the application:")
    print("   Press Ctrl+C in this terminal, or close the windows")
    print()
    
    if backend_ok and frontend_ok:
        print("✓ Both services started successfully!")
        print("\n🎉 Opening dashboard in browser...")
        
        # Open browser
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', 'http://localhost:8501'])
            elif platform.system() == 'Windows':
                subprocess.run(['start', 'http://localhost:8501'], shell=True)
            else:  # Linux
                subprocess.run(['xdg-open', 'http://localhost:8501'])
        except:
            pass
        
        # Keep script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down services...")
            sys.exit(0)
    else:
        print("❌ Failed to start one or more services")
        sys.exit(1)


if __name__ == "__main__":
    main()
