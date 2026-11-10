from math import isfinite, prod


# Provisional weights based on our current baseline.
# These must eventually be calibrated using historical data.
WEIGHTS = {
    "news": 0.40,
    "weather": 0.40,
    "history": 0.20
}


def calculate_risk(news, weather, history=None):
    """
    Calculate overall route risk using news, weather
    and historical risk signals.

    Each available signal must be a dictionary:
    {"value": number}

    Risk values must be between 1 and 100.
    """

    signals = (
        ("News risk", news, "news"),
        ("Weather risk", weather, "weather"),
        ("Historical risk", history, "history")
    )

    weighted_score = 0
    total_weight = 0
    reasons = []
    available_count = 0

    for name, signal, key in signals:

        # Skip missing signals
        if signal is None:
            continue

        # Check dictionary format
        if not isinstance(signal, dict):
            raise ValueError(name + " must be a dictionary")

        # Extract numerical risk value
        value = signal.get("value")

        # Skip signals without a value
        if value is None:
            continue

        # Validate risk value
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not isfinite(value)
            or not 1 <= value <= 100
        ):
            raise ValueError(
                name + " must be a number between 1 and 100"
            )

        weight = WEIGHTS[key]

        # Calculate weighted contribution
        points = value * weight

        weighted_score += points
        total_weight += weight
        available_count += 1

        reasons.append({
            "label": name,
            "points": round(points, 2)
        })

    # Check whether any valid signal was available
    if total_weight == 0:
        raise ValueError("No valid risk signals available")

    # Normalize weights if some signals are missing
    score = round(weighted_score / total_weight)

    # Provisional confidence based on signal availability
    if available_count == 3:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "score": score,
        "reasons": reasons,
        "confidence": confidence
    }


def aggregate_segment_risks(segment_scores):
    """
    Combine risk scores from multiple route segments.

    This uses the route aggregation formula from our project
    presentation, assuming independent segment risks.
    """

    if not segment_scores:
        raise ValueError("No segment risk scores provided")

    for score in segment_scores:

        if (
            isinstance(score, bool)
            or not isinstance(score, (int, float))
            or not isfinite(score)
            or not 1 <= score <= 100
        ):
            raise ValueError(
                "Each segment risk must be between 1 and 100"
            )

    remaining_safety = prod(
        1 - score / 100 for score in segment_scores
    )

    overall_risk = (1 - remaining_safety) * 100

    return round(overall_risk)


def score_route(route_id):
    """
    Fetch news and weather signals and calculate route risk.

    Historical risk is currently unavailable.
    """

    from fetch_weather import get_weather_signal
    from fetch_news import get_news_signal

    weather = get_weather_signal(route_id)
    news = get_news_signal(route_id)

    result = calculate_risk(
        news=news,
        weather=weather,
        history=None
    )

    result["route_id"] = route_id

    return result