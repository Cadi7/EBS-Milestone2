from django.utils import timezone
from apps.users.models import User
from apps.tasks.models import Task, Timelog
import random
from datetime import datetime
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create 50.000 random time logs"

    def _log_creating_notice(self, time):
        self.stdout.write(self.style.NOTICE(f"Time logs added in {time}"))

    def handle(self, *args, **options):
        data = []
        start = datetime.now()

        user_ids = User.objects.values_list("id", flat=True)
        task_ids = Task.objects.values_list("id", flat=True)
        for _ in range(50000):
            random_duration = random.randrange(10000)
            time_log = Timelog(
                task_id=random.choice(task_ids),
                user_id=random.choice(user_ids),
                started_at=timezone.now(),
                duration=str(random_duration),
                is_started=True,
                is_stopped=True,
            )
            data.append(time_log)

        Timelog.objects.bulk_create(data)
        end = datetime.now() - start
        self._log_creating_notice(end)
