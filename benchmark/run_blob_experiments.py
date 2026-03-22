import sqlite3
import os
import time
import random
import shutil
import csv
from pathlib import Path

TOTAL_DATA_MB = 100
BLOB_SIZES_KB = [10, 20, 50, 100, 200, 500, 1000]
PAGE_SIZES_BYTES = [1024, 2048, 4096, 8192, 16384, 32768, 65536]
CACHE_SIZES_MB = [2, 4, 6, 8]

WORK_DIR = Path("blob_test_data")
FS_DIR = WORK_DIR / "fs_blobs"
DB_PATH = WORK_DIR / "blobs.db"

def setup_environment():
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir()
    FS_DIR.mkdir()

def run_experiment():
    setup_environment()
    results = []

    for size_kb in BLOB_SIZES_KB:
        size_bytes = size_kb * 1024
        files_count = (TOTAL_DATA_MB * 1024 * 1024) // size_bytes
        
        print(f"\n[{size_kb} KB] Генерація {files_count} об'єктів (загалом ~100 MB)...")
        dummy_data = os.urandom(size_bytes)
        
        # ==========================================
        # 1. ТЕСТ ФАЙЛОВОЇ СИСТЕМИ
        # ==========================================
        fs_paths = []
        for i in range(files_count):
            file_path = FS_DIR / f"file_{size_kb}_{i}.bin"
            with open(file_path, "wb") as f:
                f.write(dummy_data)
            fs_paths.append(file_path)
            
        print(f"  -> Читання File System...")
        random.shuffle(fs_paths)
        
        start_time = time.perf_counter()
        for file_path in fs_paths:
            with open(file_path, "rb") as f:
                _ = f.read()
        fs_time = time.perf_counter() - start_time
        
        results.append({
            "blob_size_kb": size_kb,
            "storage_type": "File System",
            "page_size_bytes": "N/A",
            "cache_mb": "N/A",
            "total_time_sec": round(fs_time, 4)
        })

        # ==========================================
        # 2. ТЕСТ SQLITE
        # ==========================================
        for page_size in PAGE_SIZES_BYTES:
            if DB_PATH.exists():
                DB_PATH.unlink()
            
            conn = sqlite3.connect(DB_PATH)
            conn.execute(f"PRAGMA page_size = {page_size};")
            conn.execute("CREATE TABLE images (id INTEGER PRIMARY KEY, data BLOB);")
            
            with conn:
                conn.executemany("INSERT INTO images (data) VALUES (?)", [(dummy_data,) for _ in range(files_count)])
            
            db_ids = [row[0] for row in conn.execute("SELECT id FROM images").fetchall()]
            
            for cache_mb in CACHE_SIZES_MB:
                cache_bytes = cache_mb * 1024 * 1024
                cache_pages = cache_bytes // page_size
                
                conn.execute(f"PRAGMA cache_size = {cache_pages};")
                
                print(f"  -> Читання SQLite (Page: {page_size} B | Cache: {cache_mb} MB | Pages: {cache_pages})...")
                random.shuffle(db_ids)
                
                start_time = time.perf_counter()
                for row_id in db_ids:
                    cur = conn.execute("SELECT data FROM images WHERE id = ?", (row_id,))
                    _ = cur.fetchone()[0]
                db_time = time.perf_counter() - start_time
                
                results.append({
                    "blob_size_kb": size_kb,
                    "storage_type": "SQLite",
                    "page_size_bytes": page_size,
                    "cache_mb": cache_mb,
                    "total_time_sec": round(db_time, 4)
                })
            conn.close()

        for p in fs_paths:
            p.unlink()
            
    csv_path = "blob_official_results.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    shutil.rmtree(WORK_DIR)

if __name__ == "__main__":
    run_experiment()