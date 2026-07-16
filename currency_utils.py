import urllib.request
import json
import time

SUPPORTED_CURRENCIES = ["INR", "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "SGD", "AED", "CNY"]

_FALLBACK_RATES = {
    "INR": 1.0,
    "USD": 0.012,
    "EUR": 0.011,
    "GBP": 0.0094,
    "JPY": 1.78,
    "AUD": 0.018,
    "CAD": 0.016,
    "SGD": 0.016,
    "AED": 0.044,
    "CNY": 0.086
}

_RATES_CACHE = None
_LAST_FETCH = 0

def get_rates():
    global _RATES_CACHE, _LAST_FETCH
    if _RATES_CACHE and time.time() - _LAST_FETCH < 3600:
        return _RATES_CACHE
        
    try:
        req = urllib.request.Request(
            "https://api.exchangerate-api.com/v4/latest/INR",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            rates = data.get("rates", {})
            _RATES_CACHE = rates
            _LAST_FETCH = time.time()
            return _RATES_CACHE
    except Exception:
        pass
        
    return _FALLBACK_RATES

def convert_currency(amount, from_curr, to_curr):
    if from_curr == to_curr:
        return float(amount)
        
    rates = get_rates()
    # Convert from_curr to INR, then INR to to_curr
    from_rate = rates.get(from_curr, _FALLBACK_RATES.get(from_curr, 1.0))
    to_rate = rates.get(to_curr, _FALLBACK_RATES.get(to_curr, 1.0))
    
    amount_inr = float(amount) / from_rate
    return amount_inr * to_rate

def get_currency_symbol(curr):
    symbols = {
        "INR": "₹", "USD": "$", "EUR": "€", "GBP": "£",
        "JPY": "¥", "AUD": "A$", "CAD": "C$", "SGD": "S$",
        "AED": "د.إ", "CNY": "¥"
    }
    return symbols.get(curr, f"{curr} ")

def format_amount(amount, curr):
    amount = float(amount)
    neg = amount < 0
    amount = abs(amount)
    sym = get_currency_symbol(curr)
    
    if curr == "JPY":
        return f"{'−' if neg else ''}{sym}{amount:,.0f}"
    return f"{'−' if neg else ''}{sym}{amount:,.2f}"
