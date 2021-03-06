import re
from dateutil.parser import parse
from bs4 import BeautifulSoup
from urllib import request
from datetime import datetime
import time


currentdate=time.strftime('%Y-%m-%d')

# This was just for testing purposes
# currentdate='2018-01-01'

############# To be modified #############                                                                  
TOPIC = "((?![Pp]ress\s)[Cc]onference(?!\s[Cc]all))|[Rr]oadshow|[Ii]nvestor\sday?s"
pagename="Straumann"
ID="1199"
address="https://www.straumann.com/group/en/home/investors/news-an-events/investor-calendar.html"
##########################################

def altnames(mydict):
    aux_mydict = mydict.copy()
    for elem in mydict.keys():
        if "/" in elem:
            for alt in elem.split("/"):
                aux_mydict[alt] = mydict[elem]
            del aux_mydict[elem]
    return aux_mydict   

def findrows(soup_browser):
    """This method receives as parameter a BeautifulSoup object and
    returns a list of strings, one for each event to be processed"""
    rows = []
    try:
    ############# To be modified #############
        # This was the original, example code
        # rows=["13/14 November 2018$UBS Conference - London$UBS"]
        
        # Get all the lines from the web page
        all_lines = soup_browser.find_all("table")[0].find_all("td", {"class": "search-result-entry"})
        
        # Get the text from the lines
        text_lines = ["$".join([e.strip() for e in lines.recursiveChildGenerator() if isinstance(e,str) and len(e.strip())]) for lines in all_lines]
        
        # The sponsor is embedded in the event title
        # Let's see if there is a match in the list of sponsors in the dictionary
        for line in text_lines:
            if line != "":
                for sponsor in psponsors.keys():
                    if sponsor in line:
                        # Now add the sponsor value
                        sponsor_line = "$".join((line, sponsor)).strip()
                        break
                    else:
                        # If no sponsor found, add an empty line
                        sponsor_line = "$".join((line, '')).strip()
                # Append to the list of lines
                rows.append(sponsor_line)                  
    ##########################################

    except e:
        print(e, "Could not process webpage")
    return rows


def output(m,spondict,citydict):
    ############# To be modified #############
    # This was the original, example code
    # ti,d,c,s="Press Conference","2021-11-13/14","London","UBS"

    try:
        # Start by defining groups 
        # group 1: title
        title = m.group(1)
            
        # group 2: date
        date = m.group(2)
        # The date always has a point --> remove it
        date = date.replace(".","")
        # Read the string 'date' and convert it to a datetime object from format "dd mm yyyy"
        date = datetime.strptime(date, "%d %b %Y")
        # Now that we have a datetime object, change its format as requested
        date = date.strftime('%Y-%m-%d')
        
        # group 3: city
        city = m.group(3)
        # transform the city into a code
        if city in pcities.keys():
            city = pcities.get(city,city)
        else:
            city = "Not available"
            
        # We are not using this
        # group 4: country
        # country = m.group(4)
        # print("country:", country)        
        
        # group 5: sponsor
        sponsor = m.group(5)
        if sponsor == "":
            sponsor = "Not available"        
        
        ## Define output
        ti,d,c,s=title,date,city,sponsor

        ###########################################
        return ti.strip(), d, c.strip(), s.strip()    
    except e:
        return e,0,currentdate,0,0

    
def processhtml(pageID,pageAddress,pcities,psponsors):
    """This method reads in the webpage with id pageID and url pageAddress
    and prints out the requested information for each of the relevant events found"""
    ############# To be modified #############
    url=request.urlopen(pageAddress,timeout=None).read()
    soup = BeautifulSoup(url,"lxml")
 
    r="(.*)\$(.*)\$(.*)\$(.*)\$(.*)"   
    for line in findrows(soup):
        m1=re.search(TOPIC,line)
        if m1:
            # Type of event: 1 = Roadshow; 2 = Conference (but not Press Conference or Conference Call); 3 = Investor day(s)
            t = 0 # this must be changed accordingly
            
            pattern_road = re.compile("[Rr]oadshow")
            pattern_conf = re.compile("((?![Pp]ress\s)[Cc]onference(?!\s[Cc]all))")
            pattern_inve = re.compile("[Ii]nvestor\sday?s")
            if pattern_road.match(m1.group(0)):
                 t = 1
            elif pattern_conf.match(m1.group(0)):
                 t = 2
            elif pattern_inve.match(m1.group(0)):
                 t = 3
            else:
                t = "Not available"
            m2=re.search(r,line)
            if m2:
                ti,d,c,s=output(m2,psponsors,pcities)
                if d[:10]>currentdate:
                    c=pcities.get(c,c)
                    s=psponsors.get(s,s)
                    newrecord="Company: %s\nType: %s\nDate: %s\nTitle: %s\nCity: %s\nSponsor: %s\n"%(pageID,t,d,ti,c,s)
                    print(newrecord)
    ##########################################                    
    
                            
if __name__ == "__main__":
    ## Read cities list from file    
    cities=dict([line.strip().split(";") for line in open("city.csv", encoding='ISO-8859-1').readlines()[1:]])
    pcities = dict(zip([x for x in cities.values()],cities.keys()))
    pcities=altnames(pcities)
    ## Read sponsors list from file     
    sponsors=dict([line.strip().split(";") for line in open("sponsor.csv").readlines()[1:]])
    psponsors = dict(zip(sponsors.values(),sponsors.keys()))
    psponsors = altnames(psponsors)  

    print("Extract information from %s webpage"%pagename)
    processhtml(ID,address,pcities,psponsors)

                






