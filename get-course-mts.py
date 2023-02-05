from typing import Tuple, List
from bs4 import BeautifulSoup
import re
import requests
import json
from datetime import datetime
import csv

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
RESULT_CSV_FILENAME = "result.csv"

# Variables
driver: webdriver.Chrome

# Get current termcode given date (which is a datetime object)
def getTermcode(date):
    # return the 'year' part of the termcode
    year_termcode = int(date.year) - 1900
    # return the 'month' part of the termcode
    # 1 = Winter; 5 = Spring; 9 = Fall
    month_termcode = 1 if date.month < 5 else 5 if date.month < 9 else 9
    return f"{year_termcode}{month_termcode}"

# Get current termcode
def getCurrentTerm():
    return getTermcode(datetime.now())

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

# Convert # of seconds to hours:minutes
def convertTime(seconds):
  return f"{str(seconds // 3600).zfill(2)}:{str((seconds % 3600) // 60).zfill(2)}"

# Write data to a csv with specified file path
def writeDataToCsv(data, filename):
  with open(filename, 'w', newline='') as csvfile:
    field_names = ["course_code", "date", "start_time", "end_time"]
    writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=field_names)
    writer.writeheader()
    for e in data:
      writer.writerow(e)

# Main function
def getCoursesMts():
  courseCodes = getCourseCodesForDegree()
  result = []

  for cc in courseCodes:
    courseSections = getCourseSectionsFromUwFlow(cc.split(" ")[0], cc.split(" ")[1])
    if len(courseSections) == 0: continue

    # Filter to just get tests
    courseSections = filter(lambda cs: cs["term_id"] == int(getCurrentTerm()) and len(re.findall("TST", cs["section_name"])) > 0, courseSections)
    
    for cs in courseSections:
      meetings = cs["meetings"][0]
      # Get date and time of the exam
      date = datetime.fromisoformat(meetings["start_date"]).date()
      start_time = convertTime(meetings["start_seconds"])
      end_time = convertTime(meetings["end_seconds"])
      
      result += [{
        "course_code": cc, 
        "date": date, 
        "start_time": start_time, 
        "end_time": end_time
      }]

  writeDataToCsv(result, RESULT_CSV_FILENAME)

if __name__ == '__main__':
  chrome_options = Options()
  chrome_options.add_argument("--headless")
  driver = webdriver.Chrome(options=chrome_options)
  
  print("Chromedriver up and running")
  getCoursesMts()
