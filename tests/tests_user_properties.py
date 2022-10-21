import os
import pytest

from dotenv import load_dotenv

from src.user_properties import LambdaCoreHandler

load_dotenv()


@pytest.fixture(autouse=True)
def get_event():
    yield {
        "body": '{"test":"body"}',
        "resource": "/{proxy+}",
        "path": "/path/to/resource",
        "httpMethod": "POST",
        "queryStringParameters": {"query": "tavomantilla@hotmail.com", "pages": True},
        "pathParameters": {"proxy": "path/to/resource"},
        "stageVariables": {"baz": "qux"},
        "headers": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-US,en;q=0.8",
            "Cache-Control": "max-age=0",
            "authorization": os.getenv("AUTHORIZATION"),
        },
    }


@pytest.fixture(autouse=True)
def start_app(get_event):
    lambda_core = LambdaCoreHandler(event=get_event, context={})
    return lambda_core


def test_result(start_app):
    assert isinstance(start_app.result(), list)


def test_get_schema_properties(start_app):
    assert isinstance(start_app.get_schema_properties(), list)


@pytest.fixture(autouse=True)
def get_user_id(start_app):
    return start_app.get_user_id()


def test_get_generic_properties(start_app, get_user_id):
    assert isinstance(start_app.get_generic_properties(user_id=get_user_id), list)


def test_get_user_properties(start_app, get_user_id):
    assert isinstance(start_app.get_user_properties(user_id=get_user_id), list)


@pytest.fixture(autouse=True)
def get_testing_properties(start_app):
    return start_app.get_schema_properties()


def test_build_properties(start_app, get_testing_properties):
    assert isinstance(start_app.build_properties_body(properties=get_testing_properties), list)


def test_get_data(start_app):
    assert isinstance(start_app.get_data(), list)


def test_get_user_id(start_app):
    assert isinstance(start_app.get_user_id(), int)
