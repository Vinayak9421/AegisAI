"""Dataset seeder utility to ingest FinRed, HarmBench, AdvBench, and calibration datasets into PostgreSQL."""

from app.modules.benchmarks.seeder import (
    find_datasets_dir,
    seed_all_benchmarks,
    seed_finred_dataset,
    seed_advbench_dataset,
    seed_harmbench_dataset,
    seed_benign_dataset,
)
from app.db.session import SessionLocal

if __name__ == "__main__":
    db = SessionLocal()
    try:
        results = seed_all_benchmarks(db)
        print(f"Dataset seeding completed successfully: {results}")
    finally:
        db.close()
