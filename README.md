# Smart Parking API & СУБД Бенчмаркінг (Курсова робота)

Цей репозиторій містить вихідний код REST API веб-застосунку «Smart Parking», а також набір інструментів та скриптів для емпіричного дослідження, бенчмаркінгу та стрес-тестування СУБД (SQLite та PostgreSQL). 

Робота виконана в рамках курсової роботи на тему: **«Налаштування СУБД SQLite для використання у високонавантажених веб-застосунках. Порівняльний аналіз ефективності SQLite і PostgreSQL»**.

## Технологічний стек
* **Backend:** Python 3.10+, Django, Django REST Framework
* **Бази даних:** SQLite (Standard & Modified WAL), PostgreSQL
* **Стрес-тестування:** Locust, k6
* **Реплікація SQLite:** LiteFS
* **Сервер:** Waitress

---

## 1. Встановлення та налаштування

1. **Клонування репозиторію:**
   ```bash
   git clone https://github.com/MaFiN1337/Course-work.git
   cd Course-work

2. **Створення та активація віртуального середовища:**
   * **Windows:**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   * **Linux/macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Встановлення залежностей:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Застосування міграцій бази даних:**
   ```bash
   python manage.py migrate
   ```

5. **Генерація тестових даних (Синтетичний бенчмаркінг):**
   Для тестування необхідно згенерувати масив даних (наприклад, парковки, місця, бронювання).
   ```bash
   python manage.py generate_test_data --size
   ```

---

## 2. Стрес-тестування API (Locust та k6)

Перед запуском тестів переконайтеся, що ви згенерували JWT токен з тривалим часом життя (налаштовано в `src/parking/settings.py`) та вставили його у файли `locustfile.py` та `k6_script.js`. Swagger є зручним інструментом для цього (/api/docs)

### Запуск сервера
Для тестів використовується WSGI-сервер `waitress` для імітації реального production-навантаження:
```bash
waitress-serve --port=8000 --threads=32 --connection-limit=1000 src.parking.wsgi:application
```

### Варіант А: Тестування за допомогою Locust
Locust генерує навантаження та надає зручний веб-інтерфейс (або працює в консолі).
```bash
# Запуск у консольному (headless) режимі на 300 користувачів (1.5 хвилини)
locust -f locustfile.py --headless -u 300 -r 10 -t 1m30s --host http://localhost:8000
```

### Варіант Б: Тестування за допомогою k6
k6 написаний на Go та ідеально підходить для вимірювання максимальної пропускної здатності (RPS).
*Встановіть k6 з [офіційного сайту](https://k6.io/docs/get-started/installation/)*.
```bash
k6 run k6_script.js
```

---

## 3. Тестування реплікації SQLite (LiteFS) у GitHub Codespaces

Скрипти `measure_litefs.py`, `primary.yml` та `replica.yml` призначені для тестування розподіленого кластера SQLite за допомогою **LiteFS**. Оскільки LiteFS потребує механізму `FUSE` (Filesystem in Userspace), найзручніше запускати цей тест у Linux-середовищі, наприклад, у **GitHub Codespaces**.

**Крок 1.** Відкрийте репозиторій у GitHub Codespaces.

**Крок 2.** Встановіть необхідні системні пакети:
```bash
sudo apt-get update && sudo apt-get install -y fuse
```

**Крок 3.** Завантажте бінарний файл LiteFS:
```bash
wget [https://github.com/superfly/litefs/releases/download/v0.5.11/litefs-v0.5.11-linux-amd64.tar.gz](https://github.com/superfly/litefs/releases/download/v0.5.11/litefs-v0.5.11-linux-amd64.tar.gz)
tar -xzf litefs-v0.5.11-linux-amd64.tar.gz
```

**Крок 4.** Створіть директорії для монтування віртуальної файлової системи:
```bash
mkdir -p /tmp/primary_mnt /tmp/primary_data
mkdir -p /tmp/replica_mnt /tmp/replica_data
```

**Крок 5. Запуск кластера (потребує 3 паралельні термінали):**
Відкрийте три паралельні термінали в Codespaces.
* **Термінал 1 (Primary Node):**
  ```bash
  sudo ./litefs mount -config primary.yml
  ```
* **Термінал 2 (Replica Node):**
  ```bash
  sudo ./litefs mount -config replica.yml
  ```
* **Термінал 3 (Скрипт вимірювання Replication Lag):**
  ```bash
  sudo python3 measure_litefs.py
  ```
Після виконання скрипт виведе в консоль середню, максимальну затримку та 90-й перцентиль (p90) швидкості реплікації SQLite через HTTP/FUSE.

---

## Результати дослідження
Детальні результати порівняння пропускної здатності, відсотку відмов транзакцій та багатокритеріального вибору СУБД (Метод аналізу ієрархій) наведено в тексті курсової роботи. 

**Короткий підсумок:** Оптимізована конфігурація SQLite (WAL + Memory-Mapped I/O + таймаут + Immediate транзакції) довела здатність обробляти навантаження до 300 одночасних користувачів практично без відмов транзакцій (151 RPS), що робить її економічно вигідною та надійною альтернативою PostgreSQL для проєктів малого та середнього масштабу.

---
*Розроблено в рамках навчального процесу Факультету інформатики НаУКМА, 2026 рік.*
