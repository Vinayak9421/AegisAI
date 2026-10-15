import collections
import app.db.models  # noqa: F401
from app.db.session import SessionLocal, init_db
from app.modules.auth.service import AuthService
from app.modules.benchmarks.models import BenchmarkSource, TestCase
from app.modules.benchmarks.seeder import seed_all_benchmarks

def run_database_setup():
    print("================================================================")
    print(" Aegis AI - Database Establishment & Benchmark Seeder")
    print("================================================================")
    print("[1/4] Initializing database tables...")
    init_db()
    
    db = SessionLocal()
    try:
        print("[2/4] Seeding default demonstration users (admin@aegis.ai, user@aegis.ai)...")
        auth_service = AuthService(db)
        auth_service.seed_default_users()
        
        print("[3/4] Ingesting financial & adversarial benchmarks from Datasets/...")
        results = seed_all_benchmarks(db)
        print(f"      - FinRed cases ingested:     {results.get('finred_cases', 0)}")
        print(f"      - AdvBench cases ingested:   {results.get('advbench_cases', 0)}")
        print(f"      - HarmBench cases ingested:  {results.get('harmbench_cases', 0)}")
        print(f"      - Benign baseline ingested:  {results.get('benign_cases', 0)}")
        print(f"      - MTSA session cases:        {results.get('mtsa_cases', 0)}")
        
        print("[4/4] Verifying database catalog...")
        total_sources = db.query(BenchmarkSource).count()
        total_cases = db.query(TestCase).count()
        cat_counts = collections.Counter([tc.category for tc in db.query(TestCase).all()])
        
        print("----------------------------------------------------------------")
        print(f"Database Status: READY")
        print(f"Total Benchmark Sources: {total_sources}")
        print(f"Total Active Test Cases: {total_cases}")
        print("Test Cases by Category:")
        for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
            print(f"  - {cat:<30}: {cnt} vectors")
        print("----------------------------------------------------------------")
        print("Seeding completed successfully. Ready for evaluation scans.")
    finally:
        db.close()

if __name__ == "__main__":
    run_database_setup()
