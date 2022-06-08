import uuid
import os

from minio import Minio
from fastapi import FastAPI, UploadFile, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime

from pydantic import conlist

from sql import crud, models
from sql.database import SessionLocal, engine
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_minio_client():
    client = Minio('play.min.io',
                   access_key='Q3AM3UQ867SPQQA43P2F',
                   secret_key='zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG',
                   secure=False,
                   )
    return client


@app.post('/frames/')
def create_image(
        images: conlist(UploadFile, min_items=1, max_items=15),
        db: Session = Depends(get_db),
):
    client = get_minio_client()

    inbox = datetime.now()
    bucket_name = inbox.strftime('%Y%m%d')
    bucket = client.bucket_exists(bucket_name)
    if not bucket:
        client.make_bucket(bucket_name)
    else:
        print('bucket {inbox} already exists!')

    result = []
    code = str(uuid.uuid4())
    for image in images:
        uuid_img = uuid.uuid4()
        image_name = ''.join((str(uuid_img), '.jpg'))
        file_size = os.fstat(image.file.fileno()).st_size

        client.put_object(bucket_name, image_name, image.file, file_size)
        db_image = crud.create_image(db=db, code=code, date=inbox,
                                     image_name=image_name)
        result.append(jsonable_encoder(db_image))

    return JSONResponse(content=result)


@app.get('/frames/{images_code}')
def get_images(
        images_code: str,
        db: Session = Depends(get_db)
):
    db_images = crud.get_images(db=db, code_name=images_code)
    result = jsonable_encoder(db_images)
    return result


@app.delete('/frames/{images_code}')
def delete_images(
        images_code: str,
        db: Session = Depends(get_db)
):
    client = get_minio_client()
    images = crud.delete_images(db, images_code)
    for name, date in images:
        client.remove_object(date.strftime('%Y%m%d'), name)
    return "Files deleted"
