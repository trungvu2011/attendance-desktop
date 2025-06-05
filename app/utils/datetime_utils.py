"""
Utility functions for handling datetime with Vietnamese format and timezone
"""

import datetime
import pytz
import locale
import sys

# Thiết lập timezone Việt Nam
VIETNAM_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

def set_vietnamese_locale():
    """Set Vietnamese locale for date formatting"""
    try:
        if sys.platform.startswith('win'):
            # Windows
            locale.setlocale(locale.LC_TIME, 'vi_VN.UTF-8')
        else:
            # Linux/Mac
            locale.setlocale(locale.LC_TIME, 'vi_VN.UTF-8')
    except locale.Error:
        try:
            # Fallback for Windows
            if sys.platform.startswith('win'):
                locale.setlocale(locale.LC_TIME, 'Vietnamese_Vietnam.1258')
            else:
                locale.setlocale(locale.LC_TIME, 'vi_VN')
        except locale.Error:
            # If Vietnamese locale is not available, keep default
            pass

def get_current_time():
    """Get current time in Vietnam timezone"""
    return datetime.datetime.now(VIETNAM_TZ)

def format_datetime_vietnamese(dt=None, format_type='full'):
    """
    Format datetime in Vietnamese format
    
    Args:
        dt: datetime object, if None uses current time
        format_type: 'full', 'date', 'time', 'short', 'iso'
    
    Returns:
        Formatted datetime string
    """
    if dt is None:
        dt = get_current_time()
    elif dt.tzinfo is None:
        # If datetime is naive, assume it's UTC and convert to Vietnam time
        dt = pytz.UTC.localize(dt).astimezone(VIETNAM_TZ)
    elif dt.tzinfo != VIETNAM_TZ:
        # Convert to Vietnam timezone
        dt = dt.astimezone(VIETNAM_TZ)
    
    formats = {
        'full': '%d/%m/%Y %H:%M:%S',          # 25/12/2023 15:30:45
        'date': '%d/%m/%Y',                   # 25/12/2023
        'time': '%H:%M:%S',                   # 15:30:45
        'short': '%d/%m/%Y %H:%M',           # 25/12/2023 15:30
        'iso': '%Y-%m-%dT%H:%M:%S',          # 2023-12-25T15:30:45 (for API)
        'iso_with_tz': '%Y-%m-%dT%H:%M:%S%z', # 2023-12-25T15:30:45+0700
        'filename': '%Y%m%d-%H%M%S',         # 20231225-153045 (for filenames)
        'display': '%d tháng %m, %Y %H:%M',  # 25 tháng 12, 2023 15:30
    }
    
    return dt.strftime(formats.get(format_type, formats['full']))

def format_date_vietnamese(dt=None):
    """Format date in Vietnamese format: dd/mm/yyyy"""
    return format_datetime_vietnamese(dt, 'date')

def format_time_vietnamese(dt=None):
    """Format time in Vietnamese format: HH:MM:SS"""
    return format_datetime_vietnamese(dt, 'time')

def format_datetime_short_vietnamese(dt=None):
    """Format datetime in short Vietnamese format: dd/mm/yyyy HH:MM"""
    return format_datetime_vietnamese(dt, 'short')

def format_datetime_for_api(dt=None):
    """Format datetime for API (ISO format with Vietnam timezone)"""
    if dt is None:
        dt = get_current_time()
    elif dt.tzinfo is None:
        dt = VIETNAM_TZ.localize(dt)
    elif dt.tzinfo != VIETNAM_TZ:
        dt = dt.astimezone(VIETNAM_TZ)
    
    return dt.isoformat()

def format_datetime_for_filename(dt=None):
    """Format datetime for filename: YYYYMMDD-HHMMSS"""
    return format_datetime_vietnamese(dt, 'filename')

def format_datetime_display(dt=None):
    """Format datetime for display: dd tháng mm, yyyy HH:MM"""
    return format_datetime_vietnamese(dt, 'display')

def parse_iso_datetime(iso_string):
    """
    Parse ISO format datetime string and convert to Vietnam timezone
    
    Args:
        iso_string: ISO format datetime string (e.g., "2023-12-25T15:30:45")
    
    Returns:
        datetime object in Vietnam timezone
    """
    try:
        # Parse the ISO string
        if 'T' in iso_string:
            # Handle ISO format with T separator
            if '+' in iso_string or iso_string.endswith('Z'):
                # Has timezone info
                dt = datetime.datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
            else:
                # No timezone info, assume UTC
                dt = datetime.datetime.fromisoformat(iso_string)
                dt = pytz.UTC.localize(dt)
        else:
            # Handle other datetime formats
            dt = datetime.datetime.strptime(iso_string, '%Y-%m-%d %H:%M:%S')
            dt = pytz.UTC.localize(dt)
        
        # Convert to Vietnam timezone
        return dt.astimezone(VIETNAM_TZ)
    except (ValueError, TypeError) as e:
        # If parsing fails, return current time
        return get_current_time()

def format_time_from_iso(iso_string):
    """
    Parse ISO datetime string and return formatted time
    
    Args:
        iso_string: ISO format datetime string
    
    Returns:
        Time string in HH:MM:SS format
    """
    dt = parse_iso_datetime(iso_string)
    return format_time_vietnamese(dt)

def get_today_date_vietnamese():
    """Get today's date in Vietnamese format"""
    return format_date_vietnamese()

def get_current_datetime_vietnamese():
    """Get current datetime in Vietnamese format"""
    return format_datetime_vietnamese()

def format_timestamp_for_display(timestamp_str):
    """
    Format any timestamp string to Vietnamese display format
    Handles various input formats: ISO, technical format, etc.
    
    Args:
        timestamp_str: Timestamp string in various formats
    
    Returns:
        Formatted string in Vietnamese display format: dd/mm/yyyy HH:MM:SS
    """
    if not timestamp_str:
        return ""
    
    try:
        # Try parsing as ISO format first
        if 'T' in str(timestamp_str):
            dt = parse_iso_datetime(timestamp_str)
        else:
            # Try parsing common datetime formats
            formats_to_try = [
                '%Y-%m-%d %H:%M:%S.%f',  # 2025-06-05 06:02:15.641840
                '%Y-%m-%d %H:%M:%S',     # 2025-06-05 06:02:15
                '%d/%m/%Y %H:%M:%S',     # 05/06/2025 06:02:15
                '%d/%m/%Y',              # 05/06/2025
            ]
            
            dt = None
            for fmt in formats_to_try:
                try:
                    dt = datetime.datetime.strptime(str(timestamp_str), fmt)
                    # Localize to Vietnam timezone if naive
                    if dt.tzinfo is None:
                        dt = VIETNAM_TZ.localize(dt)
                    break
                except ValueError:
                    continue
            
            if dt is None:
                # If all parsing fails, return the original string
                return str(timestamp_str)
        
        # Format to Vietnamese display format
        return format_datetime_vietnamese(dt, 'full')
        
    except Exception as e:
        # If anything fails, return original string
        return str(timestamp_str)

# Initialize Vietnamese locale on import
set_vietnamese_locale()
