import os

from setup_selenium import Browser, SetupSelenium


def test_can_be_instantiated() -> None:
    s = SetupSelenium(headless=True)
    assert isinstance(s, SetupSelenium)


# these require installation of the browsers
def test_install_chrome() -> None:
    path = SetupSelenium.install_driver(Browser.CHROME)
    assert os.path.exists(path)


def test_install_firefox() -> None:
    path = SetupSelenium.install_driver(Browser.FIREFOX)
    assert os.path.exists(path)


# def test_install_chromium() -> None:
#     path = SetupSelenium.install_driver(Browser.CHROMIUM)
#     assert os.path.exists(path)


# def test_install_edge() -> None:
#     path = SetupSelenium.install_driver(Browser.EDGE)
#     assert os.path.exists(path)
