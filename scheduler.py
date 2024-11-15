from apscheduler.schedulers.background import BackgroundScheduler
from docker_manager import stop_container
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Pod

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

def schedule_container_stop(pod_id: int, container_id: str, duration_minutes: int):
    """
    Schedule the termination of a container after 'duration_minutes'.
    """
    run_date = datetime.utcnow() + timedelta(minutes=duration_minutes)
    scheduler.add_job(stop_and_update_pod, 'date', run_date=run_date, args=[pod_id, container_id])

def stop_and_update_pod(pod_id: int, container_id: str):
    """
    Stop the container and update its status in the database.
    """
    success = stop_container(container_id)
    db: Session = SessionLocal()
    try:
        pod = db.query(Pod).filter(Pod.id == pod_id).first()
        if pod:
            pod.status = "stopped" if success else "error"
            if success:
                db.delete(pod)  # Delete pod record if the container is stopped successfully
            db.commit()
    except Exception as e:
        print(f"Error updating pod {pod_id} status: {e}")
    finally:
        db.close()

def check_expired_pods_periodically():
    """
    Periodically check for expired pods every 2 seconds and stop their containers if they are still running.
    """
    db: Session = SessionLocal()
    try:
        # Find all expired pods that are still running
        expired_pods = db.query(Pod).filter(Pod.expires_at < datetime.utcnow(), Pod.status == "running").all()

        for pod in expired_pods:
            print(f"Found expired pod {pod.id}. Attempting to stop and remove container {pod.container_id}...")
            stop_and_update_pod(pod.id, pod.container_id)

    except Exception as e:
        print(f"Error checking and stopping expired pods: {e}")
    finally:
        db.close()

# Schedule the periodic job to check every 2 seconds for expired pods
scheduler.add_job(check_expired_pods_periodically, 'interval', seconds=2)

# This can be used as a standalone script, or you can import and initialize it in your main application.
if __name__ == "__main__":
    try:
        print("Scheduler started, checking for expired pods every 2 seconds.")
        while True:
            # Keep the main thread alive to let the scheduler run in the background
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler shut down.")
