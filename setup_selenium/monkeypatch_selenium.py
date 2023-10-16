# ruff: noqa: E501, ERA001
"""
This module need to be imported before any of the other selenium modules to work proper
"""
import contextlib
import sys
from collections.abc import Iterable


def uncache(exclude: Iterable[str]) -> None:
    """
    Remove package modules from cache except excluded ones.
    On next import they will be reloaded.

    Args:
        exclude (iter<str>): Sequence of module paths.
    """
    pkgs = []
    for mod in exclude:
        pkg = mod.split(".", 1)[0]
        pkgs.append(pkg)

    to_uncache = []
    for mod in sys.modules:
        if mod in exclude:
            continue

        if mod in pkgs:
            to_uncache.append(mod)
            continue

        for pkg in pkgs:
            if mod.startswith(pkg + "."):
                to_uncache.append(mod)
                break

    for mod in to_uncache:
        del sys.modules[mod]


def monkeypatch() -> None:
    import selenium.common.exceptions

    def __str_replacement__(
        self: selenium.common.exceptions.WebDriverException
        | selenium.common.exceptions.UnexpectedAlertPresentException,
    ) -> str:
        """Hack to fix extra newline at the end of exceptions"""
        exception_msg = f"{self.__class__.__name__}: {self.msg}"
        if self.screen:
            exception_msg += "\nScreenshot: available via screen"
        # selenium4 annoyingly includes the chromedriver stacktrace when an exception occurs
        # if there ever is a way to disable that normally, we should uncomment this code
        # if self.stacktrace is not None:
        #     stacktrace = "\n".join(self.stacktrace)
        #     exception_msg += f"\nStacktrace:\n{stacktrace}"
        return exception_msg

    uncache(["selenium.common.exceptions"])

    selenium.common.exceptions.WebDriverException.__str__ = __str_replacement__  # type: ignore[method-assign]
    selenium.common.exceptions.UnexpectedAlertPresentException.__str__ = (  # type: ignore[method-assign]
        __str_replacement__
    )

    from selenium import webdriver

    def __del_replacement__(
        self: webdriver.Firefox | webdriver.Chrome | webdriver.Edge,
    ) -> None:
        """Hack to force firefox (and any other drivers) to quit when closing scope"""
        with contextlib.suppress(Exception):
            self.quit()

    webdriver.Firefox.__del__ = __del_replacement__  # type: ignore[attr-defined]
    webdriver.Chrome.__del__ = __del_replacement__  # type: ignore[attr-defined]
    webdriver.Edge.__del__ = __del_replacement__  # type: ignore[attr-defined]
