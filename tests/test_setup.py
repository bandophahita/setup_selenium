from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import pytest
from selenium import __version__ as selenium_version, webdriver
from selenium.common.exceptions import NoSuchDriverException
from semantic_version import Version  # type: ignore[import-untyped]

from setup_selenium import Browser, SetupSelenium, set_logger
from setup_selenium.setup_selenium import logger as original_logger

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture

CHROME_VERSION_OLD = "118.0.5993.70"
CHROME_VERSION_NEW = "133.0.6943.98"
EDGE_VERSION_OLD = "133.0.3065.69"
EDGE_VERSION_NEW = "136.0.3240.50"
GECKO_VERSION_OLD = "0.34.0"
GECKO_VERSION_NEW = "0.35.0"
FIREFOX_VERSION_OLD = "134.0"
FIREFOX_VERSION_NEW = "135.0.1"


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
        Browser.CHROME, driver_version=CHROME_VERSION_NEW, install_browser=False
    )

    assert CHROME_VERSION_NEW in path1


def test_install_chrome_browser_version() -> None:
    path1, path2 = SetupSelenium.install_driver(
        Browser.CHROME, browser_version=CHROME_VERSION_OLD
    )

    assert CHROME_VERSION_OLD in path2


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
        Browser.FIREFOX, driver_version=GECKO_VERSION_OLD, install_browser=False
    )

    assert GECKO_VERSION_OLD in path1


def test_install_firefox_browser_version() -> None:
    path1, path2 = SetupSelenium.install_driver(
        Browser.FIREFOX, browser_version=FIREFOX_VERSION_OLD
    )

    assert FIREFOX_VERSION_OLD in path2


@pytest.mark.xfail(
    Version(selenium_version) < Version("4.28.0"), reason="broken until selenium 4.28"
)
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
        Browser.EDGE, driver_version=EDGE_VERSION_OLD, install_browser=False
    )

    assert EDGE_VERSION_OLD in path1


@pytest.mark.xfail(
    Version(selenium_version) < Version("4.28.0"), reason="broken until selenium 4.28"
)
def test_install_edge_browser_version() -> None:
    path1, path2 = SetupSelenium.install_driver(
        Browser.EDGE, browser_version=EDGE_VERSION_OLD
    )

    assert EDGE_VERSION_OLD in path2


def test_can_be_instantiated() -> None:
    s = SetupSelenium(headless=True)
    assert isinstance(s, SetupSelenium)
    assert isinstance(s.driver, (webdriver.Firefox, webdriver.Chrome, webdriver.Edge))
    assert s.driver.service.is_connectable()


def test_accepts_paths() -> None:
    path1, path2 = SetupSelenium.install_driver(
        Browser.CHROME, browser_version=CHROME_VERSION_NEW
    )
    s = SetupSelenium(headless=True, driver_path=path1, browser_path=path2)
    assert isinstance(s, SetupSelenium)
    assert isinstance(s.driver, webdriver.Chrome)
    assert s.driver.service.is_connectable()
    assert s.driver.service.path == path1
    assert s.driver.capabilities["browserVersion"] == CHROME_VERSION_NEW


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


def test_chrome_bad_binary_path() -> None:
    with pytest.raises(NoSuchDriverException):
        SetupSelenium.create_driver(
            Browser.CHROME, headless=True, binary="/fake_path/binary"
        )


def test_firefox_bad_binary_path() -> None:
    with pytest.raises(NoSuchDriverException):
        SetupSelenium.create_driver(
            Browser.FIREFOX, headless=True, binary="/fake_path/binary"
        )


def test_edge_bad_binary_path() -> None:
    with pytest.raises(NoSuchDriverException):
        SetupSelenium.create_driver(
            Browser.EDGE, headless=True, binary="/fake_path/binary"
        )


def test_create_firefox_wrong_options() -> None:
    with pytest.raises(AssertionError):
        SetupSelenium.create_driver(
            Browser.FIREFOX, options=SetupSelenium.chrome_options()
        )


def test_create_chrome_wrong_options() -> None:
    with pytest.raises(AssertionError):
        SetupSelenium.create_driver(
            Browser.CHROME, options=SetupSelenium.edge_options()
        )


def test_create_edge_wrong_options() -> None:
    with pytest.raises(AssertionError):
        SetupSelenium.create_driver(
            Browser.EDGE, options=SetupSelenium.firefox_options()
        )


@pytest.fixture
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
        "--disable-back-forward-cache\n"
        "--disable-background-timer-throttling\n"
        "--disable-breakpad\n"
        "--disable-component-extensions-with-background-pages\n"
        "--disable-ipc-flooding-protection\n"
        "--enable-features=NetworkService,NetworkServiceInProcess\n"
        "--enable-logging\n"
        "--export-tagged-pdf\n"
        "--force-color-profile=srgb\n"
        "--metrics-recording-only\n"
        "--mute-audio\n"
        # "--remote-debugging-pipe\n"
        "--disable-renderer-backgrounding\n"
        "--disable-backgrounding-occluded-windows\n"
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
        "--headless=new"
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
        "--disable-back-forward-cache\n"
        "--disable-background-timer-throttling\n"
        "--disable-breakpad\n"
        "--disable-component-extensions-with-background-pages\n"
        "--disable-ipc-flooding-protection\n"
        "--enable-features=NetworkService,NetworkServiceInProcess\n"
        "--enable-logging\n"
        "--export-tagged-pdf\n"
        "--force-color-profile=srgb\n"
        "--metrics-recording-only\n"
        "--mute-audio\n"
        # "--remote-debugging-pipe\n"
        "--disable-renderer-backgrounding\n"
        "--disable-backgrounding-occluded-windows\n"
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
        "--headless=new"
    ) in caplog.messages

    assert in_caplog("Driver info: chromedriver=", caplog)
    assert in_caplog("Browser info:      chrome=", caplog)

    set_logger(original_logger)
