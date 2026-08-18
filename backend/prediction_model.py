 # Calculate the Exponential Moving Average (EMA) for a list of values.
def calculate_ema(data_list: list, days: int = 7) -> float:
    if not data_list:
        return 0.0
        
    alpha = 2 / (days + 1)
    
    # Initialize EMA with the oldest value
    ema = float(data_list[0])
    
    # Apply EMA formula for the rest of the days
    for i in data_list[1:]:
        value = float(i)
        ema = (value * alpha) + (ema * (1 - alpha))
        
    return round(ema, 1)