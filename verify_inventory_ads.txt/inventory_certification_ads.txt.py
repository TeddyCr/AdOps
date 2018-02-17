# -*- coding: utf-8 -*-
"""
Purpose: This program is intended to automatically validate traffic source from SSP by comparing from what exchanges domains where bought
Copyright: GNU General Public License v3.0
"""

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class FileOperation(object):
    """
    Execute operation on template files (open, clean data, create file etc.)
    """
    
    def __init__(self, file):
        self.file = file
        
    def myDataFrame(self):
        """
        return unduplicated dataframe
        """
        return self.buildDataFrame()
        
    def buildDataFrame(self):
        """
        Convert .csv file to a panda dataframe + remove duplicated values
        """
        df = pd.read_csv(self.file, skip_blank_lines=True) #convert .csv file to a df while skipping blank lines
        df = pd.DataFrame.drop_duplicates(df)  #drop duplicates
        df = df.reset_index(drop=True)
        return df
        

class DomainOps(object):
    """
    Perform operations (parse ads.txt page) on list of domains from dataframe
    """
    def __init__(self, url):
        self.url = url
        
    def fullURL(self):
        return self.buildURL()
        
    def buildURL(self):
        """
        Build ads.txt to use to fetch webpage
        """
        return 'https://' + self.url + '/ads.txt'
    
    def requestURL(self):
        session = requests.Session()
        retry = Retry(connect = 1, backoff_factor = 0.1)
        adapter = HTTPAdapter(max_retries = retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)'}

        return session.get(self.fullURL(), headers = headers)
    
    def statusCode(self):
        if self.requestURL().status_code == 404:
            return False
        else:
            return True
            
        
    def pageContent(self):
        return self.requestURL().text
    
    def pageContentBinary(self):
        return self.requestURL().content
    
    def __str__(self):
        return str(self.url)
    
def csvToDF(file):
    """
    Open the template file containing domains + exchanges served on and transform it into a pandas dataframe.
    This file contain the data that needs to be verified against the ads.txt file.
    """
    df = FileOperation(file).myDataFrame()
    return df
    
def dataFetching(dataframe):
    """
    Fetch data from the ads.txt page of the list of domains and put data in new df
    """
    domains_df = pd.DataFrame.drop_duplicates(dataframe, subset='DOMAINS')
    domains_df = domains_df.reset_index(drop=True)
    dict_values = {}
    for index, row, in domains_df.iterrows():
        try:
            domain = DomainOps(row[0])
            print('Fetching: ', domain)
            if domain.statusCode():
                r = domain.pageContent() #Fetch URL and returns page content -> type = string (use 'pageContentBinary" for binary)
                r = r.replace(',',' ') #Remove comas
                r = [tuple(line.split()) for line in r.splitlines() if "#" not in line] #Each line will be put in a tuple and a list [(line1), (line2)]
                ads_txt_df = pd.DataFrame.from_records(r) #Transfer list into df
                df_exchanges = ads_txt_df[0]
                df_exchanges = pd.Series.drop_duplicates(df_exchanges).reset_index(drop=True)
                df_exchanges = pd.Series.tolist(df_exchanges)
                dict_values[str(domain)] = df_exchanges
            else:
                pass
        except requests.exceptions.ConnectionError:
            pass

    return dict_values

def dataVerification(initial_data, verification_data):
    """
    This function check the data the user wants to verify against the source data from the domain
    """
    df_to_dict = {k: list(v) for k,v in initial_data.groupby("DOMAINS")["EXCHANGES"]}
    res = {}
    for key, value in df_to_dict.items():
        res[key] = [value for value in df_to_dict[key] if key in verification_data and value.lower() not in verification_data[key]]
    
    
    return res
    
def main(file):
    initial_data = csvToDF(file)
    exchange_list = dataFetching(initial_data)
    non_matches = dataVerification(initial_data, exchange_list)
    
    return non_matches

print(main("domain_exchange_list.csv"))













































