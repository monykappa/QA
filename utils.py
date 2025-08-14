from datetime import datetime
import pytz

def format_timestamp(timestamp: datetime | None) -> str | None:
    if timestamp is None:
        return None
    phnom_penh_tz = pytz.timezone('Asia/Phnom_Penh')
    if timestamp.tzinfo is None:
        # Assume naive timestamps are in Phnom Penh time (for legacy data)
        timestamp = phnom_penh_tz.localize(timestamp)
    else:
        # Convert to Phnom Penh time
        timestamp = timestamp.astimezone(phnom_penh_tz)
    # Format as DD-MM-YY h:mmAM/PM
    return timestamp.strftime('%d-%m-%y %I:%M%p')