# scoring.py

def calculate_daily_score(data: dict) -> int:
    """
    Calculate a simple Sovereignty Score based on daily habits.
    Expects keys:
      home_cooked_meals: int
      junk_food: bool
      exercise_minutes: int
      strength_training: bool
      no_spending: bool
      invested_bitcoin: bool
      meditation: bool
      gratitude: bool
    """

    score = 0

    # 1) Home-cooked meals (max 3):  ∴ 20 pts total → ~6.66 pts/meal
    meals = min(data.get("home_cooked_meals", 0), 3)
    score += meals * (20/3)

    # 2) Junk food penalty: 0 pts if yes, 10 if no
    if not data.get("junk_food", False):
        score += 10

    # 3) Aerobic exercise: max 15 pts (30 min = full points)
    mins = data.get("exercise_minutes", 0)
    score += min(mins, 30) * (15/30)

    # 4) Strength training: +15 pts if yes
    if data.get("strength_training", False):
        score += 15

    # 5) No discretionary spending: +10 pts
    if data.get("no_spending", False):
        score += 10

    # 6) Invest in Bitcoin: +10 pts
    if data.get("invested_bitcoin", False):
        score += 10

    # 7) Meditation: +10 pts
    if data.get("meditation", False):
        score += 10

    # 8) Gratitude practice: +10 pts
    if data.get("gratitude", False):
        score += 10

    return int(round(min(score, 100)))


