"""
Datetime related functions isolated for reusability.
"""
from datetime import datetime

import pytz


def utc_now():
    """Get current **AWARE** UTC datetime."""
    return pytz.timezone('UTC').localize(datetime.utcnow())
