from app.database import SessionLocal
from app.models import Role

def seed_roles():
    db = SessionLocal()
    try:
        # Check if roles already exist
        if db.query(Role).count() == 0:
            admin_role = Role(name="administrator")
            user_role = Role(name="user")
            db.add(admin_role)
            db.add(user_role)
            db.commit()
            print("✅ Successfully seeded initial roles: 'administrator' and 'user'")
        else:
            print("✅ Roles already exist, skipping seeding.")
    except Exception as e:
        print(f"❌ Error seeding roles: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_roles()