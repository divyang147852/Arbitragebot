"""
Date extraction utility to parse match dates from URLs
"""

import re
from datetime import datetime, timedelta
from typing import Optional


def extract_date_from_urls(text: str) -> Optional[datetime]:
    """
    Extract match date from Kalshi or Polymarket URLs.
    
    Returns:
        datetime object if date found, None otherwise
    """
    
    # Pattern 1: Polymarket format (YYYY-MM-DD)
    # Example: https://polymarket.com/event/nhl-stl-sj-2026-03-06
    polymarket_pattern = r'polymarket\.com/[^\s]*?(\d{4})-(\d{2})-(\d{2})'
    match = re.search(polymarket_pattern, text, re.IGNORECASE)
    if match:
        try:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            return datetime(year, month, day)
        except (ValueError, IndexError):
            pass
    
    # Pattern 2: Kalshi format (YYmonDD or similar variations)
    # Example: kxnhlgame-26mar06stlsj → 2026-03-06
    kalshi_pattern = r'kalshi\.com/[^\s]*?(\d{2})(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)(\d{2})'
    match = re.search(kalshi_pattern, text, re.IGNORECASE)
    if match:
        try:
            year_short = int(match.group(1))
            month_str = match.group(2).lower()
            day = int(match.group(3))
            
            # Convert month name to number
            month_map = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
                'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            month = month_map.get(month_str)
            
            if month:
                # Assume 20XX for year (2000 + YY)
                year = 2000 + year_short
                return datetime(year, month, day)
        except (ValueError, IndexError):
            pass
    
    return None


def is_match_within_days(text: str, max_days: int = 3) -> bool:
    """
    Check if match date extracted from text is within the next X days.
    Also allows past matches (no lower limit).
    
    Args:
        text: Message text containing URLs
        max_days: Maximum number of days in the future to allow (default: 3)
        
    Returns:
        True if match is within max_days or in the past, False otherwise
        Returns True if no date found (to avoid blocking valid messages)
    """
    
    match_date = extract_date_from_urls(text)
    
    if not match_date:
        # No date found - allow message through
        return True
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    max_date = today + timedelta(days=max_days)
    
    # Allow matches from the past up to max_days in the future
    # No lower limit - past matches are allowed
    if match_date <= max_date:
        return True
    
    return False


def get_match_date_info(text: str) -> dict:
    """
    Get detailed information about match date.
    
    Returns:
        dict with date info and whether it's within range
    """
    match_date = extract_date_from_urls(text)
    
    if not match_date:
        return {
            'date_found': False,
            'date': None,
            'days_away': None,
            'within_range': True,  # Default to allow
            'reason': 'No date found in URLs'
        }
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    days_away = (match_date - today).days
    # Allow past matches and up to 3 days in the future
    within_range = days_away <= 3
    
    return {
        'date_found': True,
        'date': match_date,
        'date_str': match_date.strftime('%Y-%m-%d'),
        'days_away': days_away,
        'within_range': within_range,
        'reason': f'Match is {abs(days_away)} days {"ago" if days_away < 0 else "away"}' if days_away != 0 else 'Match is today'
    }
