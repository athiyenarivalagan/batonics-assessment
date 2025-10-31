# Convert the raw CSV into a structured Python dict 
from typing import Optional, Dict
from datetime import datetime

def parse_csv_line(header: Dict[str, int], line: str) -> Optional[dict]:
    """
    Parse the MBO CSV line into a normalized event dict.
    
    Columns expected:
    ts_event, rtype, publisher_id, instrument_id, action, side, price,\
    size, channel_id, order_id, flags, ts_in_delta, sequence, symbol
    """    
    # Clean the line (remove newline) and split into CSV fields.
    parts = line.rstrip("\n").split(",")
    # Skip incomplete rows
    if len(parts) < len(header):
        return None # or should I skip and proceed to the next line?
    
    # Helper function (state the purpose)
    def get(name:str, default=None):
        idx = header.get(name)
        if idx is None: 
            return default
        val = parts[idx].strip()
        return val if val != "" else default
    
    # Extract relevant fields
    # ts = float(get("ts_event", 0.0) or 0.0) # ts_event col isn't a numeric timestamp

    ts_str = get("ts_event", "")
    # try:
    #     # Convert ISO 8601 → UNIX timestamp (float seconds)
    #     ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp() if ts_str else 0.0
    # except Exception:
    #     ts = 0.0

    try:
        # Trim excess precision and timezone issues
        ts_str = ts_str.split("+")[0].strip()  # remove timezone
        ts_str = ts_str.split(".")[0] + "." + ts_str.split(".")[1][:6] if "." in ts_str else ts_str
        ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f").timestamp()
    except Exception:
        ts = 0.0

    action_code = (get("action", "") or "").upper()
    # side = (get("side", "N") or "N").upper()
    side = str(get("side", "N") or "N").upper() if not isinstance(get("side", "N"), float) else "N"
    price = float(get("price", 0.0) or 0.0)
    size = float(get("size", 0.0) or 0.0)
    order_id = int(get("order_id", 0) or 0)
    symbol = get("symbol", "UNKNOWN")

    # Map one-letter codes → normalized actions
    ACTION_MAP = {
        "A": "ADD",
        "M": "MOD",
        "C": "CXL",
        "T": "TRD",
        "F": "FILL",
        "R": "CLR",
        "N": "CLR"
    }
    action = ACTION_MAP.get(action_code) # get the value given the key
    if not action:
        return None  # skip unknown codes

    return {
        "ts": ts,
        "action": action,
        "order_id": order_id,
        "side": side,
        "price": price,
        "size": size,
        "instrument": symbol,
    }