import os
import sys
import time
import csv
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.parking.settings')

import django
django.setup()

from django.db import connection, transaction
from django.conf import settings

QUERIES = {
    "1_COUNT_ALL": """
        SELECT COUNT(*) FROM api_booking WHERE status = 'confirmed';
    """,
    "2_JOIN_4_TABLES": """
        SELECT l.city, COUNT(b.id)
        FROM api_booking b
        JOIN api_spot s ON b.spot_id = s.id
        JOIN api_parkinglot l ON s.lot_id = l.id
        JOIN auth_user u ON b.user_id = u.id
        WHERE b.status = 'confirmed'
        GROUP BY l.city;
    """,
    "3_SUBQUERY": """
        SELECT COUNT(name) FROM api_parkinglot
        WHERE id IN (
            SELECT lot_id FROM api_spot
            WHERE id IN (
                SELECT spot_id FROM api_booking
                WHERE status = 'cancelled' AND user_id IN (
                    SELECT id FROM auth_user WHERE email LIKE '%@%'
                )
            )
        );
    """,
    "4_JOIN_INSTEAD_OF_SUBQUERY": """
        SELECT COUNT(DISTINCT l.name)
        FROM api_parkinglot l
        JOIN api_spot s ON l.id = s.lot_id
        JOIN api_booking b ON s.id = b.spot_id
        JOIN auth_user u ON b.user_id = u.id
        WHERE b.status = 'cancelled' AND u.email LIKE '%@%';
    """,
    "5_UNION": """
        SELECT * FROM (
            SELECT name, base_price_per_hour 
            FROM api_parkinglot 
            ORDER BY base_price_per_hour DESC 
            LIMIT 5
        ) AS top_expensive
        UNION ALL
        SELECT * FROM (
            SELECT name, base_price_per_hour 
            FROM api_parkinglot 
            ORDER BY base_price_per_hour ASC 
            LIMIT 5
        ) AS top_cheap;
    """,
    "6_MASS_DELETE": """
        DELETE FROM api_booking WHERE status = 'cancelled';
    """
}


def format_size_label(size):
    if size >= 1_000_000:
        val = size / 1_000_000
        return f"{val:g}m"
    else:
        val = size // 1000
        return f"{val}k"

def run_benchmarks(size, iterations=30):
    db_vendor = connection.vendor
    db_label = db_vendor
    if db_vendor == 'sqlite':
        options = settings.DATABASES['default'].get('OPTIONS', {})
        if 'init_command' in options and 'WAL' in options['init_command']:
            db_label = 'sqlite_modified'
        else:
            db_label = 'sqlite_standard'

    size_label = format_size_label(size)
    
    benchmark_dir = BASE_DIR / "benchmark"
    benchmark_dir.mkdir(exist_ok=True)
    
    results_file = benchmark_dir / f"results_{db_label}_{size_label}.csv"
    results = []

    print(f"Починаємо тестування БД: {db_label.upper()} | Розмір: {size} | Ітерацій: {iterations}")
    print("-" * 60)

    with connection.cursor() as cursor:
        for test_name, sql in QUERIES.items():
            print(f"Виконується {test_name}...")
            times = []
            
            if "DELETE" not in sql:
                cursor.execute(sql)
                cursor.fetchall()
            
            for _ in range(iterations):
                start_time = time.perf_counter()
                
                if "DELETE" in sql:
                    try:
                        with transaction.atomic():
                            cursor.execute(sql)
                            transaction.set_rollback(True)
                    except Exception as e:
                        print(f"Помилка в DELETE: {e}")
                else:
                    cursor.execute(sql)
                    cursor.fetchall()
                
                end_time = time.perf_counter()
                times.append((end_time - start_time) * 1000)
            
            times.sort()
            
            avg_time = sum(times) / len(times)
            min_time = times[0]
            max_time = times[-1]
            p50 = times[int(len(times) * 0.5)]
            p90 = times[int(len(times) * 0.9)]
            p95 = times[int(len(times) * 0.95)]
            p99 = times[int(len(times) * 0.99)]
            
            print(f"  -> Сер: {avg_time:.2f} мс | P50: {p50:.2f} | P99: {p99:.2f}")
            
            results.append({
                "test_name": test_name,
                "db_engine": db_label,
                "db_size": size,
                "iterations": iterations,
                "avg_time_ms": round(avg_time, 2),
                "p50_time_ms": round(p50, 2),
                "p90_time_ms": round(p90, 2),
                "p95_time_ms": round(p95, 2),
                "p99_time_ms": round(p99, 2),
                "min_time_ms": round(min_time, 2),
                "max_time_ms": round(max_time, 2),
            })

    keys = results[0].keys()
    with open(results_file, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)

    print("-" * 60)
    print(f"Тестування завершено! Результати збережено у файл: {results_file.name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Скрипт для бенчмаркінгу бази даних.")
    parser.add_argument('--size', type=int, required=True, help='Кількість записів у базі')
    parser.add_argument('--iterations', type=int, default=30, help='Кількість ітерацій для кожного запиту')
    
    args = parser.parse_args()
    
    run_benchmarks(size=args.size, iterations=args.iterations)