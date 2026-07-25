import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from scheduler.scheduler import DealScheduler


def main():

    scheduler = DealScheduler()

    try:

        scheduler.start()

    except (KeyboardInterrupt, SystemExit):

        print("\n🛑 DealHunterAI Scheduler Stopped")


if __name__ == "__main__":

    main()

