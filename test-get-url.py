import requests
import re
from bs4 import BeautifulSoup
from pprint import pprint 
from sys import argv

rezult = requests.get(argv[1])
soup = BeautifulSoup(rezult.text, "lxml")
page = soup.find("div", attrs={"class" : "feed-item"})
base = "https://bcs-express.ru"
header = page.find("div", attrs={"class": "feed-item__title"}).text
time = page.find("div", attrs={"class": "feed-item__date"}).text
href = base + re.findall('.*href="(\S+)".*', str(page))[0]
text = page.find("div", attrs={"class": "feed-item__summary"}).text

print (time)
print (header)
print (text)
print (href)
