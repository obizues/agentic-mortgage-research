from database import DebateDatabase

db = DebateDatabase()
trend = db.get_accuracy_trend()
print(f"Default DB path: {db.db_path}")
print(f"Trend data points: {len(trend)}")
if trend:
    print("\nFirst 5:")
    for item in trend[:5]:
        print(f"  Debate {item['debate_num']}: {item['status']} - {item['accuracy']:.1f}%")
