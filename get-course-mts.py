from typing import Tuple, List
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Constants
BCS_CALENDAR_LINK = "http://ugradcalendar.uwaterloo.ca/page/MATH-Bachelor-of-Computer-Science-1"
COURSES_LINK = "courses/"
TIMEOUT = 10

# Variables
driver: webdriver.Chrome

# Gets course codes from the calendar in the form [subjectCode, catalogNumber]
def getCourseCodesForDegree() -> List[Tuple[str, str]]:
  driver.get(BCS_CALENDAR_LINK)
  soup = BeautifulSoup(driver.page_source, 'html.parser')

  courseCodes = [s.string for s in soup.find_all('a', href=re.compile("courses/"))]
  # remove breadth and depth links from the list
  courseCodes = list(filter(lambda cc: len(cc.split(" ")) == 2, courseCodes))

  print('hello')

def getCoursesMts():
  getCourseCodesForDegree()

if __name__ == '__main__':
  chrome_options = Options()
  chrome_options.add_argument("--headless")
  driver = webdriver.Chrome(options=chrome_options)
  
  print("Chromedriver up and running")
  getCoursesMts()
