"""Example of adding tasks on app startup."""

from .extensions import scheduler
from .models import Job
from app import db
from datetime import datetime


@scheduler.task(
    "interval",
    id="job_sync",
    seconds=15,
    max_instances=1,
    start_date="2000-01-01 12:19:00",
)
def task1():
    """Sample task 1.

    Added when app starts.
    """
    # print(" --- running task 1 in every 1s!")  # noqa: T001

    # oh, do you need something from config?
    with scheduler.app.app_context():
        now = datetime.now()
        # print(scheduler.app.config)  # noqa: T001
        jobs = Job.query.filter(Job.status == 1).filter(Job.stage < 100).all()
        for job in jobs:
            if job.stage == 1 and job.stage == 0:
                job.equipment.status = 1
            job.stage += 1
            if job.stage == 100:
                job.status = 2
                job.end_time = now
                job.equipment.status = 0
        db.session.commit()


def task2():
    """Sample task 2.

    Added when /add url is visited.
    """
    print("running task 2!")  # noqa: T001