from typing import Tuple, List
from bs4 import BeautifulSoup
import re
import requests
import json
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Constants
BCS_CALENDAR_LINK = "http://ugradcalendar.uwaterloo.ca/page/MATH-Bachelor-of-Computer-Science-1"
COURSES_LINK = "courses/"
TIMEOUT = 10
UWFLOW_API_LINK = "https://uwflow.com/graphql"

# Variables
driver: webdriver.Chrome

# Get course data from UWFlow - returns a list of course sections for that course
def getCourseSectionsFromUwFlow(subjectCode: str, catalogNumber: str):
  uwflow_file_query = open("uwflow-query.txt", 'r').read()

  data = requests.post(UWFLOW_API_LINK, json = {
    "query": uwflow_file_query,
    "operationName": "getCourse",
    "variables": {
      "code": f"{subjectCode.lower()}{catalogNumber}",
      "user_id": 0
    }
  })
  contentBytes = data.content.decode('utf8')

  content = json.loads(contentBytes)
  course = content["data"]["course"]
  
  if len(course) > 0:
    courseSections = course[0]["sections"]
    return courseSections
  return []

# Gets course codes from the calendar in the form [subjectCode, catalogNumber]
def getCourseCodesForDegree() -> List[Tuple[str, str]]:
  driver.get(BCS_CALENDAR_LINK)
  soup = BeautifulSoup(driver.page_source, 'html.parser')

  courseCodes = [s.string for s in soup.find_all('a', href=re.compile(COURSES_LINK))]
  # remove breadth and depth links from the list
  courseCodes = list(filter(lambda cc: len(cc.split(" ")) == 2, courseCodes))
  return courseCodes

# Convert # of seconds to [hours, minutes]
def convertTime(seconds):
  return [seconds // 3600, (seconds % 3600) // 60]

def getCoursesMts():
  courseCodes = getCourseCodesForDegree()
  result = []

  for cc in courseCodes:
    courseSections = getCourseSectionsFromUwFlow(cc.split(" ")[0], cc.split(" ")[1])
    if len(courseSections) == 0: continue

    # Filter to just get tests
    courseSections = filter(lambda cc: len(re.findall("TST", cc["section_name"])) > 0, courseSections)

    for cs in courseSections:
      meetings = cs["meetings"][0]
      # Get date and time of the exam
      date = datetime.fromisoformat(meetings["start_date"])
      start_time = convertTime(meetings["start_seconds"])
      end_time = convertTime(meetings["end_seconds"])
      print('hellpo')

    


if __name__ == '__main__':
  chrome_options = Options()
  chrome_options.add_argument("--headless")
  driver = webdriver.Chrome(options=chrome_options)
  
  print("Chromedriver up and running")
  getCoursesMts()
