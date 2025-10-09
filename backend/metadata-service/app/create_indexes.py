from models import get_db, create_indexes

if __name__ == "__main__":
    db = get_db()
    create_indexes(db)
    print("Indexes created")
