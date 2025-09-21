"""Credential sharing functionality for Discord CLI."""

import argparse
import os
import sys
import tempfile
from typing import Optional

from .config import load_webhook_config
from .discord_api import send_embed_to_discord, send_file_to_discord, send_message_to_discord


def create_creds_embed(username: str = None, password: str = None, description: str = None,
                      hostname: str = None, service: str = None) -> dict:
    """Create a rich embed for credential sharing."""
    embed = {
        "title": "🔐 Credentials Found",
        "color": 15158332,  # Red color for security/credentials
        "fields": [],
        "timestamp": None
    }

    if description:
        embed["description"] = description

    if hostname:
        embed["fields"].append({
            "name": "🖥️ Host/Target",
            "value": f"`{hostname}`",
            "inline": True
        })

    if service:
        embed["fields"].append({
            "name": "🔧 Service",
            "value": f"`{service}`",
            "inline": True
        })

    if username:
        embed["fields"].append({
            "name": "👤 Username",
            "value": f"```\n{username}\n```",
            "inline": False
        })

    if password:
        embed["fields"].append({
            "name": "🔑 Password",
            "value": f"```\n{password}\n```",
            "inline": False
        })

    # Add warning if no actual credentials provided
    if not username and not password:
        embed["fields"].append({
            "name": "⚠️ Note",
            "value": "Check attached file for credential details",
            "inline": False
        })

    # Add SSH command for SSH service
    if service and service.upper() == "SSH" and hostname:
        ssh_commands = []

        if username and password:
            # Password-based SSH
            ssh_commands.append(f"sshpass -p '{password}' ssh {username}@{hostname}")
        elif username:
            # Key-based SSH (assuming key file will be provided)
            ssh_commands.append(f"ssh {username}@{hostname}")
            ssh_commands.append(f"ssh {username}@{hostname} -i keyfile")

        if ssh_commands:
            embed["fields"].append({
                "name": "🔧 SSH Commands",
                "value": f"```bash\n{chr(10).join(ssh_commands)}\n```",
                "inline": False
            })

    return embed


def create_ssh_key_embed(key_content: str, filename: str, hostname: str = None,
                        username: str = None, description: str = None) -> dict:
    """Create an embed specifically for SSH keys as text."""
    embed = {
        "title": "🔐 SSH Private Key",
        "color": 15158332,  # Red color for security/credentials
        "fields": [],
        "timestamp": None
    }

    if description:
        embed["description"] = description
    else:
        embed["description"] = f"SSH private key: `{filename}`"

    if hostname:
        embed["fields"].append({
            "name": "🖥️ Target Host",
            "value": f"`{hostname}`",
            "inline": True
        })

    if username:
        embed["fields"].append({
            "name": "👤 Username",
            "value": f"`{username}`",
            "inline": True
        })

    # Add the full SSH key content
    embed["fields"].append({
        "name": "🔑 SSH Key",
        "value": f"```\n{key_content}\n```",
        "inline": False
    })

    # Add SSH commands for key files
    if hostname:
        ssh_commands = []

        if username:
            ssh_commands.append(f"ssh {username}@{hostname} -i {filename}")
        else:
            ssh_commands.append(f"ssh user@{hostname} -i {filename}")

        # Add setup commands
        ssh_commands.append(f"chmod 600 {filename}")

        embed["fields"].append({
            "name": "🔧 SSH Commands",
            "value": f"```bash\n{chr(10).join(ssh_commands)}\n```",
            "inline": False
        })

    return embed


def handle_creds_command(username: str = None, password: str = None, file_path: str = None,
                        description: str = None, hostname: str = None, service: str = None):
    """Handle credentials sharing command."""
    # Show help if no arguments provided
    if not username and not password and not file_path and not description and not hostname and not service:
        print("dc creds - Share credentials securely with your team via Discord")
        print()
        print("Usage:")
        print("  dc creds -u USERNAME -p PASSWORD [-H hostname] [-s service] [-d description]")
        print("  dc creds -f FILE [-H hostname] [-s service] [-d description]")
        print("  dc creds -u USERNAME [-H hostname] [-s service] [-d description]")
        print()
        print("Options:")
        print("  -u, --username     Username to share")
        print("  -p, --password     Password to share")
        print("  -f, --file         Credential file to upload (e.g., SSH keys, credential dumps)")
        print("  -d, --description  Description of the credentials")
        print("  -H, --hostname     Target hostname or IP")
        print("  -s, --service      Service name (e.g., SSH, HTTP, SMB)")
        print()
        print("Examples:")
        print("  dc creds -u admin -p password123 -H 10.10.10.1")
        print("  dc creds -u root -p toor -s SSH -d \"Root access to target\"")
        print("  dc creds -f id_rsa -H target.example.com -s SSH")
        print("  dc creds -f creds.txt -d \"Found in /etc/passwd\"")
        return

    try:
        webhook_url, thread_id, needs_thread = load_webhook_config()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Validate that we have some credentials to share
    if not username and not password and not file_path:
        print("Error: Must provide username, password, or file to share credentials.")
        print("Use 'dc creds --help' for usage information.")
        sys.exit(1)

    # Handle file sharing
    if file_path:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            sys.exit(1)

        filename = os.path.basename(file_path)

        # Check if it's likely an SSH key file
        is_ssh_key = (
            'id_' in filename.lower() or
            filename.lower().endswith(('.pem', '.key')) or
            'ssh' in filename.lower() or
            service and service.upper() == "SSH"
        )

        # Read file content to check if it's an SSH key
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()

            # Check if content looks like an SSH key
            is_ssh_key_content = (
                "BEGIN RSA PRIVATE KEY" in file_content or
                "BEGIN OPENSSH PRIVATE KEY" in file_content or
                "BEGIN DSA PRIVATE KEY" in file_content or
                "BEGIN EC PRIVATE KEY" in file_content or
                "BEGIN PRIVATE KEY" in file_content
            )

            if (is_ssh_key or is_ssh_key_content):
                # Handle SSH keys as text in embed
                embed = create_ssh_key_embed(file_content, filename, hostname, username, description)

                # Send embed with full SSH key
                status_code, response_text = send_embed_to_discord(
                    embed, webhook_url, thread_id, needs_thread, "Credentials"
                )

                if status_code in [200, 204]:
                    print(f"SSH key '{filename}' shared successfully as text.")
                else:
                    print(f"Error sending SSH key: {status_code} - {response_text}")
                return

        except UnicodeDecodeError:
            # File is binary, not a text-based SSH key
            pass

        # Handle as regular file upload for non-SSH files or binary files
        embed = create_creds_embed(
            description=description or f"Credential file: {filename}",
            hostname=hostname,
            service=service
        )

        # Send embed first
        status_code, response_text = send_embed_to_discord(
            embed, webhook_url, thread_id, needs_thread, "Credentials"
        )

        if status_code not in [200, 204]:
            print(f"Error sending credential embed: {status_code} - {response_text}")
            return

        # Then send the file
        status_code, response_text = send_file_to_discord(
            file_path, webhook_url, thread_id, needs_thread,
            f"🔐 Credential file: {filename}", "Credentials"
        )

        if status_code in [200, 204]:
            print(f"Credential file '{file_path}' shared successfully.")
        else:
            print(f"Error sending credential file: {status_code} - {response_text}")

    else:
        # Handle username/password sharing
        embed = create_creds_embed(
            username=username,
            password=password,
            description=description,
            hostname=hostname,
            service=service
        )

        status_code, response_text = send_embed_to_discord(
            embed, webhook_url, thread_id, needs_thread, "Credentials"
        )

        if status_code in [200, 204]:
            cred_types = []
            if username:
                cred_types.append("username")
            if password:
                cred_types.append("password")
            print(f"Credentials ({', '.join(cred_types)}) shared successfully.")
        else:
            print(f"Error sending credentials: {status_code} - {response_text}")


def main():
    """Main entry point for dccreds command."""
    parser = argparse.ArgumentParser(
        description="Share credentials securely with your team via Discord.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dc creds -u admin -p password123 -H 10.10.10.1
  dc creds -u root -p toor -s SSH -d "Root access to target"
  dc creds -f id_rsa -H target.example.com -s SSH
  dc creds -f creds.txt -d "Found in /etc/passwd"
"""
    )

    parser.add_argument('-u', '--username', help='Username to share')
    parser.add_argument('-p', '--password', help='Password to share')
    parser.add_argument('-f', '--file', help='Credential file to upload (e.g., SSH keys, credential dumps)')
    parser.add_argument('-d', '--description', help='Description of the credentials')
    parser.add_argument('-H', '--hostname', help='Target hostname or IP')
    parser.add_argument('-s', '--service', help='Service name (e.g., SSH, HTTP, SMB)')

    args = parser.parse_args()

    handle_creds_command(
        username=args.username,
        password=args.password,
        file_path=args.file,
        description=args.description,
        hostname=args.hostname,
        service=args.service
    )


if __name__ == "__main__":
    main()