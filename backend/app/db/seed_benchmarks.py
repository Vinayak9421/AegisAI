import app.db.models  # noqa: F401
from app.db.session import SessionLocal, init_db
from app.modules.auth.service import AuthService
from app.modules.benchmarks.seeder import (
    find_datasets_dir,
    seed_all_benchmarks,
    seed_finred_dataset,
    seed_advbench_dataset,
    seed_harmbench_dataset,
    seed_benign_dataset,
)

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    try:
        AuthService(db).seed_default_users()
        results = seed_all_benchmarks(db)
        print(f"Dataset seeding completed successfully: {results}")
    finally:
        db.close()
