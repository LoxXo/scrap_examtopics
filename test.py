import pytest
#import pytest-selenium
import scrap_examtopics
import conftest
from conftest import ListStorage

class TestQuestion:
    def __init__(self) -> None:
        pass
    number: int
    question: str
    answers: list
    comments: list

def test_get_csv(file):
    ListStorage.test_list = scrap_examtopics.get_csv(file)
    assert ListStorage.test_list[0][0] == "https://www.examtopics.com/discussions/splunk/view/139162-exam-splk-1004-topic-1-question-45-discussion/"
    assert ListStorage.test_list[966][0] == "https://www.examtopics.com/discussions/splunk/view/37651-exam-splk-1001-topic-1-question-120-discussion/"

def test_filter_by_text_1002():
    ListStorage.sorted_test_list = scrap_examtopics.search_for_text(ListStorage.test_list, '1002')
    assert ListStorage.sorted_test_list[0] == "https://www.examtopics.com/discussions/splunk/view/102692-exam-splk-1002-topic-1-question-114-discussion/"
    assert ListStorage.sorted_test_list[133] == "https://www.examtopics.com/discussions/splunk/view/98007-exam-splk-1002-topic-1-question-104-discussion/"

def test_scrap_page(firefox_browser):
    for topic in ListStorage.sorted_test_list:
        content = scrap_examtopics.scrap_page(firefox_browser, topic, True)
        assert type(content.number) is int
        assert len(content.question) > 20
        assert len(content.answers) == 4