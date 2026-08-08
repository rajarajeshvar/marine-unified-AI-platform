from database import engine, SessionLocal, Base
import models

# Create tables
Base.metadata.create_all(bind=engine)

# Seed default networks
def seed_networks():
    db = SessionLocal()
    channels = ["twilio", "wifi", "cellular", "satellite", "radio"]
    for ch in channels:
        existing = db.query(models.NetworkStatus).filter_by(channel=ch).first()
        if not existing:
            db.add(models.NetworkStatus(channel=ch, is_active=True))
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_networks()
