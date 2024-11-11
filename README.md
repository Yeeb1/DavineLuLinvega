# DavineLuLinvega

<p align="center">
  <img src="https://i.pinimg.com/originals/80/2f/c1/802fc1cd743108d1bc271203d217856e.jpg" width="400">

# Discord CLI Tools for CTFs and Competitive Hacking

This repository contains a set of Python scripts designed to help in the process of sharing files, tool output, and clipboard content via Discord during CTFs or competitive hacking events. These tools enable quick and efficient sharing of command output, files, and clipboard data to designated Discord channels or threads, making team collaboration easier and faster.

## Overview

1. **`dcmanage.py`**: Manage Discord webhooks and thread IDs for efficient setup and customization.
2. **`dclog.py`**: Send terminal command output directly to Discord for real-time collaboration.
3. **`dcsend.py`**: Share files and artifacts with teammates through Discord.
4. **`dcclip.py`**: Send clipboard content (text, images, or file paths) directly to Discord for quick sharing of results and findings.


## Environment Configuration

These scripts use environment variables stored in a `.env` file located in your home directory (`~/.env`). Ensure the file is set up as follows:

```bash
export DISCORD_WEBHOOK_URL='https://discord.com/api/webhooks/your-webhook-id/your-webhook-token'
export THREAD_ID='123456789012345678'
export WEBHOOK_NEEDS_THREAD='true'
```

- **DISCORD_WEBHOOK_URL**: Your Discord webhook URL.
- **THREAD_ID**: The ID of the Discord thread (if applicable).
- **WEBHOOK_NEEDS_THREAD**: Set to `'true'` if the webhook requires a thread ID.

## Scripts

### dcmanage.py

Manages webhooks and thread IDs for your Discord webhook configurations.

#### Usage

```bash
┌──(kalikali)-[~/DavineLuLinvega]
└─$ dcmanage.py <command> [arguments]
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
┌──(kalikali)-[~/DavineLuLinvega]
└─$ dcmanage.py list-webhooks

# Add a new webhook and set it as the default
┌──(kalikali)-[~/DavineLuLinvega]
└─$ dcmanage.py add-webhook MainWebhook https://discord.com/api/webhooks/12345/abcdef --default

# Set an existing webhook as default
┌──(kalikali)-[~/DavineLuLinvega]
└─$ dcmanage.py set-default-webhook MainWebhook

# List all threads
┌──(kalikali)-[~/DavineLuLinvega]
└─$ dcmanage.py list-threads

# Add a new thread and set it as default
┌──(kalikali)-[~/DavineLuLinvega]
└─$ dcmanage.py add-thread GeneralDiscussion 987654321098765432 --force
```

### dclog.py

This script captures the output of a terminal command and sends it to Discord. If the output is longer than 2000 characters, it sends the output as a file.

#### Usage

```bash
┌──(kalikali)-[~/DavineLuLinvega]
└─$ dclog.py [-c COMMENT] <command>
```

#### Options

- `-c, --comment`: Optional comment to include with the output.
- `<command>`: The terminal command to execute.

#### Examples

```bash
# Send output of the `ls` command
┌──(kalikali)-[~/DavineLuLinvega]
└─$ dclog.py -c "Listing directory" ls -la

# Send content of a file to Discord
┌──(kalikali)-[~/DavineLuLinvega]
└─$ dclog.py cat large_file.txt
```

### dcsend.py

This script uploads files to Discord using a webhook.

#### Usage

```bash
┌──(kalikali)-[~/DavineLuLinvega]
└─$ dcsend.py <file> [-c COMMENT]
```

#### Options

- `<file>`: The path of the file to upload.
- `-c, --comment`: Optional comment to include with the file.

#### Examples

```bash
# Send a file with a comment
┌──(kalikali)-[~/DavineLuLinvega]
└─$ dcsend.py report.pdf -c "Here is the report"

# Send a file without a comment
┌──(kalikali)-[~/DavineLuLinvega]
└─$ dcsend.py backup.zip
```

### dcclip.py

This script sends the current clipboard content to Discord. It can handle text, images, and file paths copied to the clipboard.

#### Usage

Run `dcclip.py` without any arguments to send the current clipboard content to Discord.

```bash
┌──(kalikali)-[~/DavineLuLinvega]
└─$ dcclip.py
```

### Examples

- If the clipboard contains text, it sends the text directly:
  ```bash
  ┌──(kalikali)-[~/DavineLuLinvega]
  └─$ dcclip.py
  Clipboard content sent successfully.
  ```
- If the clipboard contains an image, it uploads the image as a file:
  ```bash
  ┌──(kalikali)-[~/DavineLuLinvega]
  └─$ dcclip.py
  Image sent successfully.
  ```
- If the clipboard contains a file path (e.g., `file:///path/to/file.txt`), it uploads the file:
  ```bash
  ┌──(kalikali)-[~/DavineLuLinvega]
  └─$ dcclip.py
  File sent successfully.
  ```
