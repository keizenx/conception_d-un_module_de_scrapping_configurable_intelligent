import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import ScrapingSession

s = ScrapingSession.objects.last()
print(f'Session ID: {s.id}')
print(f'Status: {s.status}')
print(f'Logs: {len(s.progress_logs)} entries')
print('\nAll logs:')
for log in s.progress_logs:
    print(f"  [{log.get('type', 'info')}] {log.get('message', '')}")
