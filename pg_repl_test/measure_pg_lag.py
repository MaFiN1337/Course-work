import psycopg2
import time
import statistics

conn_master = psycopg2.connect(
    dbname="bottleneck_db", user="admin", password="supersecret", host="localhost", port=5432
)
conn_master.autocommit = True
cur_master = conn_master.cursor()

conn_replica = psycopg2.connect(
    dbname="bottleneck_db", user="admin", password="supersecret", host="localhost", port=5433
)
conn_replica.autocommit = True
cur_replica = conn_replica.cursor()

cur_master.execute("""
    CREATE TABLE IF NOT EXISTS repl_test (
        id SERIAL PRIMARY KEY,
        test_val VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
time.sleep(1)

lags = []
iterations = 100

for i in range(iterations):
    val = f"test_data_{i}"
    
    t_start = time.perf_counter()
    
    cur_master.execute("INSERT INTO repl_test (test_val) VALUES (%s)", (val,))
    
    found = False
    while not found:
        cur_replica.execute("SELECT 1 FROM repl_test WHERE test_val = %s", (val,))
        if cur_replica.fetchone():
            found = True
        else:
            time.sleep(0.001) 
            
    t_end = time.perf_counter()

    lag_ms = (t_end - t_start) * 1000
    lags.append(lag_ms)

avg_lag = statistics.mean(lags)
p90_lag = statistics.quantiles(lags, n=100)[89]
max_lag = max(lags)

print("-" * 30)
print("РЕЗУЛЬТАТИ POSTGRESQL СТРИМІНГ РЕПЛІКАЦІЇ:")
print(f"Середня затримка (Avg): {avg_lag:.2f} мс")
print(f"90-й перцентиль (p90):  {p90_lag:.2f} мс")
print(f"Максимальна (Max):      {max_lag:.2f} мс")
print("-" * 30)

cur_master.close()
conn_master.close()
cur_replica.close()
conn_replica.close()