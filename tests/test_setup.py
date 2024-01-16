from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import pytest
from selenium import webdriver
from selenium.common import NoSuchDriverException

from setup_selenium import Browser, SetupSelenium, set_logger
from setup_selenium.selenium_module import logger as original_logger

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


# these require installation of the browsers to pass
def test_install_chrome() -> None:
    path1, path2 = SetupSelenium.install_driver(Browser.CHROME, install_browser=False)
    path3, path4 = SetupSelenium.install_driver(Browser.CHROME, install_browser=True)
    assert os.path.exists(path1)
    assert os.path.exists(path2)
    assert os.path.exists(path3)
    assert os.path.exists(path4)
    assert path2 != path4


def test_install_chrome_path() -> None:
    path1, path2 = SetupSelenium.install_driver(Browser.CHROME, install_browser=False)
    path3, path4 = SetupSelenium.install_driver(Browser.CHROME, browser_path=path2)
    assert path2 == path4


def test_install_chrome_driver_version() -> None:
    path1, path2 = SetupSelenium.install_driver(
        Browser.CHROME, driver_version="116.0.5845.96", install_browser=False
    )

    assert "116.0.5845.96" in path1


def test_install_chrome_browser_version() -> None:
    path1, path2 = SetupSelenium.install_driver(
        Browser.CHROME, browser_version="118.0.5993.70"
    )

    assert "118.0.5993.70" in path2


def test_install_firefox() -> None:
    path1, path2 = SetupSelenium.install_driver(Browser.FIREFOX, install_browser=False)
    path3, path4 = SetupSelenium.install_driver(Browser.FIREFOX, install_browser=True)
    assert os.path.exists(path1)
    assert os.path.exists(path2)
    assert os.path.exists(path3)
    assert os.path.exists(path4)
    assert path2 != path4


def test_install_firefox_path() -> None:
    path1, path2 = SetupSelenium.install_driver(Browser.FIREFOX, install_browser=False)
    path3, path4 = SetupSelenium.install_driver(Browser.FIREFOX, browser_path=path2)
    assert path2 == path4


def test_install_firefox_driver_version() -> None:
    path1, path2 = SetupSelenium.install_driver(
        Browser.FIREFOX, driver_version="0.31.0", install_browser=False
    )

    assert "0.31.0" in path1


def test_install_firefox_browser_version() -> None:
    path1, path2 = SetupSelenium.install_driver(
        Browser.FIREFOX, browser_version="118.0.2"
    )

    assert "118.0.2" in path2


def test_install_edge() -> None:
    path1, path2 = SetupSelenium.install_driver(Browser.EDGE, install_browser=False)
    path3, path4 = SetupSelenium.install_driver(Browser.EDGE, install_browser=True)
    assert os.path.exists(path1)
    assert os.path.exists(path2)
    assert os.path.exists(path3)
    assert os.path.exists(path4)
    assert path2 != path4


def test_install_edge_path() -> None:
    path1, path2 = SetupSelenium.install_driver(Browser.EDGE, install_browser=False)
    path3, path4 = SetupSelenium.install_driver(Browser.EDGE, browser_path=path2)
    assert path2 == path4


def test_install_edge_driver_version() -> None:
    path1, path2 = SetupSelenium.install_driver(
        Browser.EDGE, driver_version="118.0.2088.57", install_browser=False
    )

    assert "118.0.2088.57" in path1


def test_install_edge_browser_version() -> None:
    path1, path2 = SetupSelenium.install_driver(
        Browser.EDGE, browser_version="118.0.2088.57"
    )

    assert "118.0.2088.57" in path2


def test_can_be_instantiated() -> None:
    s = SetupSelenium(headless=True)
    assert isinstance(s, SetupSelenium)
    assert isinstance(s.driver, (webdriver.Firefox, webdriver.Chrome, webdriver.Edge))
    assert s.driver.service.is_connectable()


def test_accepts_paths() -> None:
    path1, path2 = SetupSelenium.install_driver(
        Browser.CHROME, browser_version="116.0.5845.96"
    )
    s = SetupSelenium(headless=True, driver_path=path1, browser_path=path2)
    assert isinstance(s, SetupSelenium)
    assert isinstance(s.driver, webdriver.Chrome)
    assert s.driver.service.is_connectable()
    assert s.driver.service.path == path1
    assert s.driver.capabilities["browserVersion"] == "116.0.5845.96"


def test_chrome_service(create_logger: logging.Logger) -> None:
    set_logger(create_logger)
    driver = SetupSelenium.chrome(headless=True)
    assert driver.service.is_connectable()


def test_chrome_bad_driver_path() -> None:
    with pytest.raises(NoSuchDriverException):
        SetupSelenium.chrome(headless=True, driver_path="/fake_path/driver")


def test_firefox_bad_driver_path() -> None:
    with pytest.raises(NoSuchDriverException):
        SetupSelenium.firefox(headless=True, driver_path="/fake_path/driver")


def test_edge_bad_driver_path() -> None:
    with pytest.raises(NoSuchDriverException):
        SetupSelenium.edge(headless=True, driver_path="/fake_path/driver")


def test_create_chrome_bad_driver_path() -> None:
    with pytest.raises(NoSuchDriverException):
        SetupSelenium.create_driver(
            Browser.CHROME, headless=True, driver_path="/fake_path/driver"
        )


def test_create_firefox_bad_driver_path() -> None:
    with pytest.raises(NoSuchDriverException):
        SetupSelenium.create_driver(
            Browser.FIREFOX, headless=True, driver_path="/fake_path/driver"
        )


def test_create_edge_bad_driver_path() -> None:
    with pytest.raises(NoSuchDriverException):
        SetupSelenium.create_driver(
            Browser.EDGE, headless=True, driver_path="/fake_path/driver"
        )


def test_chrome_bad_binary_path(create_logger: logging.Logger) -> None:
    set_logger(create_logger)
    driver = SetupSelenium.create_driver(
        Browser.CHROME, headless=True, binary="/fake_path/binary"
    )
    assert driver.service.is_connectable()


def test_firefox_bad_binary_path(create_logger: logging.Logger) -> None:
    set_logger(create_logger)
    driver = SetupSelenium.create_driver(
        Browser.FIREFOX, headless=True, binary="/fake_path/binary"
    )
    assert driver.service.is_connectable()


def test_edge_bad_binary_path(create_logger: logging.Logger) -> None:
    set_logger(create_logger)
    driver = SetupSelenium.create_driver(
        Browser.EDGE, headless=True, binary="/fake_path/binary"
    )
    assert driver.service.is_connectable()


@pytest.fixture()
def create_logger() -> logging.Logger:
    """Create a logger."""
    logr = logging.getLogger("testsetupsel")
    logr.setLevel(logging.DEBUG)
    return logr


def in_caplog(s: str, caplog: LogCaptureFixture) -> bool:
    """For matching partial strings against the caplog"""
    return len(list(filter(lambda x: s in x, caplog.messages))) > 0


def test_default_logger(
    caplog: LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.DEBUG, logger="sel"):
        SetupSelenium(headless=True)

    assert "initializing chromedriver" in caplog.messages
    assert (
        "--disable-extensions\n"
        "--allow-running-insecure-content\n"
        "--ignore-certificate-errors\n"
        "--disable-single-click-autofill\n"
        "--disable-autofill-keyboard-accessory-view[8]\n"
        "--disable-full-form-autofill-ios\n"
        "--disable-infobars\n"
        "--no-sandbox\n"
        "--disable-dev-shm-usage\n"
        "--disable-gpu\n"
        "--headless"
    ) in caplog.messages

    assert in_caplog("Driver info: chromedriver=", caplog)
    assert in_caplog("Browser info:      chrome=", caplog)


def test_custom_logger(
    caplog: LogCaptureFixture, create_logger: logging.Logger
) -> None:
    """Test the custom logger."""

    # Set the custom logger
    set_logger(create_logger)

    with caplog.at_level(logging.DEBUG, logger="testsetupsel"):
        SetupSelenium(headless=True)

    assert "initializing chromedriver" in caplog.messages
    assert in_caplog("Selenium Manager binary", caplog)
    assert (
        "--disable-extensions\n"
        "--allow-running-insecure-content\n"
        "--ignore-certificate-errors\n"
        "--disable-single-click-autofill\n"
        "--disable-autofill-keyboard-accessory-view[8]\n"
        "--disable-full-form-autofill-ios\n"
        "--disable-infobars\n"
        "--no-sandbox\n"
        "--disable-dev-shm-usage\n"
        "--disable-gpu\n"
        "--headless"
    ) in caplog.messages

    assert in_caplog("Driver info: chromedriver=", caplog)
    assert in_caplog("Browser info:      chrome=", caplog)

    set_logger(original_logger)
