def classify_health(score):
    if score >= 80:
        return "Healthy"
    elif score >= 50:
        return "Warning"
    return "Critical"