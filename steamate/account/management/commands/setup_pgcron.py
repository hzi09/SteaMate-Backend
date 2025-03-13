from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "pg_cron을 이용해 10분마다 미인증 계정 삭제 스케줄 등록"

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("""                
                SELECT cron.schedule(
                    'delete_unverified_users', 
                    '*/10 * * * *',
                    $$ DELETE FROM users WHERE is_verified = FALSE AND created_at < NOW() - INTERVAL '10 minutes' $$
                );
            """)
        self.stdout.write(self.style.SUCCESS('pg_cron 작업이 등록되었습니다!'))