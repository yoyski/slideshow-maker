"""
Test script to verify all dependencies are installed correctly
"""
import sys
import importlib

def test_import(module_name, package_name=None):
    """Test if a package can be imported"""
    if package_name is None:
        package_name = module_name
    
    try:
        importlib.import_module(module_name)
        print(f"✓ {package_name}")
        return True
    except ImportError as e:
        print(f"✗ {package_name}: {e}")
        return False

def main():
    print("Voice Slideshow Maker - Dependency Check")
    print("=" * 50)
    print()
    
    packages = [
        ("flask", "Flask"),
        ("flask_cors", "Flask-CORS"),
        ("librosa", "librosa"),
        ("numpy", "numpy"),
        ("scipy", "scipy"),
        ("cv2", "OpenCV"),
        ("PIL", "Pillow"),
        ("soundfile", "soundfile"),
        ("werkzeug", "werkzeug"),
        ("dotenv", "python-dotenv"),
    ]
    
    results = []
    for module, name in packages:
        results.append(test_import(module, name))
    
    print()
    print("=" * 50)
    
    if all(results):
        print("✓ All dependencies installed successfully!")
        print()
        print("You can now run the application:")
        print("  python app.py")
        return 0
    else:
        print(f"✗ {sum(1 for r in results if not r)} package(s) missing")
        print()
        print("Install missing packages with:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
