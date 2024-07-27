from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import csv
import os
import json


class Question:
    def __init__(self) -> None:
        pass
    topic_nr: int
    number: int
    question: str
    image: object = None
    answers: list
    comments: list

def create_driver():
    options = Options()
    # options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    return driver

def create_dir(folder:str) -> None:
    try:
        os.mkdir(f'./{folder}')
    except:
        print(f'./{folder}/ already exists, skipping creating a directory')
    return None

def check_for_file(folder: str, filename: str):
    if os.path.isfile(f'./{folder}/{filename}.txt') == False:
        return None
    else:
        raise Exception(f'File ./{folder}/{filename} exists, if you want to dump questions delete it.')

def check_csv_content(csvfile:str) -> bool:
    # add checking content of csv file to verify it contains correct links
    if os.path.isfile(csvfile):
        print(f"File {csvfile} already exists, skipping scrapping and writing to it.")
        return True
    return False

def scrap_discussions(driver, page: str):
    disc_list = []
    links_list: list[str] = []
    page_counter = 1

    driver.get(page)
    page_ind = driver.find_element(By.CLASS_NAME, 'discussion-list-page-indicator')
    max_page_count: int = int(page_ind.text.split()[-1])

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
    with open(csvfile, newline='', mode='w') as file:
        csvwrite = csv.writer(file, delimiter='\n')
        file.write("Link\n")
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
        try:
            imageobject = driver.find_element(By.CLASS_NAME, 'in-exam-image')
        except:
            imageobject = None
        # if imagelink:
        #     qname = f't_{numbers_title[0]}_q_{numbers_title[1]}'
        #     download_photo(imagelink, qname)
        answers = driver.find_elements(By.CLASS_NAME, 'multi-choice-item')
        comments = driver.find_elements(By.CLASS_NAME, 'discussion-container')
        full_content.topic_nr = numbers_title[0]
        full_content.number = numbers_title[1]
        question = question.text.encode('ascii', errors='ignore')
        full_content.question = question.decode()
        if imageobject != None:
            full_content.image = imageobject
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

def dump_to_file(content: Question, filename: str, folder: str) -> None:
    if content.image:
        content.image.screenshot(f'./{folder}/t_{content.topic_nr}_q_{content.number}.png')
    with open(f'{folder}/{filename}', 'a') as file:
        file.write("Topic: " + str(content.topic_nr) + " question: " + str(content.number) + ". ")
        file.write(content.question + '\n')
        for answer in content.answers:
            file.write(answer + '\n')
        file.write('\n')
        for comment in content.comments:
            file.write(comment + '\n')
        file.write('------------------------\n\n')
    return None

def create_stock_html(filename: str, folder: str):
    with open(f'{folder}/{filename}.html', 'a') as file:
        file.write(f"<html><head></head><body><p></p></body></html>")

# def dump_to_json(content: Question, filename: str, folder: str) -> None:
#     with open(f'{folder}/{filename}.json', 'a') as file:
#         file.write(json.dumps(content.__dict__))

def main():
    csvfilename: str = 'splunklinks.csv'
    link_to_scrap: str = 'https://www.examtopics.com/discussions/splunk/'
    search_phrase = 'splk-1002'
    folder = 'resaults/' + search_phrase

    create_dir(folder)
    check_for_file(folder, search_phrase)
    driver = create_driver()
    if check_csv_content(csvfilename) == False:
        #disc_links = scrap_discussions(driver, link_to_scrap)
        disc_links = scrap_discussions(driver, link_to_scrap)
        write_csv(csvfilename, disc_links)
    topics = get_csv(csvfilename)
    sorted_topics = search_for_text(topics, search_phrase)
    for topic in sorted_topics:
        content: Question = scrap_page(driver, topic, True)
        dump_to_file(content, f'{search_phrase}.txt', folder)

    driver.close()

if __name__ == "__main__":
    main()
