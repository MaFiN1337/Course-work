import subprocess

SIZES = [
    100_000, 200_000, 300_000, 500_000, 800_000, 
    1_000_000, 1_500_000, 2_000_000, 2_500_000, 
    3_000_000, 4_000_000, 5_000_000
]

def run_command(command):
    print(f"\n>>> ВИКОНУЄТЬСЯ: {command}")
    subprocess.run(command, shell=True, check=True)

for size in SIZES:
    print(f"\n{'='*50}")
    print(f"ПОЧИНАЄМО ЕКСПЕРИМЕНТ ДЛЯ РОЗМІРУ: {size}")
    print(f"{'='*50}")
    
    run_command("python manage.py migrate")

    run_command("python manage.py flush --no-input")
    
    run_command(f"python manage.py generate_test_data --size {size}")
    
    run_command(f"python benchmark/run_raw_sql_tests.py --size {size}")