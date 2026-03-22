import sqlite3
import time
import statistics
import os

primary_db = "/tmp/primary_mnt/my_db.sqlite"
replica_db = "/tmp/replica_mnt/my_db.sqlite"

conn_master = sqlite3.connect(primary_db, isolation_level=None)
cur_master = conn_master.cursor()

cur_master.execute("""
    CREATE TABLE IF NOT EXISTS repl_test (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_val TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

time.sleep(2)
conn_replica = sqlite3.connect(replica_db, isolation_level=None)
cur_replica = conn_replica.cursor()

lags = []
iterations = 100

print(f"Починаємо тест реплікації LiteFS на {iterations} ітерацій")

for i in range(iterations):
    val = f"test_data_{i}"
    t_start = time.perf_counter()
    
    cur_master.execute("INSERT INTO repl_test (test_val) VALUES (?)", (val,))

    found = False
    while not found:
        try:
            cur_replica.execute("SELECT 1 FROM repl_test WHERE test_val = ?", (val,))
            if cur_replica.fetchone():
                found = True
        except sqlite3.OperationalError:
            pass
        time.sleep(0.001) 
            
    t_end = time.perf_counter()
    
    lag_ms = (t_end - t_start) * 1000
    lags.append(lag_ms)

avg_lag = statistics.mean(lags)
p90_lag = statistics.quantiles(lags, n=100)[89]
max_lag = max(lags)

print("-" * 30)
print("РЕЗУЛЬТАТИ LITEFS (DISTRIBUTED SQLITE):")
print(f"Середня затримка (Avg): {avg_lag:.2f} мс")
print(f"90-й перцентиль (p90):  {p90_lag:.2f} мс")
print(f"Максимальна (Max):      {max_lag:.2f} мс")
print("-" * 30)

conn_master.close()
conn_replica.close()