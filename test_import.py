import sys
print("Python version:", sys.version)
print("\nTrying to import scoring module...")
try:
    from tracker.scoring import calculate_daily_score
    print("Successfully imported calculate_daily_score")
except Exception as e:
    print("Error:", str(e))
    print("\nFull error details:")
    import traceback
    traceback.print_exc() 