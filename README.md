# DavineLuLinvega

<p align="center">
  <img src="https://i.pinimg.com/originals/80/2f/c1/802fc1cd743108d1bc271203d217856e.jpg" width="400">

# CLI tools for quickly sending CLI stuff to Discord channels

A Python package containing CLI tools designed to help in the process of sharing files, tool output, clipboard content, and credentials via Discord during CTFs or competitive hacking events. These tools enable quick and efficient sharing of command output, files, clipboard data, and credential information to designated Discord channels or threads, making team collaboration easier and faster.

## Installation

Install directly from GitHub using pipx (recommended):
```bash
pipx install git+https://github.com/username/DavineLuLinvega.git
```

Or install using uv:
```bash
uv tool install git+https://github.com/username/DavineLuLinvega.git
```

For development installation:
```bash
git clone https://github.com/username/DavineLuLinvega.git
cd DavineLuLinvega
pip install -e .
```

## Overview

The `dc` command provides several subcommands for Discord integration:

1. **`dc setup`**: Quick setup wizard for first-time configuration with webhook validation and thread discovery.
2. **`dc manage`**: Manage Discord webhooks, threads, and settings for efficient setup and customization.
3. **`dc log`**: Send terminal command output directly to Discord for real-time collaboration.
4. **`dc send`**: Share files and artifacts with teammates through Discord.
5. **`dc clip`**: Send clipboard content (text, images, or file paths) directly to Discord for quick sharing of results and findings.
6. **`dc creds`**: Share credentials with automated SSH command generation.


## Configuration

Discord CLI uses a centralized JSON configuration system stored at `~/.config/discord-cli/config.json`. This replaces the old `.env` file approach for better organization and features.

### Quick Setup

For first-time setup, use the setup wizard:

```bash
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$  dc setup
```

This will guide you through:
- Adding your first webhook with validation
- Discovering and configuring threads
- Setting up your username
- Configuring thread usage preferences

### Manual Configuration

You can also manage configuration manually:

```bash
# Add webhooks
dc manage add-webhook main https://discord.com/api/webhooks/your-webhook-id/your-webhook-token --default

# Add threads
dc manage add-thread general 123456789012345678 --force

# Configure settings
dc manage set-username YourName
dc manage enable-thread

# View current configuration
dc manage show-config
```

### Migration from .env

If you have an existing `.env` file, it will be automatically migrated:

```bash
dc manage migrate
```

## Commands

### dc setup

Interactive setup wizard for first-time configuration.

#### Usage

```bash
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$  dc setup
```

Guides you through:
- Webhook validation and setup
- Thread discovery and configuration
- Username customization
- Thread usage preferences

### dc manage

Manages webhooks, threads, and settings for your Discord configurations.

#### Usage

```bash
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc manage <command> [arguments]
```

#### Commands

- **Webhooks**
  - `list-webhooks`: List all saved webhooks.
  - `add-webhook <name> <url> [--default]`: Add a new webhook with the specified name and URL. Optionally sets it as the default.
  - `set-default-webhook <name>`: Set a webhook as the default.
  - `remove-webhook <name>`: Remove a saved webhook.

- **Threads**
  - `list-threads`: List all saved threads.
  - `add-thread <name> <thread_id> [--force]`: Add a new thread and optionally set it as the default.
  - `set-default-thread <name>`: Set a saved thread as the default.
  - `enable-thread`: Enable thread usage for webhooks.
  - `disable-thread`: Disable thread usage for webhooks.

#### Examples

```bash
# List all saved webhooks
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc manage list-webhooks

# Add a new webhook and set it as the default
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc manage add-webhook HTB-Machines https://discord.com/api/webhooks/12345/abcdef --default

# Set an existing webhook as default
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc manage set-default-webhook HTB-Machines

# List all threads
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc manage list-threads

# Add a new thread and set it as default
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc manage add-thread Reaper 987654321098765432 --force
```

### dc log

This script captures the output of a terminal command and sends it to Discord. If the output is longer than 2000 characters, it sends the output as a file.

#### Usage

```bash
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc log [-c COMMENT] <command>
```

#### Options

- `-c, --comment`: Optional comment to include with the output.
- `<command>`: The terminal command to execute.

#### Examples

```bash
# Send output of the `ls` command
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc log -c "Listing directory" ls -la

# Send content of a file to Discord
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc log cat large_file.txt
```

#### Quick Usage

With an alias set up, you can use the `!!` command in combination with an alias like `dl` to send the output of your last terminal command directly to Discord.

```bash
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ ls -la
# You want to send this output to Discord
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dl !!
```

- **`!!`** repeats the last command you executed.
- **`dl !!`** runs `dc log` with the output of the previous command, sending it directly to your Discord channel.

### dc send

This script uploads files to Discord using a webhook.

#### Usage

```bash
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc send <file> [-c COMMENT]
```

#### Options

- `<file>`: The path of the file to upload.
- `-c, --comment`: Optional comment to include with the file.

#### Examples

```bash
# Send a file with a comment
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc send report.pdf -c "Here is the report"

# Send a file without a comment
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc send backup.zip
```

### dc clip

This script sends the current clipboard content to Discord. It can handle text, images, and file paths copied to the clipboard.

#### Usage

Run `dc clip` without any arguments to send the current clipboard content to Discord.

```bash
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc clip
```

### Examples

- If the clipboard contains text, it sends the text directly:
  ```bash
  ┌──(kali😈kali)-[~/DavineLuLinvega]
  └─$ dc clip
  Clipboard content sent successfully.
  ```
- If the clipboard contains an image, it uploads the image as a file:
  ```bash
  ┌──(kali😈kali)-[~/DavineLuLinvega]
  └─$ dc clip
  Image sent successfully.
  ```
- If the clipboard contains a file path (e.g., `file:///path/to/file.txt`), it uploads the file:
  ```bash
  ┌──(kali😈kali)-[~/DavineLuLinvega]
  └─$ dc clip
  File sent successfully.
  ```

### dc creds

Share credentials securely with your team via Discord with rich formatting and SSH command generation.

#### Usage

```bash
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$  dc creds [options]
```

#### Options

- `-u, --username`: Username to share
- `-p, --password`: Password to share
- `-f, --file`: Credential file to upload (e.g., SSH keys, credential dumps)
- `-d, --description`: Description of the credentials
- `-H, --hostname`: Target hostname or IP
- `-s, --service`: Service name (e.g., SSH, HTTP, SMB)

#### Examples

```bash
# Share username and password
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc creds -u admin -p password123 -H 10.10.10.1

# Share SSH credentials with commands
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc creds -u root -p toor -s SSH -d "Root access to target"

# Share SSH private key as inline text
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc creds -f id_rsa -H target.example.com -s SSH

# Share credential file with description
┌──(kali😈kali)-[~/DavineLuLinvega]
└─$ dc creds -f creds.txt -d "Found in /etc/passwd"
```

**Features:**
- SSH keys are automatically sent as copyable inline text
- SSH service generates ready-to-use command examples
- Rich Discord embeds with color coding and organized fields
- Supports both username/password and file-based credentials

## Key Features

- **Centralized Configuration**: Modern JSON-based config system at `~/.config/discord-cli/config.json`
- **Interactive Setup**: Guided setup wizard with webhook validation and thread discovery
- **Multiple Webhooks & Threads**: Support for multiple configurations with easy switching
- **Customizable Username**: Set your own username for Discord messages instead of hardcoded values
- **Rich Credential Sharing**: Specialized `dc creds` command with SSH key support and command generation
- **Clean Formatting**: ASCII-based displays that work across all terminal environments
- **Legacy Migration**: Automatic migration from old `.env` file configurations
