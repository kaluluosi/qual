from typing import Any
import pytest
from unittest.mock import MagicMock
from pytest_mock import MockerFixture
from qual.core.xyapi import _PackageMetadata, _setup_app_info


@pytest.fixture
def fake_meta(mocker: MockerFixture) -> dict[str, str]:
    mock = mocker.MagicMock()

    mock.metadata.json = {
        "name": "pkg_name",
        "summary": "pkg_summary",
        "version": "pkg_version",
        "description": "pkg_description",
        "author": "pkg_author",
        "author_email": "pkg_author_email",
    }
    return mock


@pytest.fixture
def mock_distribution(mocker: MockerFixture, fake_meta: Any):
    mock = mocker.patch("importlib.metadata.Distribution.from_name")
    mock.return_value = fake_meta
    return mock


def test_packagemetadata(mock_distribution: MagicMock):
    pkg_meta = _PackageMetadata.get("fake_package")
    mock_distribution.assert_called_once_with("fake_package")

    assert pkg_meta.model_dump() == mock_distribution.return_value.metadata.json


def test_setup_fastapi_info_from_packagemetadata(
    mock_distribution: MagicMock, mocker: MockerFixture
):
    mock_app = mocker.patch("fastapi.FastAPI")
    metadata = mock_distribution.return_value.metadata.json
    _setup_app_info(mock_app)

    assert mock_app.title == metadata["name"]
    assert mock_app.summary == metadata["summary"]
    assert mock_app.description == metadata["description"]
    assert mock_app.version == metadata["version"]
    assert mock_app.contact == {
        "name": metadata["author"],
        "email": metadata["author_email"],
    }
