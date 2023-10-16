from __future__ import annotations

import errno
import logging
import os as os
from enum import Enum
from typing import TYPE_CHECKING, TypeAlias

from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from semantic_version import Version  # type: ignore
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.logger import set_logger as wdm_set_logger
from webdriver_manager.core.os_manager import ChromeType
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

if TYPE_CHECKING:
    from collections.abc import Mapping

    from selenium.webdriver import Chrome, Edge, Firefox
    from selenium.webdriver.common.options import ArgOptions

    T_WebDriver: TypeAlias = Firefox | Chrome | Edge

__all__ = ["SetupSelenium"]


def create_logger(name: str) -> logging.Logger:
    __logger: type[logging.Logger] = logging.getLoggerClass()
    logr: logging.Logger = logging.getLogger(name)
    logging.setLoggerClass(__logger)
    logr.setLevel(logging.DEBUG)
    return logr


logger = create_logger("sel")
wdm_set_logger(logger)


def set_logger(logr: logging.Logger) -> None:
    """
    Set the global logger with a custom logger
    """
    # Check if the logger is a valid logger
    if not isinstance(logr, logging.Logger):
        raise ValueError("The logger must be an instance of logging.Logger")

    # Bind the logger input to the global logger
    global logger  # noqa: PLW0603
    logger = logr
    wdm_set_logger(logger)


class Browser(str, Enum):
    EDGE = "edge"
    CHROME = "chrome"
    CHROMIUM = "chromium"
    FIREFOX = "firefox"


################################################################################
################################################################################
class SetupSelenium:
    DIMENSIONS: Mapping[str, tuple[int, int]] = {
        # ratio 4:3
        "1024": (1024, 768),
        "1280": (1280, 960),
        "1600": (1600, 1200),
        "1920": (1920, 1440),
        # ratio 16:9
        "720": (1280, 720),
        "1080": (1920, 1080),
        "1440": (2560, 1440),
        "2160": (3840, 2160),  # 4k
        "4320": (7680, 4320),  # 8k
    }

    def __init__(
        self,
        browser: Browser = Browser.CHROME,
        baseurl: str = "",
        timeout: int = 15,
        headless: bool = False,
        window_size: str = "720",
        enable_log_performance: bool = False,
        enable_log_console: bool = False,
        enable_log_driver: bool = False,
        log_path: str = "./logs",
        driver_version: str | None = None,
    ) -> None:
        log_path = os.path.abspath(os.path.expanduser(log_path))
        self.main_window_handle: str = ""
        self.screenshot_path: str = self.make_screenshot_path(log_path)
        self.log_path: str = log_path
        self.timeout: int = timeout
        self.baseurl: str = baseurl

        driver_path = SetupSelenium.install_driver(browser, driver_version)

        self.driver: T_WebDriver = self.create_driver(
            browser=browser,
            headless=headless,
            enable_log_performance=enable_log_performance,
            enable_log_console=enable_log_console,
            enable_log_driver=enable_log_driver,
            log_dir=log_path,
            driver_path=driver_path,
        )

        # driver must be setup before the following
        self.driver.set_window_position(0, 0)
        self.set_window_size(window_size)
        self.set_main_window_handle()

    ############################################################################
    @staticmethod
    def make_screenshot_path(
        output_dir: str = "./logs", screenshots: str = "screenshots"
    ) -> str:
        """
        Set the output directory for where screenshots should go.
        """
        output_dir = os.path.abspath(os.path.expanduser(output_dir))
        if os.path.split(output_dir)[-1].lower() != screenshots:
            output_dir = os.path.join(output_dir, screenshots)

        try:
            os.makedirs(output_dir)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(output_dir):
                pass
            else:
                raise

        return output_dir

    ############################################################################
    @staticmethod
    def log_options(options: ArgOptions) -> None:
        opts = "\n".join(options.arguments)
        logger.debug(f"{opts}")

    @staticmethod
    def install_driver(
        browser: str,
        version: str | None = None,
    ) -> str:
        browser = browser.lower()
        version = version or None

        if browser == Browser.FIREFOX:
            driver_path = GeckoDriverManager(version).install()
            if not os.path.exists(f"{driver_path}"):
                raise FileNotFoundError("Geckodriver was not downloaded.")
            logger.debug(f"installed chromedriver {driver_path}")

        elif browser in Browser.CHROME:
            driver_path = ChromeDriverManager(version).install()

            if not os.path.exists(f"{driver_path}"):
                raise FileNotFoundError("Chromedriver was not downloaded.")
            logger.debug(f"installed chromedriver {driver_path}")

        elif browser == Browser.CHROMIUM:
            driver_path = ChromeDriverManager(
                version, chrome_type=ChromeType.CHROMIUM
            ).install()
            logger.debug(f"installed chromedriver {driver_path}")

        elif browser == Browser.EDGE:
            driver_path = EdgeChromiumDriverManager(version).install()

            if not os.path.exists(f"{driver_path}"):
                raise FileNotFoundError("Edgedriver was not downloaded.")
            logger.debug(f"installed chromedriver {driver_path}")
        else:
            raise ValueError(f"Unknown browser: {browser}")

        return driver_path

    @staticmethod
    def create_driver(
        browser: Browser,
        headless: bool = False,
        enable_log_performance: bool = False,
        enable_log_console: bool = False,
        enable_log_driver: bool = False,
        log_dir: str = "./logs",
        binary: str | None = None,
        driver_path: str | None = None,
    ) -> T_WebDriver:
        browser = browser.lower()
        driver: T_WebDriver
        if browser == Browser.FIREFOX:
            driver = SetupSelenium.firefox(
                headless=headless,
                enable_log_driver=enable_log_driver,
                log_dir=log_dir,
                binary=binary,
                driver_path=driver_path,
            )

        elif browser == Browser.CHROME:
            driver = SetupSelenium.chrome(
                headless=headless,
                enable_log_performance=enable_log_performance,
                enable_log_console=enable_log_console,
                enable_log_driver=enable_log_driver,
                log_dir=log_dir,
                binary=binary,
                driver_path=driver_path,
            )

        elif browser == Browser.CHROMIUM:
            driver = SetupSelenium.chromium(
                headless=headless,
                enable_log_performance=enable_log_performance,
                enable_log_console=enable_log_console,
                enable_log_driver=enable_log_driver,
                log_dir=log_dir,
                binary=binary,
                driver_path=driver_path,
            )

        elif browser == Browser.EDGE:
            driver = SetupSelenium.edge(
                headless=headless,
                enable_log_performance=enable_log_performance,
                enable_log_console=enable_log_console,
                enable_log_driver=enable_log_driver,
                log_dir=log_dir,
                binary=binary,
                driver_path=driver_path,
            )

        else:
            raise ValueError(f"Unknown browser: {browser}")

        return driver

    @staticmethod
    def firefox_options() -> webdriver.FirefoxOptions:
        options = webdriver.FirefoxOptions()
        options.set_capability("unhandledPromptBehavior", "ignore")

        # profile settings
        options.set_preference("app.update.auto", False)
        options.set_preference("app.update.enabled", False)
        options.set_preference("network.prefetch-next", False)
        options.set_preference("network.dns.disablePrefetch", True)
        return options

    @staticmethod
    def firefox(
        headless: bool = False,
        enable_log_driver: bool = False,
        log_dir: str = "./logs",
        driver_path: str | None = None,
        binary: str | None = None,
        options: webdriver.FirefoxOptions = None,
    ) -> webdriver.Firefox:
        options = options or SetupSelenium.firefox_options()
        if binary:
            options.binary_location = binary

        if headless:
            options.add_argument("--headless")

        # setting logpath to /dev/null will prevent geckodriver from creating it's own
        # log file. if we enable root logging, we can capture the logging from
        # geckodriver, ourselves.
        logpath = "/dev/null"
        options.log.level = "fatal"  # type: ignore[assignment]
        if enable_log_driver:
            lp = os.path.abspath(os.path.expanduser(log_dir))
            logpath = os.path.join(lp, "geckodriver.log")

        if driver_path:
            service = FirefoxService(executable_path=driver_path, log_path=logpath)
        else:
            service = FirefoxService(log_path=logpath)

        driver = webdriver.Firefox(service=service, options=options)

        driverversion = driver.capabilities["moz:geckodriverVersion"]
        browserversion = driver.capabilities["browserVersion"]

        logger.info(f"Driver info: geckodriver={driverversion}")
        logger.info(f"Browser info:    firefox={browserversion}")
        SetupSelenium.log_options(options)
        return driver

    @staticmethod
    def chrome_options() -> webdriver.ChromeOptions:
        logger.debug("Setting up chrome options")
        # The list of options set below mostly came from this StackOverflow post
        # https://stackoverflow.com/q/48450594/2532408
        opts = (
            "--disable-extensions",
            "--allow-running-insecure-content",
            "--ignore-certificate-errors",
            "--disable-single-click-autofill",
            "--disable-autofill-keyboard-accessory-view[8]",
            "--disable-full-form-autofill-ios",
            # https://bugs.chromium.org/p/chromedriver/issues/detail?id=402#c128
            # "--dns-prefetch-disable",
            "--disable-infobars",
            # chromedriver crashes without these two in linux
            "--no-sandbox",
            "--disable-dev-shm-usage",
            # it's possible we no longer need to do these
            # "enable-automation",  # https://stackoverflow.com/a/43840128/1689770
            # "--disable-browser-side-navigation",  # https://stackoverflow.com/a/49123152/1689770
            "--disable-gpu",  # https://stackoverflow.com/q/51959986/2532408
            # # https://groups.google.com/forum/m/#!topic/chromedriver-users/ktp-s_0M5NM[21-40]
            # "--enable-features=NetworkService,NetworkServiceInProcess",
        )

        options = webdriver.ChromeOptions()
        for opt in opts:
            options.add_argument(opt)
        return options

    @staticmethod
    def chrome(
        headless: bool = False,
        enable_log_performance: bool = False,
        enable_log_console: bool = False,
        enable_log_driver: bool = False,
        log_dir: str = "./logs",
        driver_path: str | None = None,
        binary: str | None = None,
        options: webdriver.ChromeOptions = None,
    ) -> webdriver.Chrome:
        options = options or SetupSelenium.chrome_options()
        if binary:
            options.binary_location = binary

        # options.headless = headless
        # This is the new way to run headless. Unfortunately it crashes a lot.
        # https://crbug.com/chromedriver/4353
        # https://crbug.com/chromedriver/4406
        if headless:
            options.add_argument("--headless")

        logging_prefs = {"browser": "OFF", "performance": "OFF", "driver": "OFF"}

        if enable_log_console:
            logging_prefs["browser"] = "ALL"

        # by default performance is disabled.
        if enable_log_performance:
            logging_prefs["performance"] = "ALL"
            options.add_experimental_option(
                "perfLoggingPrefs",
                {
                    "enableNetwork": True,
                    "enablePage": False,
                },
            )

        args: list | None = None
        logpath = None
        if enable_log_driver:
            lp = os.path.abspath(os.path.expanduser(log_dir))
            logpath = os.path.join(lp, "chromedriver.log")
            args = [
                # "--verbose"
            ]
            logging_prefs["driver"] = "ALL"

        options.set_capability("goog:loggingPrefs", logging_prefs)

        logger.debug("initializing chromedriver")
        if driver_path:
            service = ChromeService(
                executable_path=driver_path,
                service_args=args,
                log_path=logpath,
            )
        else:
            service = ChromeService(
                service_args=args,
                log_path=logpath,
            )

        driver = webdriver.Chrome(service=service, options=options)

        driver_vers = driver.capabilities["chrome"]["chromedriverVersion"].split(" ")[0]
        browser_vers = driver.capabilities["browserVersion"]

        drvmsg = f"Driver info: chromedriver={driver_vers}"
        bsrmsg = f"Browser info:      chrome={browser_vers}"

        dver = Version.coerce(driver_vers)
        bver = Version.coerce(browser_vers)
        if dver.major != bver.major:
            logger.critical(drvmsg)
            logger.critical(bsrmsg)
            logger.critical("chromedriver and browser versions not in sync!!")
            logger.warning(
                "https://chromedriver.chromium.org/downloads for the latest version"
            )
        else:
            logger.info(drvmsg)
            logger.info(bsrmsg)
        SetupSelenium.log_options(options)

        # set_throttle(driver)  # noqa: ERA001
        return driver

    @staticmethod
    def set_throttle(driver: webdriver.Chrome):
        # experimental settings to slow down browser
        # @formatter:off
        # fmt: off
        network_conditions = {
            # latency, down, up
            "GPRS"     : (500, 50,    20),
            "SLOW3G"   : (100, 250,   100),
            "FAST3G"   : (40,  750,   250),
            "LTE"      : (20,  4000,  3000),
            "DSL"      : (5,   2000,  1000),
            "WIFI"     : (2,   30000, 15000),
        }
        # fmt: on
        # @formatter:on
        net_type = "SLOW3G"
        net_lat, net_down, net_up = network_conditions[net_type]
        net_down = net_down / 8 * 1024
        net_up = net_up / 8 * 1024
        driver.set_network_conditions(
            offline=False,
            latency=net_lat,
            download_throughput=net_down,
            upload_throughput=net_up,
        )
        driver.execute_cdp_cmd("Emulation.setCPUThrottlingRate", {"rate": 100})

    @staticmethod
    def chromium(
        headless: bool = False,
        enable_log_performance: bool = False,
        enable_log_console: bool = False,
        enable_log_driver: bool = False,
        log_dir: str = "./logs",
        driver_path: str | None = None,
        binary: str | None = None,
        options: webdriver.ChromeOptions = None,
    ) -> webdriver.Chrome:
        options = options or SetupSelenium.chrome_options()
        if binary:
            options.binary_location = binary

        # This is the new way to run headless in the future. Unfortunately it crashes a lot.  # noqa: E501
        # https://crbug.com/chromedriver/4353
        # https://crbug.com/chromedriver/4406
        if headless:
            options.add_argument("--headless")

        logging_prefs = {"browser": "OFF", "performance": "OFF", "driver": "OFF"}

        if enable_log_console:
            logging_prefs["browser"] = "ALL"

        # by default performance is disabled.
        if enable_log_performance:
            logging_prefs["performance"] = "ALL"
            options.set_capability(
                "perfLoggingPrefs",
                {
                    "enableNetwork": True,
                    "enablePage": False,
                    "enableTimeline": False,
                },
            )

        args: list | None = None
        logpath = None
        if enable_log_driver:
            lp = os.path.abspath(os.path.expanduser(log_dir))
            logpath = os.path.join(lp, "chromedriver.log")
            args = [
                # "--verbose"
            ]
            logging_prefs["driver"] = "ALL"

        options.set_capability("goog:loggingPrefs", logging_prefs)

        logger.debug("initializing chromedriver")
        if driver_path:
            service = ChromeService(
                executable_path=driver_path,
                service_args=args,
                log_path=logpath,
            )
        else:
            service = ChromeService(
                service_args=args,
                log_path=logpath,
            )

        driver = webdriver.Chrome(service=service, options=options)

        driver_vers = driver.capabilities["chrome"]["chromedriverVersion"].split(" ")[0]
        browser_vers = driver.capabilities["browserVersion"]

        drvmsg = f"Driver info: chromedriver={driver_vers}"
        bsrmsg = f"Browser info:    chromium={browser_vers}"

        dver = Version.coerce(driver_vers)
        bver = Version.coerce(browser_vers)
        if dver.major != bver.major:
            logger.critical(drvmsg)
            logger.critical(bsrmsg)
            logger.critical("chromedriver and browser versions not in sync!!")
            logger.warning(
                "https://chromedriver.chromium.org/downloads for the latest version"
            )
        else:
            logger.info(drvmsg)
            logger.info(bsrmsg)
        SetupSelenium.log_options(options)

        return driver

    @staticmethod
    def edge_options() -> webdriver.EdgeOptions:
        opts = (
            "--disable-extensions",
            "--allow-running-insecure-content",
            "--ignore-certificate-errors",
            "--disable-single-click-autofill",
            "--disable-autofill-keyboard-accessory-view[8]",
            "--disable-full-form-autofill-ios",
            # https://bugs.chromium.org/p/chromedriver/issues/detail?id=402#c128
            # "--dns-prefetch-disable",
            "--disable-infobars",
            # edgedriver crashes without these two in linux
            "--no-sandbox",
            "--disable-dev-shm-usage",
            # it's possible we no longer need to do these
            # "enable-automation",  # https://stackoverflow.com/a/43840128/1689770
            # "--disable-browser-side-navigation",  # https://stackoverflow.com/a/49123152/1689770
            # "--disable-gpu",  # https://stackoverflow.com/q/51959986/2532408
            # # https://groups.google.com/forum/m/#!topic/chromedriver-users/ktp-s_0M5NM[21-40]
            # "--enable-features=NetworkService,NetworkServiceInProcess"  # noqa: ERA001
        )
        options = webdriver.EdgeOptions()
        for opt in opts:
            options.add_argument(opt)
        return options

    @staticmethod
    def edge(
        headless: bool = False,
        enable_log_performance: bool = False,
        enable_log_console: bool = False,
        enable_log_driver: bool = False,
        log_dir: str = "./logs",
        driver_path: str | None = None,
        binary: str | None = None,
        options: webdriver.EdgeOptions = None,
    ) -> webdriver.Edge:
        # edge
        # https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

        options = options or SetupSelenium.edge_options()
        if binary:
            options.binary_location = binary

        if headless:
            options.add_argument("--headless")
            
        logging_prefs = {"browser": "OFF", "performance": "OFF", "driver": "OFF"}

        if enable_log_console:
            logging_prefs["browser"] = "ALL"

        # by default performance is disabled.
        if enable_log_performance:
            logging_prefs["performance"] = "ALL"
            options.set_capability(
                "perfLoggingPrefs",
                {
                    "enableNetwork": True,
                    "enablePage": False,
                    "enableTimeline": False,
                },
            )

        args: list | None = None
        logpath = None
        if enable_log_driver:
            lp = os.path.abspath(os.path.expanduser(log_dir))
            logpath = os.path.join(lp, "chromedriver.log")
            args = [
                # "--verbose"
            ]
            logging_prefs["driver"] = "ALL"

        options.set_capability("ms:loggingPrefs", logging_prefs)

        logger.debug("initializing edgedriver")
        if driver_path:
            service = EdgeService(
                executable_path=driver_path,
                service_args=args,
                log_path=logpath,
            )
        else:
            service = EdgeService(
                service_args=args,
                log_path=logpath,
            )
        driver = webdriver.Edge(service=service, options=options)

        driver_vers = driver.capabilities["msedge"]["msedgedriverVersion"].split(" ")[0]
        browser_vers = driver.capabilities["browserVersion"]

        drvmsg = f"Driver info: msedge webdriver={driver_vers}"
        bsrmsg = f"Browser info:          msedge={browser_vers}"

        dver = Version.coerce(driver_vers)
        bver = Version.coerce(browser_vers)
        if dver.major != bver.major:
            logger.critical(drvmsg)
            logger.critical(bsrmsg)
            logger.critical("msedgedriver and browser versions not in sync!!")
            logger.warning(
                "https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/ "
                "for the latest version"
            )
        else:
            logger.info(drvmsg)
            logger.info(bsrmsg)
        SetupSelenium.log_options(options)
        return driver

    ############################################################################
    def set_window_size(self, size: str = "720") -> None:
        if size == "max":
            self.driver.maximize_window()
            return

        width, height = SetupSelenium.DIMENSIONS.get(
            size, SetupSelenium.DIMENSIONS.get(size, (1280, 720))
        )
        self.driver.set_window_size(width, height)

    def set_main_window_handle(self, window: str | None = None) -> str:
        if not window:
            # does the main_window_handle exist and point to an available window?
            if not self.main_window_handle:
                try:
                    window = self.driver.current_window_handle
                except NoSuchWindowException:
                    try:
                        window = self.driver.window_handles[0]
                    except WebDriverException:
                        # Have we closed all the windows?
                        raise
        if window:
            self.main_window_handle = window
        return self.main_window_handle

    # not sure we need these -- commenting out to verify it doesn't break something
    ############################################################################
    # def close(self) -> None:
    #     if self.driver is not None:
    #         self.driver.close()
    #
    # ############################################################################
    # def quit(self) -> None:  # noqa: A003
    #     if self.driver is not None:
    #         self.driver.quit()

    ############################################################################
    def __repr__(self) -> str:
        browser = self.driver.name if self.driver is not None else "NoBrowserSet"
        url = self.baseurl
        return f"{self.__class__.__name__} :: {browser} -> {url}"
