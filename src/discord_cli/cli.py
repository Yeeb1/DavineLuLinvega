"""Main CLI interface for Discord CLI tools."""

import argparse
import sys

from . import __version__
from .manage import (
    list_webhooks, add_webhook, set_default_webhook_interactive, remove_webhook,
    list_threads, add_thread, set_default_thread_interactive, enable_thread_ids, disable_thread_ids,
    show_username, set_username_interactive
)
from .config import show_config, migrate_from_env
from .setup_wizard import quick_setup
from .log import handle_log_command
from .send import handle_send_command
from .clip import handle_clip_command
from .creds import handle_creds_command


def create_parser():
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog='dc',
        description='Discord CLI tools for CTF and hacking collaboration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dc manage add-webhook main https://discord.com/api/webhooks/...
  dc log -c "Directory listing" ls -la
  dc send report.pdf -c "Here's the report"
  dc clip
"""
    )
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Manage subcommand
    manage_parser = subparsers.add_parser('manage', help='Manage webhooks and threads')
    manage_subparsers = manage_parser.add_subparsers(dest='manage_command', help='Management commands')

    # Webhook commands
    manage_subparsers.add_parser('list-webhooks', help='List all saved webhooks')

    add_webhook_parser = manage_subparsers.add_parser('add-webhook', help='Add a new webhook')
    add_webhook_parser.add_argument('name', help='Webhook name')
    add_webhook_parser.add_argument('url', help='Webhook URL')
    add_webhook_parser.add_argument('--default', action='store_true', help='Set as default webhook')

    manage_subparsers.add_parser('set-default-webhook', help='Set a webhook as default')
    manage_subparsers.add_parser('remove-webhook', help='Remove a saved webhook')

    # Thread commands
    manage_subparsers.add_parser('list-threads', help='List all saved threads')

    add_thread_parser = manage_subparsers.add_parser('add-thread', help='Add a new thread')
    add_thread_parser.add_argument('name', help='Thread name')
    add_thread_parser.add_argument('thread_id', help='Thread ID')
    add_thread_parser.add_argument('--force', action='store_true', help='Set as default thread')

    manage_subparsers.add_parser('set-default-thread', help='Set a thread as default')
    manage_subparsers.add_parser('enable-thread', help='Enable thread usage')
    manage_subparsers.add_parser('disable-thread', help='Disable thread usage')

    # Config commands
    manage_subparsers.add_parser('show-config', help='Show current configuration')
    manage_subparsers.add_parser('migrate', help='Migrate from .env file to new config system')
    manage_subparsers.add_parser('setup', help='Run quick setup wizard for first-time configuration')

    # Username commands
    manage_subparsers.add_parser('show-username', help='Show current username')
    manage_subparsers.add_parser('set-username', help='Set Discord username')

    # Log subcommand
    log_parser = subparsers.add_parser('log', help='Send command output to Discord')
    log_parser.add_argument('-c', '--comment', help='Optional comment to include')
    log_parser.add_argument('cmd_args', nargs=argparse.REMAINDER, help='The command to execute')

    # Send subcommand
    send_parser = subparsers.add_parser('send', help='Send files to Discord')
    send_parser.add_argument('file', help='The file to upload')
    send_parser.add_argument('-c', '--comment', help='Optional comment to include')

    # Clip subcommand
    subparsers.add_parser('clip', help='Send clipboard content to Discord')

    # Creds subcommand
    creds_parser = subparsers.add_parser('creds', help='Share credentials securely with your team')
    creds_parser.add_argument('-u', '--username', help='Username to share')
    creds_parser.add_argument('-p', '--password', help='Password to share')
    creds_parser.add_argument('-f', '--file', help='Credential file to upload (e.g., SSH keys, credential dumps)')
    creds_parser.add_argument('-d', '--description', help='Description of the credentials')
    creds_parser.add_argument('-H', '--hostname', help='Target hostname or IP')
    creds_parser.add_argument('-s', '--service', help='Service name (e.g., SSH, HTTP, SMB)')

    # Setup subcommand (alias for manage setup)
    subparsers.add_parser('setup', help='Quick setup wizard for first-time configuration')

    return parser


def handle_manage_command(args):
    """Handle manage subcommands."""
    if not args.manage_command:
        print("Available management commands:")
        print()
        print("Webhook management:")
        print("  list-webhooks      List all saved webhooks")
        print("  add-webhook        Add a new webhook")
        print("  set-default-webhook Set a webhook as default")
        print("  remove-webhook     Remove a saved webhook")
        print()
        print("Thread management:")
        print("  list-threads       List all saved threads")
        print("  add-thread         Add a new thread")
        print("  set-default-thread Set a thread as default")
        print("  enable-thread      Enable thread usage")
        print("  disable-thread     Disable thread usage")
        print()
        print("Configuration:")
        print("  show-config        Show current configuration")
        print("  migrate            Migrate from .env file")
        print("  setup              Run quick setup wizard")
        print()
        print("Username:")
        print("  show-username      Show current Discord username")
        print("  set-username       Set Discord username")
        print()
        print("Use 'dc manage <command> --help' for detailed help on each command.")
        return

    if args.manage_command == 'list-webhooks':
        list_webhooks()
    elif args.manage_command == 'add-webhook':
        add_webhook(args.name, args.url, args.default)
    elif args.manage_command == 'set-default-webhook':
        set_default_webhook_interactive()
    elif args.manage_command == 'remove-webhook':
        remove_webhook()
    elif args.manage_command == 'list-threads':
        list_threads()
    elif args.manage_command == 'add-thread':
        add_thread(args.name, args.thread_id, args.force)
    elif args.manage_command == 'set-default-thread':
        set_default_thread_interactive()
    elif args.manage_command == 'enable-thread':
        enable_thread_ids()
    elif args.manage_command == 'disable-thread':
        disable_thread_ids()
    elif args.manage_command == 'show-config':
        show_config()
    elif args.manage_command == 'migrate':
        migrate_from_env()
    elif args.manage_command == 'setup':
        quick_setup()
    elif args.manage_command == 'show-username':
        show_username()
    elif args.manage_command == 'set-username':
        set_username_interactive()
    else:
        print(f"Error: Unknown management command '{args.manage_command}'.")
        print("Use 'dc manage --help' for available commands.")
        sys.exit(1)


def main():
    """Main entry point for the dc command."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'manage':
        handle_manage_command(args)
    elif args.command == 'log':
        handle_log_command(args.cmd_args, args.comment)
    elif args.command == 'send':
        handle_send_command(args.file, args.comment)
    elif args.command == 'clip':
        handle_clip_command()
    elif args.command == 'creds':
        handle_creds_command(
            username=args.username,
            password=args.password,
            file_path=args.file,
            description=args.description,
            hostname=args.hostname,
            service=args.service
        )
    elif args.command == 'setup':
        quick_setup()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()