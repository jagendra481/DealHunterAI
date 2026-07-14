import time
import traceback

from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from engine.deal_engine import DealEngine


CHECK_INTERVAL_MINUTES = 60


class DealScheduler:

    def __init__(self):

        self.scheduler = BlockingScheduler(
            job_defaults={
                "coalesce": True,
                "max_instances": 1,
                "misfire_grace_time": 300
            }
        )

    # ==========================================================
    # START SCHEDULER
    # ==========================================================

    def start(self):

        print(
            "🚀 DealHunterAI Scheduler Starting..."
        )

        # ======================================================
        # RUN FIRST SCAN IMMEDIATELY
        # ======================================================

        self.run()

        # ======================================================
        # SCHEDULE FUTURE SCANS
        # ======================================================

        self.scheduler.add_job(
            self.run,
            trigger="interval",
            minutes=CHECK_INTERVAL_MINUTES,
            id="deal_checker",
            replace_existing=True
        )

        print(
            f"\n✅ Scheduler Started — "
            f"checking every "
            f"{CHECK_INTERVAL_MINUTES} minutes"
        )

        print(
            f"⏰ Next scan will run approximately "
            f"{CHECK_INTERVAL_MINUTES} minutes "
            f"after scheduler startup."
        )

        # ======================================================
        # START APSCHEDULER
        # ======================================================

        self.scheduler.start()

    # ==========================================================
    # RUN DEAL ENGINE
    # ==========================================================

    def run(self):

        started_at = datetime.now()

        start_time = time.perf_counter()

        print(
            "\n"
            + "=" * 60
        )

        print(
            "🔍 Starting Product Scan..."
        )

        print(
            "🕒 Scan Started:",
            started_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        print(
            "=" * 60
        )

        try:

            engine = DealEngine()

            engine.run()

            duration = (
                time.perf_counter()
                - start_time
            )

            completed_at = datetime.now()

            print(
                "\n✅ Product Scan Completed"
            )

            print(
                "🕒 Scan Completed:",
                completed_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            print(
                f"⚡ Scan Duration: "
                f"{duration:.2f} seconds"
            )

        except Exception as error:

            duration = (
                time.perf_counter()
                - start_time
            )

            print(
                "\n❌ PRODUCT SCAN FAILED"
            )

            print(
                "Error:",
                str(error)
            )

            print(
                f"⚡ Failed After: "
                f"{duration:.2f} seconds"
            )

            traceback.print_exc()

        finally:

            print(
                "=" * 60
            )

    # ==========================================================
    # SHUTDOWN
    # ==========================================================

    def shutdown(self):

        print(
            "\n🛑 Shutting Down Scheduler..."
        )

        if self.scheduler.running:

            self.scheduler.shutdown(
                wait=False
            )

        print(
            "✅ DealHunterAI Scheduler Stopped"
        )
