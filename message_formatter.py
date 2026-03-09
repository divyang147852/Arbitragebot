"""
Message Formatter Module
Formats raw arbitrage messages into clean, professional format for your channel.
"""

import re
from datetime import datetime, timedelta
from typing import Optional


def extract_date_from_urls(text: str) -> Optional[datetime]:
    """Extract match date from Kalshi or Polymarket URLs."""
    
    # Pattern 1: Polymarket format (YYYY-MM-DD)
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
    
    # Pattern 2: Kalshi format (YYmonDD)
    kalshi_pattern = r'kalshi\.com/[^\s]*?(\d{2})(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)(\d{2})'
    match = re.search(kalshi_pattern, text, re.IGNORECASE)
    if match:
        try:
            year_short = int(match.group(1))
            month_str = match.group(2).lower()
            day = int(match.group(3))
            
            month_map = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
                'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            month = month_map.get(month_str)
            
            if month:
                year = 2000 + year_short
                return datetime(year, month, day)
        except (ValueError, IndexError):
            pass
    
    return None


def format_arbitrage_message(raw_message: str) -> str:
    """
    Transform raw arbitrage message into a nicely formatted message.
    
    Args:
        raw_message: Original message text from source channel
        
    Returns:
        Formatted message ready to post
    """
    
    # Try to extract key information
    info = extract_arbitrage_info(raw_message)
    
    if info['structured']:
        # If we successfully parsed the message, use structured format
        return create_structured_message(info)
    else:
        # Otherwise, use enhanced original format
        return create_enhanced_message(raw_message)


def extract_arbitrage_info(text: str) -> dict:
    """
    Extract structured information from arbitrage message.
    
    Returns a dictionary with extracted fields.
    """
    info = {
        'structured': False,
        'roi': None,
        'sport': None,
        'game': None,
        'market': None,
        'match_date': None,
        'match_date_str': None,
        'line1': None,
        'line1_odds': None,
        'line1_platform': None,
        'line1_link': None,
        'line2': None,
        'line2_odds': None,
        'line2_platform': None,
        'line2_link': None,
        'profit_percent': None
    }
    
    # Extract ROI/Profit percentage - try ROI first, then %
    roi_match = re.search(r'ROI:\s*(\d+\.?\d*)\s*%', text, re.IGNORECASE)
    if roi_match:
        info['roi'] = float(roi_match.group(1))
        info['profit_percent'] = float(roi_match.group(1))
    else:
        profit_match = re.search(r'(\d+\.?\d*)\s*%', text)
        if profit_match:
            info['profit_percent'] = float(profit_match.group(1))
    
    # Extract sport (usually after ROI)
    sport_match = re.search(r'ROI:.*?%\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if sport_match:
        info['sport'] = sport_match.group(1).strip()
    
    # Extract game
    game_match = re.search(r'Game:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if game_match:
        info['game'] = game_match.group(1).strip()
    
    # Extract market
    market_match = re.search(r'Market:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if market_match:
        info['market'] = market_match.group(1).strip()
    
    # Extract match date from URLs
    match_date = extract_date_from_urls(text)
    if match_date:
        info['match_date'] = match_date
        # Format date nicely
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        days_away = (match_date - today).days
        
        if days_away == 0:
            info['match_date_str'] = f"Today ({match_date.strftime('%b %d')})"
        elif days_away == 1:
            info['match_date_str'] = f"Tomorrow ({match_date.strftime('%b %d')})"
        else:
            info['match_date_str'] = match_date.strftime('%B %d, %Y')
    
    # Extract Line 1
    line1_match = re.search(r'Line\s*1:\s*(.+?)\s*@\s*([\d.]+)\s*-\s*(\w+)', text, re.IGNORECASE)
    if line1_match:
        info['line1'] = line1_match.group(1).strip()
        info['line1_odds'] = line1_match.group(2).strip()
        info['line1_platform'] = line1_match.group(3).strip()
    
    # Extract Line 2
    line2_match = re.search(r'Line\s*2:\s*(.+?)\s*@\s*([\d.]+)\s*-\s*(\w+)', text, re.IGNORECASE)
    if line2_match:
        info['line2'] = line2_match.group(1).strip()
        info['line2_odds'] = line2_match.group(2).strip()
        info['line2_platform'] = line2_match.group(3).strip()
    
    # Extract URLs
    url_pattern = r'https?://[^\s)]+'
    links = re.findall(url_pattern, text)
    if len(links) >= 1:
        info['line1_link'] = links[0]
    if len(links) >= 2:
        info['line2_link'] = links[1]
    
    # Check if we have enough info for structured format
    if info['roi'] and info['game'] and info['line1'] and info['line2']:
        info['structured'] = True
    
    return info


def create_structured_message(info: dict) -> str:
    """Create a nicely formatted structured message."""
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Choose emoji based on sport
    sport_emoji = "🏒" if info.get('sport') and 'HOCKEY' in info['sport'].upper() else "⚽" if info.get('sport') and 'SOCCER' in info['sport'].upper() else "🏀" if info.get('sport') and 'BASKETBALL' in info['sport'].upper() else "🎯"
    
    # Choose profit emoji
    roi = info.get('roi') or info.get('profit_percent') or 0
    profit_emoji = "💰" if roi >= 2 else "💵"
    
    lines = [
        f"{sport_emoji} **ARBITRAGE ALERT** {sport_emoji}",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]
    
    # ROI
    if roi:
        lines.append(f"{profit_emoji} **ROI: {roi:.1f}%**")
        lines.append("")
    
    # Match Date (prominent display)
    if info.get('match_date_str'):
        lines.append(f"📅 **Match Date:** {info['match_date_str']}")
        lines.append("")
    
    # Sport
    if info.get('sport'):
        lines.append(f"🏆 **Sport:** {info['sport']}")
    
    # Game
    if info.get('game'):
        lines.append(f"🎮 **Game:** {info['game']}")
    
    # Market
    if info.get('market'):
        lines.append(f"📊 **Market:** {info['market']}")
    
    lines.append("")
    lines.append("**📈 Lines:**")
    lines.append("")
    
    # Line 1
    if info.get('line1'):
        lines.append(f"**Line 1:** {info['line1']}")
        if info.get('line1_odds'):
            lines.append(f"  └ Odds: **{info['line1_odds']}**")
        if info.get('line1_platform'):
            platform_line = f"  └ Platform: **{info['line1_platform']}**"
            if info.get('line1_link'):
                platform_line += f" [🔗 Link]({info['line1_link']})"
            lines.append(platform_line)
        lines.append("")
    
    # Line 2
    if info.get('line2'):
        lines.append(f"**Line 2:** {info['line2']}")
        if info.get('line2_odds'):
            lines.append(f"  └ Odds: **{info['line2_odds']}**")
        if info.get('line2_platform'):
            platform_line = f"  └ Platform: **{info['line2_platform']}**"
            if info.get('line2_link'):
                platform_line += f" [🔗 Link]({info['line2_link']})"
            lines.append(platform_line)
    
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"⏰ {timestamp}")
    
    return "\n".join(lines)


def create_enhanced_message(raw_message: str) -> str:
    """Create enhanced version of original message."""
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    lines = [
        "🎯 **ARBITRAGE ALERT**",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "",
        raw_message.strip(),
        "",
        f"⏰ Posted at {timestamp}",
        "━━━━━━━━━━━━━━━━━━━━━━"
    ]
    
    return "\n".join(lines)


def clean_message_text(text: str) -> str:
    """Clean up message text by removing excessive whitespace and formatting."""
    # Remove multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove excessive spaces
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()
