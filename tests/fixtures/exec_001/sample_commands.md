# CLI Commands Reference - EXEC-001 Samples

## Cross-Platform Commands

### Command: Install Node.js package

**ID**: `cmd_1`
**Platform**: Cross-platform

#### Prerequisites

- Node.js and npm package manager

#### Command

```bash
npm install -g claude-code
```

**Description**: Install Node.js package: claude-code

#### Flags Explained

- `-g`: Global installation

#### Expected Output

```
added 142 packages, and audited 143 packages in 8s
found 0 vulnerabilities
```

#### Common Errors

**Error**: `EACCES permission denied`
**Solution**: Run with sudo or fix npm permissions: npm config set prefix ~/.npm-global

**Error**: `Cannot find module`
**Solution**: Run npm install to install dependencies

**Generated**: 2025-10-06T12:00:00

---

### Command: Install Python package

**ID**: `cmd_2`
**Platform**: Cross-platform

#### Prerequisites

- Python and pip package manager

#### Command

```bash
pip install openai
```

**Description**: Install Python package: openai

#### Expected Output

```
Successfully installed package-name-1.0.0
```

#### Common Errors

**Error**: `Permission denied`
**Solution**: Use --user flag or create virtual environment

**Error**: `No matching distribution found`
**Solution**: Check package name and Python version compatibility

**Generated**: 2025-10-06T12:00:00

---

### Command: Clone repository

**ID**: `cmd_3`
**Platform**: Cross-platform

#### Prerequisites

- Git version control system

#### Command

```bash
git clone https://github.com/user/repo.git
```

**Description**: Clone repository: <https://github.com/user/repo.git>

#### Expected Output

```
Cloning into 'repository'...
remote: Enumerating objects: 100, done.
```

#### Common Errors

**Error**: `Permission denied (publickey)`
**Solution**: Set up SSH keys or use HTTPS with credentials

**Error**: `fatal: not a git repository`
**Solution**: Initialize repository with: git init

**Generated**: 2025-10-06T12:00:00

---

### Command: Build Docker image

**ID**: `cmd_4`
**Platform**: Cross-platform

#### Prerequisites

- Docker engine

#### Command

```bash
docker build -t myapp --no-cache .
```

**Description**: Build Docker image

#### Flags Explained

- `-t`: Output to: myapp
- `--no-cache`: Disable caching

#### Expected Output

```
Command executed successfully
```

#### Common Errors

**Error**: `Cannot connect to Docker daemon`
**Solution**: Ensure Docker service is running

**Error**: `Permission denied`
**Solution**: Add user to docker group or use sudo

**Generated**: 2025-10-06T12:00:00

---

## Usage Tips

### Platform-Specific Notes

**Windows Users**:

- Use PowerShell or Command Prompt
- Some commands may require administrator privileges
- Path separators use backslash `\`

**Linux/Mac Users**:

- Use terminal or shell
- May need `sudo` for system-wide installations
- Path separators use forward slash `/`

### Best Practices

1. **Read prerequisites** before running commands
2. **Understand flags** - they change behavior significantly
3. **Check expected output** to verify success
4. **Consult troubleshooting** if errors occur
5. **Use version flags** to verify installations

### Command Chaining

```bash
# Sequential execution (stops on error)
npm install && npm test && npm run build

# Always continue
npm install; npm test; npm run build

# Run in background
npm start &
```
