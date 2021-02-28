import pytest
import json
from unittest import mock
from main import app as flask_app
from main import requests


@pytest.fixture
def app():
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def insert_first_data(client):
    data = {
        "surname": "Mola",
        "lastname": "Mazo",
        "name": "Charlie",
        "github_name": "SERGIOALOB",
        "github_following": 2,
    }
    client.post(
        "/posts", data=json.dumps(data), headers={"Content-Type": "application/json"}
    )
    return "DATA INSERTED"
