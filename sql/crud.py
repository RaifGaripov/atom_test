from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models


def get_images(db: Session, code_name: str):
    return db.query(models.Inbox).filter(models.Inbox.code == code_name).all()


def create_image(db: Session, code: str, date: datetime, image_name: str):
    db_image = models.Inbox(code=code, name=image_name, date=date)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def delete_images(db: Session, code_name: str):
    names_and_dates = []
    with db as session:
        images = get_images(session, code_name)
        if not images:
            raise HTTPException(status_code=404, detail="Code not found")
        for image in images:
            names_and_dates.append((image.name, image.date))
        session.query(models.Inbox).filter(models.Inbox.code == code_name). \
            delete(synchronize_session=False)
        session.commit()
        return names_and_dates
