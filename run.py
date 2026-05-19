#!/usr/bin/env python3
"""
AutoDS-LLM Quick Start Script
Starts both backend and frontend services
"""

import os
import sys
import subprocess
import time
import platform
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent


def print_banner():
    """Print project banner"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║  🤖 AutoDS-LLM - Automated Data Science Platform          ║
    ║                                                            ║
    ║  Self-Adapting Language Model Pipeline for               ║
    ║  Automated Machine Learning Recommendations              ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)


def check_dependencies():
    """Check if required packages are installed"""
    print("📋 Checking dependencies...")
    
    required_packages = {
        'fastapi': 'backend',
        'streamlit': 'frontend',
        'pandas': 'backend/frontend',
    }
    
    missing = []
    for package in ['fastapi', 'streamlit', 'pandas']:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Please install dependencies:")
        print(f"  pip install -r backend/requirements.txt")
        print(f"  pip install -r frontend/requirements.txt")
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
        'main:app',
        '--host', '0.0.0.0',
        '--port', '8000',
        '--reload'
    ]
    
    try:
        # Change to backend directory
        os.chdir(PROJECT_ROOT / 'backend')
        subprocess.Popen(cmd)
        print("✓ Backend started in separate process")
        time.sleep(3)  # Give backend time to start
        return True
    except Exception as e:
        print(f"✗ Failed to start backend: {e}")
        return False


def start_frontend():
    """Start Streamlit frontend"""
    print("🎨 Starting Frontend (Streamlit)...")
    print("   Running on: http://localhost:8501")
    print()
    
    frontend_app = PROJECT_ROOT / 'frontend' / 'app.py'
    
    cmd = [
        sys.executable,
        '-m',
        'streamlit',
        'run',
        str(frontend_app),
        '--server.port=8501',
        '--server.address=0.0.0.0'
    ]
    
    try:
        # Change to frontend directory
        os.chdir(PROJECT_ROOT / 'frontend')
        subprocess.Popen(cmd)
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
