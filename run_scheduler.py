from scheduler.scheduler import DealScheduler


def main():

    scheduler = DealScheduler()

    try:

        scheduler.start()

    except (KeyboardInterrupt, SystemExit):

        print("\n🛑 DealHunterAI Scheduler Stopped")


if __name__ == "__main__":

    main()
