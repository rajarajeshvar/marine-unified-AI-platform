import logging
from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
import models
from comm_manager import CommunicationManager

logger = logging.getLogger(__name__)

def retry_pending_alerts():
    logger.info("Running Retry Service for pending alerts...")
    db = SessionLocal()
    manager = CommunicationManager(db)
    
    try:
        pending_alerts = db.query(models.Alert).filter(models.Alert.status == "Pending").all()
        for alert in pending_alerts:
            # Increment retry count
            alert.retry_count += 1
            db.commit()
            
            logger.info(f"Retrying alert {alert.id} (Attempt #{alert.retry_count})")
            success = manager.process_alert(alert)
            if success:
                logger.info(f"Alert {alert.id} successfully delivered on retry.")
            else:
                logger.info(f"Alert {alert.id} retry failed again.")
                
    except Exception as e:
        logger.error(f"Error in retry service: {e}")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Runs every 30 seconds
    scheduler.add_job(retry_pending_alerts, 'interval', seconds=30)
    scheduler.start()
    logger.info("Retry Service Scheduler started.")
