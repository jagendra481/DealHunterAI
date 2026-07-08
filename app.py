from scheduler.scheduler import DealScheduler


def main():
    print("=" * 60)
    print("🚀 DealHunterAI Started Successfully")
    print("=" * 60)

    scheduler = DealScheduler()
    scheduler.start()


if __name__ == "__main__":
    main()
