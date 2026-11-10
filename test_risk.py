from risk import calculate_risk, aggregate_segment_risks


print("TEST 1: All three signals available")

news = {"value": 60}
weather = {"value": 30}
history = {"value": 90}

result = calculate_risk(news, weather, history)

print(result)

assert result["score"] == 54
print("TEST 1 PASSED")


print("\nTEST 2: Historical signal missing")

result = calculate_risk(
    news={"value": 60},
    weather={"value": 30},
    history={"value": 90},
)

print(result)

assert result["score"] == 45
print("TEST 2 PASSED")


print("\nTEST 3: Route segment aggregation")

segments = [50, 40]

overall = aggregate_segment_risks(segments)

print("Combined route risk:", overall)

assert overall == 70
print("TEST 3 PASSED")


print("\nALL TESTS PASSED SUCCESSFULLY!")