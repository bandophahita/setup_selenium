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
    browser=Browser.CHROMIUM,
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

driver_path = SetupSelenium.install_driver(Browser.CHROME, "118.0.5993.70")
```

# Custom logger
```python
import logging
from setup_selenium import Browser, SetupSelenium, set_logger

set_logger(logging.getLogger("your_custom_logger"))
driver = SetupSelenium.create_driver(browser=Browser.CHROME, headless=True)
```
