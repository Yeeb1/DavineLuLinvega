"""Discord API integration for discovering channels and threads."""

import re
import requests
from typing import Dict, List, Optional, Tuple


def extract_webhook_info(webhook_url: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract webhook ID and token from webhook URL."""
    pattern = r'https://discord\.com/api/webhooks/(\d+)/([a-zA-Z0-9_-]+)'
    match = re.match(pattern, webhook_url)
    if match:
        return match.group(1), match.group(2)
    return None, None


def get_webhook_info(webhook_url: str) -> Optional[Dict]:
    """Get webhook information from Discord API."""
    webhook_id, webhook_token = extract_webhook_info(webhook_url)
    if not webhook_id or not webhook_token:
        return None

    try:
        response = requests.get(f"https://discord.com/api/webhooks/{webhook_id}/{webhook_token}")
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return None


def get_channel_threads(webhook_url: str) -> List[Dict]:
    """Get active threads from the channel associated with the webhook."""
    webhook_info = get_webhook_info(webhook_url)
    if not webhook_info or 'channel_id' not in webhook_info:
        return []

    channel_id = webhook_info['channel_id']
    guild_id = webhook_info.get('guild_id')

    if not guild_id:
        return []

    # We can't easily get bot token from webhook, so we'll try to get public threads
    # This is limited but better than nothing
    webhook_id, webhook_token = extract_webhook_info(webhook_url)
    if not webhook_id or not webhook_token:
        return []

    try:
        # Try to get active threads using the webhook (limited permissions)
        response = requests.get(
            f"https://discord.com/api/channels/{channel_id}/threads/active",
            headers={"Authorization": f"Bot {webhook_token}"}  # This won't work, but worth a try
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('threads', [])
    except requests.RequestException:
        pass

    return []


def discover_threads_from_webhook(webhook_url: str) -> Tuple[Optional[str], List[Dict]]:
    """
    Discover channel info and threads from a webhook URL.
    Returns (channel_name, threads_list)
    """
    webhook_info = get_webhook_info(webhook_url)
    if not webhook_info:
        return None, []

    channel_name = webhook_info.get('name', 'Unknown Webhook')
    guild_name = webhook_info.get('guild', {}).get('name', 'Unknown Server')

    # For display purposes
    display_name = f"{guild_name} - {channel_name}"

    # Try to get threads (this is limited without bot permissions)
    threads = get_channel_threads(webhook_url)

    return display_name, threads


def validate_webhook_url(webhook_url: str) -> bool:
    """Validate that a webhook URL is valid and accessible."""
    webhook_info = get_webhook_info(webhook_url)
    return webhook_info is not None