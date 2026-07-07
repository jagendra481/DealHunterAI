from apscheduler.schedulers.blocking import BlockingScheduler

from engine.deal_engine import DealEngine


class DealScheduler:

    def __init__(self):

        self.scheduler = BlockingScheduler()

    def start(self):

        self.scheduler.add_job(
            self.run,
            trigger="interval",
            seconds=5,
            id="deal_checker",
            replace_existing=True
        )

        print("🚀 Scheduler Started")

        self.scheduler.start()

    def run(self):

        engine = DealEngine()

        engine.run()
