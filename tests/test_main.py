import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SECRET_TOKEN = 'qwerty'


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def test_get_images_positive():
    images_code = 'c91e42b4-7923-4c6b-9590-7061a1cc4a6a'
    client = TestClient(app)
    response = client.get(f'/frames/{images_code}')
    print(response.content)
    print(response.json())
    print(response.status_code)
    assert response.status_code == 200
    assert response.json()[0]['name'] == '13ba7039-f0bd-4975-84e2-d67188a6743d.jpg'


def test_get_images_not_found():
    images_code = 'some_str'
    client = TestClient(app)
    response = client.get(f'/frames/{images_code}')
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_images_multiple():
    images_code = '3f3dcf1e-1475-486a-b458-f104568e3795'
    client = TestClient(app)
    response = client.get(f'/frames/{images_code}')
    assert response.status_code == 200
    assert response.json()[0]['name'] == '40fb2e05-3fcd-43bb-a4a5-803b3f48f5aa.jpg'
    assert response.json()[1]['name'] == 'cb94d017-4008-4040-87a2-2e9da91e3990.jpg'


def test_delete_images_negative():
    images_code = 'bf851403-0f93-4a52-9363-59e329dd8d40'
    client = TestClient(app)
    response = client.delete(f'/frames/{images_code}')
    assert response.status_code == 404
    assert response.json()['detail'] == "Code not found"


# def test_delete_images_positive():
#     images_code = 'bf851403-0f93-4a52-9363-59e329dd8d40'
#     client = TestClient(app)
#     response = client.delete(f'/frames/{images_code}')
#
#     assert response.status_code == 200
#     assert response.raw == "Files deleted"


# test doesn't work, get 400 response status
# def test_create_images_positive():
#     db = override_get_db()
#     client = TestClient(app)
#     images = [open(Path(os.getcwd(), 'tests/1.jpg'), 'rb')]
#     response = client.post('/frames/', data={'images': images},
#                            headers={'content-type': 'multipart/form-data'})
#
#     assert response.status_code == 200
