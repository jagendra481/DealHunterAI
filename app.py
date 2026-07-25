import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from scheduler.scheduler import DealScheduler


def main():
    print("=" * 60)
    print("🚀 DealHunterAI Started Successfully")
    print("=" * 60)

    scheduler = DealScheduler()
    scheduler.start()


if __name__ == "__main__":
    main()

