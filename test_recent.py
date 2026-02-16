from database import DebateDatabase

db = DebateDatabase()
recent = db.get_recent_debates(limit=20)
print(f"Total recent debates returned: {len(recent)}")
print("\nAll:")
for d in recent:
    print(f"  Debate #{d['id']}: STATUS={d.get('validation_status', 'None')} ACCURACY={d.get('validation_accuracy', 'None')}")
