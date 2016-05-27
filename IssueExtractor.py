# Gregory Gay (greg@greggay.com)
# Google Code Issue Extractor
# Google Code projects that have been archived no longer offer the csv option 
# to download information about issues. This script will crawl the project
# issues and build that CSV file.

# Command line options:
# -p <project name, required>
# -s <desired statuses, optional comma separated list>
# -l <desired labels, optional  comma separated list>

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import getopt
import sys
import os
from selenium import webdriver  
import time  
import calendar

class IssueExtractor(): 

    labels=[]
    status=[]
    spreadsheet=["\"ID\",\"Status\",\"Priority\",\"Owner\",\"Summary\",\"AllLabels\",\"Stars\",\"Reporter\",\"Opened\",\"OpenedTimestamp\""]

    # Returns index of the issues for the project
    def getIssueIndex(self,project,pageNum):
        if pageNum == 1:
            return "https://code.google.com/archive/p/"+project+"/issues"
        else:
            return "https://code.google.com/archive/p/"+project+"/issues?page="+str(pageNum)

    # Returns URL of a requested issue
    def getIssueUrl(self,project,issueNum):
        return "https://code.google.com/archive/p/"+project+"/issues/"+issueNum

    # Splits comma-separated list of statuses and stores the values
    def setStatus(self,statusString):
        self.status=statusString.strip().split(",")

    # Splits comma-separated list of labels and stores the values
    def setLabels(self,labelsString):
        self.labels=labelsString.strip().split(",")

    # Gets the number of pages of issues
    def getNumberOfPages(self,project):
        issueUrl = self.getIssueIndex(project,1)
        # Render the page
        driver = webdriver.Firefox()  
        driver.get(issueUrl)  
        time.sleep(1)  
        
        # Examine the <pager-widget> 
	pageWidget = driver.find_element_by_tag_name("pager-widget")
        pageText = pageWidget.text.strip().split(" ")  
        # Last three elements are "Next", ">", and a blank entry.
        # The element before that is the last page number.   
        numPages = int(pageText[len(pageText)-3])

        # Close the page
        driver.quit() 
        return numPages

    # Scrape a page for issues that match the desired statuses and labels
    def scrapeIssuePage(self,project,page):
        issueUrl = self.getIssueIndex(project,page)

        # Render the page
        driver = webdriver.Firefox()  
        driver.get(issueUrl)  
        time.sleep(1)  
 
        # Get each issue, <tr class="ng-scope">
        issues = driver.find_elements_by_xpath("//tr[@class='ng-scope']") 
        for issue in issues:
            # Get the table elements associated with each issue
            # items[0] = issue ID
            # items[1] = status
            # items[2] = description and labels
            items = issue.find_elements_by_tag_name("td")
            statusOk = 0
            labelsOk = 0

            # If we did not specify any statuses, include the issue
            if self.status == []:
                statusOk = 1
            # Check whether it is a status that we want
            else:
                for status in self.status:
                    if status == items[1].text.strip():
                        statusOk = 1
                        break

            # If we did not specify any labels, include the issue
            if self.labels == []:
                labelsOk = 1
            # Check whether it has any of the labels that we want
            else:
                # Each label is contained in a span tag with the issue description.
                labels = items[2].find_elements_by_tag_name("span")
                for label in labels:
                    for wantedLabel in self.labels:
                        if label.text == wantedLabel:
                            labelsOk = 1
                            break
                    if labelsOk == 1:
                        break

            # If this is an issue we want, then add it to the CSV
            if statusOk and labelsOk:
                print items[0].text
                self.spreadsheet.append(self.scrapeIssue(project,items[0].text))

        driver.quit()

    def scrapeIssue(self,project,issueID):
        issueUrl = self.getIssueUrl(project,issueID)

        # Render the page
        driver = webdriver.Firefox()  
        driver.get(issueUrl)  
        time.sleep(5)  
 
        #text=driver.page_source 

        # The following fields do not appear in archived projects. 
        # Keeping them in the CSV to maintain compatibility 
        # with default CSV format used by Android Open Source Project 
        # (which still uses Google Code)
        owner = ""
        stars = ""

        # Sidebar contains status and labels, tag <div class="maia-col-4">
        sidebar = driver.find_element_by_class_name("maia-col-4")
        # Status is contained in tag <code class="ng-binding">
        status = sidebar.find_element_by_class_name("ng-binding").text
        # Labels contained in <span class="gca-label ng-binding">
        labels = sidebar.find_elements_by_class_name("gca-label")
        
        priority = ""
        labelList = []
        for label in labels:
            # A label can be the priority. Check for that.
            if "Priority-" in label.text:
                priority = label.text[label.text.index("-")+1:]
            # Add label to list
            labelList.append(label.text)
        
        # Transform label list into a string
        allLabels = ", ".join(labelList)
                        
        # Summary contained in <div class="maia-col-10" id="gca-project-header">
        header = driver.find_element_by_id("gca-project-header")
        # Within that header, summart contained in <p class="ng-binding">
        summary = header.find_element_by_tag_name("p").text

        # Reporter and open date found in <div class="maia-col-8">
        body = driver.find_element_by_class_name("maia-col-8")
        # Within <small class="ng-binding">
        reportedBlock = body.find_element_by_tag_name("small")
        # Reporter found in <i class="ng-binding">
        reporter = reportedBlock.find_element_by_tag_name("i").text
        # Reporting date is fields 3-5 of the text.
        openedParts = reportedBlock.text.strip().split(" ")
        opened = openedParts[2]+" "+openedParts[3]+" "+openedParts[4]+" 00:00:01"
        openedTimeStamp=str(self.generateTimeStamp(opened))

        driver.quit()
        # Populate row of CSV with fields:
        # ID, Status, Priority, Owner, Summary, AllLabels, Stars, Reporter, Opened, OpenedTimestamp
        line = "\""+issueID+"\",\""+status+"\",\""+priority+"\",\""+owner+"\",\""+summary+"\",\""+allLabels+"\",\""+stars+"\",\""+reporter+"\",\""+opened+"\",\""+openedTimeStamp+"\""
        print line
        return line

    # Generate Unix timestamp
    def generateTimeStamp(self,opened):
        timeParts = opened.strip().split(" ")
        year = int(timeParts[2])
        day = int(timeParts[1][:-1])
        
        if timeParts[0] == "Jan":
            month = 1
        elif timeParts[0] == "Feb":
            month = 2
        elif timeParts[0] == "Mar":
            month = 3
        elif timeParts[0] == "Apr":
            month = 4
        elif timeParts[0] == "May":
            month = 5
        elif timeParts[0] == "Jun":
            month = 6
        elif timeParts[0] == "Jul":
            month = 7
        elif timeParts[0] == "Aug":
            month = 8
        elif timeParts[0] == "Sep":
            month = 9
        elif timeParts[0] == "Oct":
            month = 10
        elif timeParts[0] == "Nov":
            month = 11
        elif timeParts[0] == "Dec":
            month = 12
        else:
            raise Exception("Unrecognized date: "+timeParts[0])

        timetuple=(year, month, day, 0, 0, 1)
        return calendar.timegm(timetuple)

    def writeToCsv(self,outputFile):
        where = open(outputFile, 'w')
       
        for line in self.spreadsheet:
            where.write(line+"\n")

        where.close()

def main(argv):
    extractor = IssueExtractor()
    project = ""
    status = ""
    labels = ""
    outFile = ""

    try:
        opts, args = getopt.getopt(argv,"hp:s:l:o:")
    except getopt.GetoptError:
        print 'issueExtractor.py -p <project name> -s <desired statuses, comma separated> -l <desired labels, comma separated> -o <output filename>'
      	sys.exit(2)
  		
    for opt, arg in opts:
        if opt == "-h":
            print 'issueExtractor.py -p <project name> -s <desired statuses, comma separated> -l <desired labels, comma separated> -o <output filename>'
            sys.exit()
      	elif opt == "-p":
            if arg == "":
                raise Exception('No project specified')
            else:
                project = arg
        elif opt == "-s":
            status = arg
        elif opt == "-l":
            labels = arg
        elif opt == "-o":
            outFile = arg

    if outFile == "":
        outFile = project+"-issues.csv"

    if project == '':
        raise Exception('No project specified')
    else:
        # If issues need to be filtered by label or status, set those.
        if status != '':
            extractor.setStatus(status)
        if labels != '':
            extractor.setLabels(labels)

        # Read the issues page and get the number of pages of issues.
        numPages=extractor.getNumberOfPages(project)
        
        # Go through each page and scrape it for issues.
        for page in range(1,numPages):
            extractor.scrapeIssuePage(project,page)

        # Write spreadsheet to CSV
        extractor.writeToCsv(outFile)

# Call into main
if __name__ == '__main__':
    main(sys.argv[1:])
