#!/usr/bin/env python3
"""
Date Utilities for Stock Analysis Articles
Ensures all articles use current date automatically
"""

from datetime import datetime
import calendar

def get_current_analysis_date() -> str:
    """Get current date formatted for analysis (e.g., 'September 7, 2025')"""
    return datetime.now().strftime("%B %d, %Y")

def get_current_date_iso() -> str:
    """Get current date in ISO format (e.g., '2025-09-07')"""
    return datetime.now().strftime("%Y-%m-%d")

def get_next_review_date(months_ahead: int = 6) -> str:
    """Get next review date (default 6 months from today)"""
    try:
        from dateutil.relativedelta import relativedelta
        next_date = datetime.now() + relativedelta(months=months_ahead)
        return next_date.strftime("%B %d, %Y")
    except ImportError:
        # Fallback if dateutil not available
        today = datetime.now()
        year = today.year
        month = today.month + months_ahead
        
        # Handle year rollover
        while month > 12:
            month -= 12
            year += 1
        
        # Handle month with fewer days
        day = min(today.day, calendar.monthrange(year, month)[1])
        
        next_date = datetime(year, month, day)
        return next_date.strftime("%B %d, %Y")

def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

def format_date_for_article(date_obj: datetime = None) -> str:
    """Format date for article display"""
    if date_obj is None:
        date_obj = datetime.now()
    return date_obj.strftime("%B %d, %Y")

# Test the functions
if __name__ == "__main__":
    print("Date Utilities Test:")
    print("=" * 30)
    print(f"Current Analysis Date: {get_current_analysis_date()}")
    print(f"ISO Date: {get_current_date_iso()}")
    print(f"Next Review Date (6 months): {get_next_review_date()}")
    print(f"Next Review Date (12 months): {get_next_review_date(12)}")
    print(f"Timestamp: {get_timestamp()}")
