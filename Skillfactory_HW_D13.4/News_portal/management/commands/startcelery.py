from django.core.management.base import BaseCommand
from subprocess import Popen, PIPE, STDOUT
import time
import signal
import sys


class Command(BaseCommand):
    help = 'Start Celery beat and worker'

    def handle(self, *args, **options):
        beat_process = Popen(['celery', '-A', 'newsProject', 'beat', '-l', 'INFO'], stdout=PIPE, stderr=STDOUT)
        worker_process = Popen(['celery', '-A', 'newsProject', 'worker', '-l', 'INFO', '--pool', 'solo'], stdout=PIPE, stderr=STDOUT)
        time.sleep(2)
        try:
            # Ожидание завершения процессов
            beat_process.wait()
            worker_process.wait()
        except KeyboardInterrupt:
            # Обработка сигнала прерывания (Ctrl+C)
            beat_process.terminate()
            worker_process.terminate()
            sys.exit(1)


        # Получаем вывод из процессов
        beat_output, beat_error = beat_process.communicate()
        worker_output, worker_error = worker_process.communicate()




