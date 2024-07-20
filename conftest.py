from pytest import fixture
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class ListStorage:
    test_list: list = []
    sorted_test_list: list = []


def pytest_addoption(parser):
    parser.addoption(
        "--file",
        action="store",
        default="splunk.csv"
    )

@fixture()
def file(request):
    return request.config.getoption("--file")

@fixture()
def firefox_browser():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    yield driver
    driver.quit()