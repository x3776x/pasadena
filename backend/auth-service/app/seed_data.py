from app.database import SessionLocal
from app.models import Role

def seed_roles():
    db = SessionLocal()
    try:
        # Check if roles already exist
        existing_roles = db.query(Role).filter(Role.name.in_(["user", "administrator"])).all()
        existing_role_names = [role.name for role in existing_roles]

        roles_to_create = []
        if "administrator" not in existing_role_names:
            roles_to_create.append(Role(name="administrator"))
            
        if "user" not in existing_role_names:
            roles_to_create.append(Role(name="user"))

        if roles_to_create:
            db.add_all(roles_to_create)
            db.commit()
            print(f"✅ Seeded {len(roles_to_create)} new roles")
        else:
            print("✅ All roles already exist, skipping seeding.")
            
    except Exception as e:
        print(f"❌ Error seeding roles: {e}")
        db.rollback()
    finally:
        db.close()
        
if __name__ == "__main__":
    seed_roles()