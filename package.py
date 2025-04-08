import os
import subprocess
import platform
import shutil

def create_virtual_environment():
    """Create a virtual environment for packaging."""
    subprocess.run(['python', '-m', 'venv', 'venv'], check=True)

def install_dependencies():
    """Install dependencies in the virtual environment."""
    pip_path = 'venv/Scripts/pip' if platform.system() == 'Windows' else 'venv/bin/pip'
    subprocess.run([pip_path, 'install', '-r', 'desktop/requirements.txt'], check=True)
    subprocess.run([pip_path, 'install', 'pyinstaller'], check=True)

def build_executable(platform_name):
    """Build standalone executable using PyInstaller."""
    pyinstaller_path = 'venv/Scripts/pyinstaller' if platform_name == 'Windows' else 'venv/bin/pyinstaller'
    
    # Create dist directory if it doesn't exist
    os.makedirs('dist', exist_ok=True)
    
    # Path separator depends on platform
    separator = ';' if platform_name == 'Windows' else ':'
    
    # Basic command with assets
    build_command = [
        pyinstaller_path, 
        '--onefile', 
        '--windowed',
        f'--add-data=desktop/assets{separator}assets',
        '--name', f'Shortify-{platform_name}',
    ]
    
    # If .env exists in root directory, include it in the package
    if os.path.exists('.env'):
        build_command.append(f'--add-data=.env{separator}.env')
        print("Including .env file from root directory")
    
    # Add the main script at the end
    build_command.append('desktop/main.py')
    
    # Run the PyInstaller command
    print("Running PyInstaller with command:", ' '.join(build_command))
    subprocess.run(build_command, check=True)
    
    # Create a README file with instructions
    with open(os.path.join('dist', 'README.txt'), 'w') as f:
        f.write("""
Shortify - AI Text Summarizer
=============================

Thank you for downloading Shortify!

First-time setup:
1. When first launching Shortify, you'll be asked for your OpenAI API key if one isn't already provided
2. You can get an API key at: https://platform.openai.com/account/api-keys
3. Enter your key in the prompt and Shortify will save it for future use

Usage:
1. Select text in any application
2. Press Ctrl+C to copy it
3. Right-click the Shortify icon and choose an action: Summarize, Paraphrase, or Code Summarize
4. The result will appear in the Shortify window
5. Use the Settings option to customize the behavior

For help or issues, please contact support@shortify.app
""")

def main():
    """Main packaging function"""
    current_platform = 'Windows' if platform.system() == 'Windows' else 'MacOS' if platform.system() == 'Darwin' else 'Linux'
    
    print(f"Packaging Shortify for {current_platform}...")
    
    create_virtual_environment()
    install_dependencies()
    build_executable(current_platform)
    
    print(f"Packaging complete! Check the 'dist' directory for Shortify-{current_platform} and README.txt")

if __name__ == '__main__':
    main()

