import argparse
import json
from app.db import SessionLocal
from app.models import User


def serialize(u: User):
    return {
        "id": u.id,
        "name": u.name,
        "age": u.age,
        "location": u.location,
        "gender": u.gender,
        "personality": u.personality,
        "looking_for": u.looking_for,
        "days_available": u.days_available,
        "age_range": u.age_range,
        "professions": u.professions,
        "favorite_foods": u.favorite_foods,
        "pets": u.pets,
    }


def list_profiles(limit: int = 10, age_min: int = None, age_max: int = None, profession: str = None):
    with SessionLocal() as session:
        q = session.query(User)
        if age_min is not None:
            q = q.filter(User.age >= age_min)
        if age_max is not None:
            q = q.filter(User.age <= age_max)
        if profession:
            q = q.filter(User.professions.ilike(f"%{profession}%"))
        q = q.order_by(User.name).limit(limit)
        return [serialize(u) for u in q]


def main():
    p = argparse.ArgumentParser(description="List demo user profiles")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--age-min", type=int)
    p.add_argument("--age-max", type=int)
    p.add_argument("--profession", type=str)
    p.add_argument("--json", dest="as_json", action="store_true")
    args = p.parse_args()

    rows = list_profiles(limit=args.limit, age_min=args.age_min, age_max=args.age_max, profession=args.profession)
    if args.as_json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    else:
        for r in rows:
            print(f"{r['id']} — {r['name']} ({r.get('age')}) — {r.get('location')} — {r.get('professions')}")


if __name__ == "__main__":
    main()
