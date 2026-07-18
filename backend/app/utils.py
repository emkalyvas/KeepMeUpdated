import re

def sanitize_prefix(name: str) -> str:
    """
    Sanitize a Data Source name to be used as a context variable prefix.
    'Athens Weather' -> 'athens_weather'
    """
    if not name:
        return "ds"
    s = re.sub(r'[^a-zA-Z0-9 ]', '', name).strip()
    if not s:
        return "ds"
    return "_".join(w.lower() for w in s.split())
