def convert_to_seconds(interval_value: float, unit: str) -> float:
    units_in_seconds = {
        'seconds': 1, # 1 second = 1 second
        'minutes': 60, # 1 minute = 60 seconds
        'hours': 3600,  # 1 hour = 3600 seconds
        'days': 86400 # 1 day = 86400 seconds
    }
    try:
        return interval_value * units_in_seconds[unit.lower()]
    except KeyError:
        raise ValueError("Invalid unit. Choose from 'seconds', 'minutes', 'hours', 'days'.")
