# -*- coding: utf-8 -*-
"""
@author: Teddy Crepineau

Purpose: scrape a list of publisher ads.txt file and returns list of authorized digital sellers        
"""

import pandas as pd
import requests
import re
import matplotlib.pyplot as plt

class URLOperations(object):
    """
    Given a list of domain, the class will 1) build the full URL, 2) send a request to the defaukt browser 
    to open the webpage, and 3) parse the page and return its content. This class assumes that the webpage is
    encoded in utf-8.
    """
    
    def __init__(self, domain, path):
        self.domain = domain
        self.path = path
        
    def getDomain(self):
        return self.domain
    
    def getPath(self):
        return '/' + self.path
    
    def getFullURL(self):
        return self.buildURL()
    
    def doesExist(self):
        return self.checkPageExist()
    
    def buildURL(self):
        return 'http://' + self.domain + self.getPath()  #assumes browser will redirect to https://...  
                                                    #if https://... exists
    def openWebPage(self):
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64'}
        req = requests.get(self.getFullURL(), headers=headers)
        return req
    
    def checkHTTPCode(self):
        return self.openWebPage().status_code
    
    def parsedWebPage(self):
        return self.openWebPage().text # assumes webpage is encoded in utf-8
    
    def __str__(self):
        return str(self.buildURL)



def openFile(file):
    """
    Simple function to open the template file containing list of donain names to scrape. Assumes domain names are
    in the format domain.comm or www.domain.com.
    
    IMPORTANT: DO NOT INCLUDE "http://" or "https://"
    """
   
    file = open(file)
    list_of_domains = [domain.rstrip() for domain in file.readlines()[1:]]
    
    return list_of_domains

def createURLObjects(domains, path):
    """
    Build full URL to scrape. "domains" correspond to a list of url returned by the openFile function. "path"
    is a simple string indicating the path of the URL. DO NOT INCLUDE "/" in your path (i.e. for test.com/test),
    simply include "test" as the path. The decision to create a separate function is intented to create 
    flexibility for the user to scrape different webpage - even though this program is specifically intended 
    to scrape ads.txt pages
    """
    full_url = []
    
    for domain in domains:
        full_url.append(URLOperations(domain, path)) #create URLOperations object and append them to full_url list
        
    return full_url

def checkHasAdsFile(list_domain_objects, filter_status, print_status):
    
    has_ads_txt = {}
    ads_txt_data = []
    
    line_start_comment = re.compile(r'^#') #Search for lines with only comments
    comment_in_line = re.compile(r'#.*') #search for lines with comments at the end
    return_char = re.compile(r'\r') #search for \r 
                                 
    for domain in list_domain_objects:
        if print_status:
            print(domain.getDomain(), ': HTTP status -> ', domain.checkHTTPCode())
        if domain.checkHTTPCode() == 404:
            has_ads_txt[domain.getDomain()] = False                        
        elif domain.checkHTTPCode() != 200:
            pass
        else:
            has_ads_txt[domain.getDomain()] = True
            if filter_status == "complete": ## parse webpage and put data in tuple if 
                                            ## filter_status == "complete" (ref runHasAdstxt())
                text_page = domain.parsedWebPage().split('\n')
                for line in text_page:
                    if re.search(line_start_comment, line) or line == "" or line == " ":
                        pass
                    elif re.search(comment_in_line, line):
                        line = comment_in_line.sub("", line)
                        line = return_char.sub("", line)
                        temp_tuple = tuple(line.split(','))
                        ads_txt_data.append((domain.getDomain(),) + temp_tuple)
                    else:
                        line = return_char.sub("", line)
                        temp_tuple = tuple(line.split(','))
                        ads_txt_data.append((domain.getDomain(),) + temp_tuple)
    
    return structureData(has_ads_txt, ads_txt_data, filter_status)

def structureData(has_ads_txt, ads_txt_data, filter_status):
    """
    This function will format the data to make it readible to the user (dataframe + chart)
    """
    
    ## Create csv with data from ads.txt of filter_status == "complete" (ref runHasAdstxt())
    if filter_status == "complete":    
        labels = ["DOMAINS","SSP","PUB_ID","SALES_CHANNEL","CERT_AUTH_ID"]         
        ads_txt_data_df = pd.DataFrame.from_records(ads_txt_data, columns=labels, index=labels[0])
        ads_txt_data_df.to_csv("ads.txt_data.csv") 
    
    has_ads_txt_df = pd.DataFrame.from_dict(has_ads_txt, orient='index')
    has_ads_txt_df.columns = ["has_ads.txt"]
    
    has_ads_txt_df.to_csv("has_ads_txt.csv")

    
    temp_series = pd.Series(has_ads_txt_df['has_ads.txt'].value_counts())
    temp_dict = pd.Series.to_dict(temp_series)
    
    ## Plot pie chart of has_ads_txt df
    plt.figure(1, figsize=(4,4))
    plt.pie([v for v in temp_dict.values()], None, [k for k in temp_dict], autopct='%.2f%%',colors=['silver', 'yellow'])  ##'%.2f%% is used to format data label'
    plt.title("Has ads.txt (%tage of publishers)")
    plt.show()
    
    return "File succesfully generated."

def runHasAdstxt(file, path, filter_status="limited", print_status=True):
    """
    The program can be run with 2 different value for the parameter 1) filter_status and 
    2) print_status. filter_status accepts either "limited" (will only return if a pub has
    ads.txt) or complete (will return if the pub has ads.txt + the values passed by ads.txt).
    print_status can be run with True or False. True will return the HTTP status of the 
    domain as the program sends a request. False will not.
    -----
   
    filter_status --> default to "limited"
    print_status --> default to "True"
    """
    list_domains = openFile(file)
    build_URL = createURLObjects(list_domains,path)
    
    return checkHasAdsFile(build_URL, filter_status, print_status)

print(runHasAdstxt('publisher_list.csv', '/ads.txt', filter_status="complete", print_status=False))