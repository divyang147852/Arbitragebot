"""
Message Formatter Module
Formats raw arbitrage messages into clean, professional format for your channel.
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional

# Indian Standard Time (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))


def to_market_cents(value_text: str) -> Optional[int]:
    """
    Convert a line value into market cents (0-100).

    Supported inputs:
    - Decimal odds (e.g., 1.63 -> 61¢)
    - Probability decimal (e.g., 0.63 -> 63¢)
    - Cents/integer price (e.g., 63 -> 63¢)
    - American odds (e.g., +150 -> 40¢, -150 -> 60¢)
    """
    try:
        value = float(value_text)
    except (TypeError, ValueError):
        return None

    if value <= 0:
        return None

    if value_text.strip().startswith(('+', '-')):
        if value > 0:
            probability = 100 / (value + 100)
        else:
            abs_value = abs(value)
            probability = abs_value / (abs_value + 100)
        cents = round(probability * 100)
        return max(0, min(100, cents))

    if value <= 1:
        cents = round(value * 100)
        return max(0, min(100, cents))

    if value < 10:
        cents = round((1 / value) * 100)
        return max(0, min(100, cents))

    if value <= 100:
        cents = round(value)
        return max(0, min(100, cents))

    return None


def calculate_investment_split(
    line1_cents: Optional[int],
    line2_cents: Optional[int],
    total_investment: float = 100.0
) -> Optional[dict]:
    """Calculate balanced $ split across two lines for near-equal payout."""
    if line1_cents is None or line2_cents is None:
        return None

    line1_price = line1_cents / 100
    line2_price = line2_cents / 100

    if line1_price <= 0 or line2_price <= 0:
        return None

    price_sum = line1_price + line2_price
    if price_sum <= 0:
        return None

    line1_investment = total_investment * (line1_price / price_sum)
    line2_investment = total_investment * (line2_price / price_sum)

    payout_if_line1_wins = line1_investment / line1_price
    payout_if_line2_wins = line2_investment / line2_price
    guaranteed_payout = min(payout_if_line1_wins, payout_if_line2_wins)
    guaranteed_profit = guaranteed_payout - total_investment

    return {
        'total_investment': total_investment,
        'line1_investment': line1_investment,
        'line2_investment': line2_investment,
        'guaranteed_payout': guaranteed_payout,
        'guaranteed_profit': guaranteed_profit
    }


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
    line1_match = re.search(r'Line\s*1:\s*(.+?)\s*@\s*([+-]?[\d.]+)\s*-\s*(\w+)', text, re.IGNORECASE)
    if line1_match:
        info['line1'] = line1_match.group(1).strip()
        info['line1_odds'] = line1_match.group(2).strip()
        info['line1_platform'] = line1_match.group(3).strip()
    
    # Extract Line 2
    line2_match = re.search(r'Line\s*2:\s*(.+?)\s*@\s*([+-]?[\d.]+)\s*-\s*(\w+)', text, re.IGNORECASE)
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
    
    timestamp = datetime.now(IST).strftime("%H:%M:%S IST")
    
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
    
    line1_cents = to_market_cents(info.get('line1_odds')) if info.get('line1_odds') else None
    line2_cents = to_market_cents(info.get('line2_odds')) if info.get('line2_odds') else None

    # Line 1
    if info.get('line1'):
        lines.append(f"**Line 1:** {info['line1']}")
        if info.get('line1_odds'):
            if line1_cents is not None:
                lines.append(f"  └ Price: **{line1_cents}¢**")
            else:
                lines.append(f"  └ Price: **{info['line1_odds']}**")
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
            if line2_cents is not None:
                lines.append(f"  └ Price: **{line2_cents}¢**")
            else:
                lines.append(f"  └ Price: **{info['line2_odds']}**")
        if info.get('line2_platform'):
            platform_line = f"  └ Platform: **{info['line2_platform']}**"
            if info.get('line2_link'):
                platform_line += f" [🔗 Link]({info['line2_link']})"
            lines.append(platform_line)

    investment_plan = calculate_investment_split(line1_cents, line2_cents, 100.0)
    if investment_plan:
        lines.append("")
        lines.append("**💵 Investment Plan ($100):**")
        lines.append(f"  └ Line 1: **${investment_plan['line1_investment']:.2f}**")
        lines.append(f"  └ Line 2: **${investment_plan['line2_investment']:.2f}**")
        lines.append(f"  └ Guaranteed Payout: **${investment_plan['guaranteed_payout']:.2f}**")
        lines.append(f"  └ Guaranteed Profit: **${investment_plan['guaranteed_profit']:.2f}**")
    
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    return "\n".join(lines)


def create_enhanced_message(raw_message: str) -> str:
    """Create enhanced version of original message."""
    
    timestamp = datetime.now(IST).strftime("%H:%M:%S IST")
    
    lines = [
        "🎯 **ARBITRAGE ALERT**",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "",
        raw_message.strip(),
        "",
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
