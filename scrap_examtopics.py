from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import csv
import os


class Question:
    def __init__(self) -> None:
        pass
    number: int
    question: str
    answers: list
    comments: list

def create_driver():
    options = Options()
    #options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    return driver

def scrap_discussions(driver, page: str):
    disc_list = []
    links_list: list[str] = []
    page_counter = 1

    driver.get(page)
    page_ind = driver.find_element(By.CLASS_NAME, 'discussion-list-page-indicator')
    #max_page_count: int = int(page_ind.text.split()[-1])
    max_page_count = 5

    while (page_counter <= max_page_count):
        try:
            driver.get(page + f'{page_counter}')
            page_counter += 1
            try:
                disc_list = driver.find_elements(By.CSS_SELECTOR, 'div.dicussion-title-container')
                for disc_title in disc_list:
                    disc_link = disc_title.find_element(By.CSS_SELECTOR, 'a.discussion-link')
                    links_list.append(disc_link.get_attribute('href'))
            except Exception as err:
                print(f'Scrapping the page {page_counter} failed: {err}')
                raise
        except Exception as err:
            print(f"Getting the page {page_counter} failed: {err}")
            raise
    return links_list

def write_csv(csvfile: str, content: list) -> None:
    if os.path.isfile(csvfile):
        print(f"File {csvfile} already exists, skipping writing to it.")
        return None
    with open(csvfile, newline='', mode='w') as file:
        csvwrite = csv.writer(file, delimiter='\n')
        csvwrite.writerow(content)

def get_csv(csvfile: str) -> list:
    with open(csvfile, newline='', mode='r') as file:
        next(file, None)
        csvread = csv.reader(file)
        page_list = list(csvread)
    return page_list

def search_for_text(page_list: list, phrase: str) -> list:
    sorted_list: list = []
    for page in page_list:
        if phrase in page[0]:
            sorted_list.append(page[0])
    return sorted_list

def fix_comments(comments: list) -> list:
    raw = comments[0].text
    splited = raw.split('\n')
    return splited

def scrap_page(driver, page: str, add_comments: bool) -> Question:
    try:
        full_content = Question()
        full_content.answers = []
        full_content.comments = []
        driver.get(page)
        title = driver.title
        numbers_title = [int(s) for s in title.split() if s.isdigit()]
        question = driver.find_element(By.CLASS_NAME, 'card-text')
        answers = driver.find_elements(By.CLASS_NAME, 'multi-choice-item')
        comments = driver.find_elements(By.CLASS_NAME, 'discussion-container')
        full_content.number = numbers_title[1]
        full_content.question = question.text
        for answer in answers:
            answer = answer.text.encode('ascii', errors='ignore')
            full_content.answers.append(answer.decode())
        if add_comments == True:
            comments_fixed = fix_comments(comments)
            for comment in comments_fixed:
                comment = comment.encode('ascii', errors='ignore')
                full_content.comments.append(comment.decode())
        return full_content 
    except Exception as err:
        print(f"Scrapping of questions failed: {err}")
        raise

def dump_to_file(content: Question, filename: str) -> None:
    with open(filename, 'a') as file:
        file.write(str(content.number) + ". ")
        file.write(content.question + '\n')
        for answer in content.answers:
            file.write(answer + '\n')
        file.write('\n')
        for comment in content.comments:
            file.write(comment + '\n')
        file.write('------------------------\n\n')
    return None

def main():
    csvfilename: str = 'examlinks.csv'
    link_to_scrap: str = 'https://www.examtopics.com/discussions/splunk/'
    search_phrase = '1002'
    #topics = get_csv('splunk.csv')
    #sorted_topics = filter_by_text(topics, '1003')

    driver = create_driver()
    disc_links = scrap_discussions(driver, link_to_scrap)
    write_csv(csvfilename, disc_links)
    topics = get_csv(csvfilename)
    sorted_topics = search_for_text(topics, search_phrase)

    for topic in sorted_topics:
        content: Question = scrap_page(driver, topic, True)
        dump_to_file(content, "splk1xxx.txt")

    driver.close()

if __name__ == "__main__":
    main()
