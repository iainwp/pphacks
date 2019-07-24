from bs4 import BeautifulSoup
import sys, os

inf = sys.argv[1]
newmap = sys.argv[2]
outf = sys.argv[3]



with open(inf) as fp:
    soup = BeautifulSoup(fp, features="lxml")

    map = soup.find('course-scribe-event').map
    abs = map['absolute-path']
    print(abs)
    
