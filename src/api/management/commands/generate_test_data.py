import random
import time
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from mimesis import Person, Address, Datetime, Text
from mimesis.locales import Locale
from src.api.models import ParkingLot, Spot, Booking

class Command(BaseCommand):
    help = 'Генерує великий обсяг тестових даних для курсової (Users, Lots, Spots, Bookings)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--size', 
            type=int, 
            required=True,
            help='Кількість бронювань для генерації (наприклад: 100000, 5000000)'
        )

    def handle(self, *args, **options):
        bookings_count = options['size']
        
        # На кожні 20 бронювань - 1 користувач. На кожні 1000 бронювань - 1 парковка.
        users_count = max(500, bookings_count // 20)
        lots_count = max(10, bookings_count // 1000)
        spots_per_lot = 50 

        self.stdout.write(self.style.SUCCESS(
            f'Починаємо генерацію: {bookings_count} бронювань, {users_count} юзерів, '
            f'{lots_count} парковок, {lots_count * spots_per_lot} місць...'
        ))
        start_time = time.time()

        person = Person(Locale.UK)
        address = Address(Locale.EN)
        text_gen = Text(Locale.EN)

        # 1. ГЕНЕРАЦІЯ КОРИСТУВАЧІВ
        self.stdout.write(f'Генерація користувачів ({users_count})...')
        users_to_create = []
        for _ in range(users_count):
            users_to_create.append(User(
                username=person.username() + str(random.randint(10000, 999999)),
                email=person.email(),
                first_name=person.first_name(),
                last_name=person.last_name(),
            ))
            if len(users_to_create) >= 10000:
                User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                users_to_create = []
        if users_to_create:
            User.objects.bulk_create(users_to_create, ignore_conflicts=True)

        users = list(User.objects.all().values_list('id', flat=True))

        # 2. ГЕНЕРАЦІЯ ПАРКОВОК
        self.stdout.write(f'Генерація майданчиків ({lots_count})...')
        lots_to_create = []
        for _ in range(lots_count):
            lots_to_create.append(ParkingLot(
                name=f"Parking {address.city()} {random.randint(1, 1000)}",
                city=address.city(),
                street=address.street_name(),
                building=str(random.randint(1, 150)),
                base_price_per_hour=round(random.uniform(20.0, 100.0), 2),
                description=text_gen.text(quantity=1),
                latitude=address.latitude(),
                longitude=address.longitude()
            ))
        ParkingLot.objects.bulk_create(lots_to_create)
        lots = list(ParkingLot.objects.all())

        # 3. ГЕНЕРАЦІЯ МІСЦЬ
        self.stdout.write(f'Генерація паркомісць ({lots_count * spots_per_lot})...')
        spots_to_create = []
        for lot in lots:
            for i in range(1, spots_per_lot + 1):
                spots_to_create.append(Spot(
                    number=f"{random.choice(['A', 'B', 'C', 'D'])}-{i}",
                    lot=lot,
                    is_ev=random.random() < 0.15, 
                    is_disabled=random.random() < 0.05, 
                ))
            if len(spots_to_create) >= 10000:
                Spot.objects.bulk_create(spots_to_create)
                spots_to_create = []
        if spots_to_create:
            Spot.objects.bulk_create(spots_to_create)
            
        spots = list(Spot.objects.all().values_list('id', flat=True))

        # 4. ГЕНЕРАЦІЯ БРОНЮВАНЬ
        self.stdout.write(f'Генерація бронювань ({bookings_count})...')
        bookings_to_create = []
        now = timezone.now()
        
        for i in range(bookings_count):
            start_at = now + timedelta(
                days=random.randint(-30, 30), 
                hours=random.randint(0, 23)
            )
            end_at = start_at + timedelta(hours=random.randint(1, 48))
            
            is_cancelled = random.random() < 0.2
            status = 'cancelled' if is_cancelled else 'confirmed'
            cancel_reason = "Changed plans" if is_cancelled else ""

            bookings_to_create.append(Booking(
                user_id=random.choice(users),
                spot_id=random.choice(spots),
                start_at=start_at,
                end_at=end_at,
                status=status,
                cancellation_reason=cancel_reason
            ))

            if len(bookings_to_create) >= 20000:
                Booking.objects.bulk_create(bookings_to_create)
                bookings_to_create = []
                # Виводимо прогрес
                self.stdout.write(f'  ...збережено {i + 1} / {bookings_count} бронювань')
                
        if bookings_to_create:
            Booking.objects.bulk_create(bookings_to_create)

        end_time = time.time()
        self.stdout.write(self.style.SUCCESS(f'✅ Генерація успішно завершена за {end_time - start_time:.2f} секунд!'))