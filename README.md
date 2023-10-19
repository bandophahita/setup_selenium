# setup_selenium
I get tired of having to rewrite the setup logic for selenium drivers 
in every project.  Time to consolidate.


# Basic usage

```python
from setup_selenium import Browser, SetupSelenium

driver = SetupSelenium.create_driver(browser=Browser.CHROME, headless=True)
```

# Advanced usage
```python
from setup_selenium import Browser, SetupSelenium

driver = SetupSelenium.create_driver(
    browser=Browser.CHROME,
    headless=True,
    enable_log_performance=False,
    enable_log_console=False,
    enable_log_driver=False,
    log_dir="./logs",
    binary="/usr/bin/chromium",
    driver_path="/usr/bin/chromedriver",
)
```

> [!NOTE]
> It is possible to enable the performance and console logging 
> but only for chrome based browsers. This only enables the browser ability.
> It is up to the tester to handle logging the messages.



# Driver installation
```python
from setup_selenium import Browser, SetupSelenium

driver_path, browser_path = SetupSelenium.install_driver(Browser.CHROME, "118.0.5993.70")
```

# Custom logger
```python
import logging
from setup_selenium import Browser, SetupSelenium, set_logger

set_logger(logging.getLogger("your_custom_logger"))
driver = SetupSelenium.create_driver(browser=Browser.CHROME, headless=True)
```

# Instantiating SetupSelenium
While it is possible to use the class directly caution is advised; as the class
will create the driver upon instantiation. 

```python
from setup_selenium import SetupSelenium

s = SetupSelenium(headless=True)
assert s.driver.service.is_connectable()
```


# Automatic driver and browser installation
This package not only handles setup of the webdriver but also will
automatically install the webdriver and/or browser depending on your
configuration.

If you do not provide a `driver_path` argument to `create_driver` the package
will utilize `selenium-manager` to install the webdriver for the browser type selected.



If the `selenium-manager` cannot find the install path for the browser type
(which is usually in the native install path) it will download a version of the browser
and use that.  

Passing a valid `binary_path` will not trigger any download of the browser.
Passing a valid `driver_path` will not trigger any download of the webdriver.
