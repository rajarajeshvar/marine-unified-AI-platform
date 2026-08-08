import models
from sqlalchemy.orm import Session
import requests
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommunicationChannel:
    def __init__(self, name: str, db: Session):
        self.name = name
        self.db = db

    def is_available(self) -> bool:
        status = self.db.query(models.NetworkStatus).filter(models.NetworkStatus.channel == self.name).first()
        return status.is_active if status else False

    def send(self, alert: models.Alert) -> bool:
        raise NotImplementedError

class WiFiChannel(CommunicationChannel):
    def send(self, alert: models.Alert) -> bool:
        return True # Mock success if available

class CellularChannel(CommunicationChannel):
    def send(self, alert: models.Alert) -> bool:
        return True

class SatelliteChannel(CommunicationChannel):
    def send(self, alert: models.Alert) -> bool:
        return True

class RadioChannel(CommunicationChannel):
    def send(self, alert: models.Alert) -> bool:
        return True

class TwilioChannel(CommunicationChannel):
    def send(self, alert: models.Alert) -> bool:
        # Actually send the SMS when this channel is used
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"
            data = {
                "To": settings.twilio_to_number,
                "From": settings.twilio_from_number,
                "Body": f"MARITIME ALERT [{alert.priority.upper()}]: {alert.message} from {alert.ship_id}"
            }
            auth = (settings.twilio_account_sid, settings.twilio_auth_token)
            resp = requests.post(url, data=data, auth=auth, timeout=5)
            logger.info(f"Twilio SMS sent via TwilioChannel: {resp.status_code}")
            return resp.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Failed to send Twilio SMS: {e}")
            return False


class CommunicationManager:
    def __init__(self, db: Session):
        self.db = db
        # Priority order
        self.channels = [
            TwilioChannel("twilio", db),
            WiFiChannel("wifi", db),
            CellularChannel("cellular", db),
            SatelliteChannel("satellite", db),
            RadioChannel("radio", db)
        ]

    def _log_attempt(self, alert_id: str, channel: str, success: bool, reason: str = None):
        log = models.DeliveryLog(
            alert_id=alert_id,
            attempted_channel=channel,
            success=success,
            failure_reason=reason
        )
        self.db.add(log)
        self.db.commit()

    def process_alert(self, alert: models.Alert):
        for channel in self.channels:
            if channel.is_available():
                logger.info(f"Attempting to send alert {alert.id} via {channel.name}")
                try:
                    success = channel.send(alert)
                    if success:
                        self._log_attempt(alert.id, channel.name, True)
                        alert.status = "Delivered"
                        alert.communication_channel = channel.name
                        self.db.commit()
                        return True
                except Exception as e:
                    self._log_attempt(alert.id, channel.name, False, str(e))
            else:
                self._log_attempt(alert.id, channel.name, False, "Channel Offline")

        # All channels failed, queue it
        logger.warning(f"All channels offline. Alert {alert.id} queued for retry.")
        alert.status = "Pending"
        self.db.commit()
        return False
