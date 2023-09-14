from pytest_mock import MockerFixture
import qual
from qual.core.database import auto_discover_models


def test_discover(mocker: MockerFixture):
    mock_import_module = mocker.patch("importlib.import_module")
    auto_discover_models(qual)

    mock_import_module.assert_called()
