# Pyhton 3.6
"""
Created on Fri Nov  3 19:52:49 2017
@author: tcrepineau

Purpose: this program is intended to check if SSPs run true second price auctions. 

Methodology: we will plot a graph of the ration of the win bid and the max bid in the x-axis 
the percentage of impressions in the y-axis.

Assumptions: in a true second price auction, the probability of the win bid to be equal to the max bid
is (1/[b - a]) where b represents the higher bound of possible bids (i.e if max bid = $4, possible bids 
are 400), and a the minimum possibility of bids (i.e 0.01).

Data: TBD  
"""

import matplotlib.pyplot as plt
from collections import defaultdict
import random as rd
import numpy as np
import scipy
from scipy.stats import chisquare

IMPRESSIONS = 0
COST = 1
MAX_BID_UI = 2
RATIO = 3


def loadDataFile(filename):
    """Return a dictionnary mapping every instance of exchange to (impressions, cost, max_bid_ui), where
    exchange is a string impressions is an integer, and cost and max_bid_ui are float rounded to 2 decimals
    in a tuple. Each line in the file represent a specific instance of an impression occurring [ideally] 
    occuring in an exchange"""
    
    exchange_data_info = defaultdict(list)
    inputFile = open(filename)
    for line in inputFile.readlines()[1:]: #[1:] Skips header row
        xid, exchange, impressions, cost, max_bid_ui = line.split(',')
        exchange_data_info[exchange].append((int(impressions), float(cost),float(max_bid_ui)))
    
    return exchange_data_info


class noExchange(Exception):
    """Raise no exchange if value enter as an exchange filter is not found in the dataset"""
    def __init__(self,data_list_exchange):
        self.data_list_exchange = data_list_exchange
    
    def __str__(self):
        error_message = 'You have entered an incorrect exchange name. Please be sure to pick one from the following list: '
        exchange_list = []
        for k,v in self.data_list_exchange.items():
            exchange_list.append(k)
        
        error_message = error_message + ', '.join(exchange_list)
        
        return error_message
            
        
    

class pickExchange(object):
    """This class is used to filter SSPs and run test on 1 specific SSP at a time"""
    
    ##Initialize data
    def __init__(self, data_list, exchange):
        self.data_list = data_list
        self.exchange = exchange
    
    ##Iterate through data list and add key corresponding to SSP chosen to new dict. {filtered_data_list}
    ##k = keys in dict. (i.e exchanges) & v = values in dict. (i.e a tuple of (impressions,cost,max_bid_uI))
    def filterExchange(self):
        for k, v in self.data_list.items():
            if self.exchange == None:
                return self.data_list
            if k.lower() == self.exchange.lower():
                return {k: self.data_list[k]}
            if self.exchange not in self.data_list:
                raise noExchange(self.data_list)
    
    ##Call def filterExchange(self) method to filter data based on SSP chosen
    def getFilteredExchange(self):
        return self.filterExchange()
        
 
class bidsRatio(object):
    """This class compute the ratio of win bid over the max bid entered"""
    
    ## Initialize data
    def __init__(self, data_set):
        self.data_set = data_set
    
    ##Compute the ratio of max bid over win bid and create a new dictionnary with initial value + ratio
    ## key = exchange & value = tuple containing impressions, max_bid_ui, cost, ratio_win_max    
    def computeRatio(self):
        dict_with_ratio = {}
        for k,v in self.data_set.items():
            for i in range(len(v)):
                ratio_win_max = v[i][COST]/v[i][MAX_BID_UI]
                v[i] = v[i] + (ratio_win_max,)
            
            dict_with_ratio[k] = v
            
        return dict_with_ratio
    
    ##Call def computeRatio(self) and return the computed ratio
    def getRatio(self):
        return self.computeRatio()
    
class observedData(object):
    """Take observed value and expected values and calculate chi square"""
    
    def __init__(self, observed_data_distribution, observed_bins):
        self.observed_data = observed_data_distribution
        self.observed_bins = observed_bins
        
    def getObservedDist(self):
        return self.observed_data
    
    def getObservedBins(self):
        return self.observed_bins
        
class expectedData(object):
    """Take observed value and expected values and calculate chi square"""
    
    def __init__(self, random_data_distribution, random_bins):
        self.random_data_distribution = random_data_distribution
        self.random_bins = random_bins
        
    def getRandomDist(self):
        return self.random_data_distribution
    
    def getRandomBins(self):
        return self.random_binst
    
    def computeDistributionRatio(self):
        expected_dist_ratio = []
        for i in range(len(self.random_data_distribution)):
            temp = self.random_data_distribution[i]/sum(self.random_data_distribution)
            expected_dist_ratio.append(temp)
        
        return expected_dist_ratio
    
    def getRatioDistribution(self):
        return self.computeDistributionRatio()
                    
    
    
def runAuctionTest(filename, exchange = None):
    inputData = loadDataFile(filename)
    filtered_input_data = pickExchange(inputData, exchange).getFilteredExchange()
    compute_ratio_list = bidsRatio(filtered_input_data).getRatio()
    
    return plotGraph(compute_ratio_list, exchange)
    
    
def plotGraph(final_data_set, exchange):
    ratios = []
    bins = []
    for k,v in final_data_set.items():
        for i in range(len(v)):
            #ratios.append(v[i][RATIO])
            ratios += v[i][IMPRESSIONS] * [(v[i][RATIO])]
    
    for i in np.arange(0.0,1.0,0.01):
        bins.append(round(i,2))
    
    distribution_ob, bins_ob, bars_ob = plt.hist(ratios, bins, histtype='bar', rwidth=0.9, label=exchange)
    plt.xlabel('Ratios')
    plt.ylabel('% Impressions')
    plt.title('True 2nd Price Auction')
    plt.legend()
    plt.show()
    
    #Compute mean and standard deviation    
    mean_ratio = sum(ratios) / len(ratios)
    st_dev = np.std(ratios)
    
    print('Mean :', mean_ratio)   
    print('Standard Deviation: ', st_dev)
    
    observed_data = observedData(distribution_ob, bins_ob)
    sum_tot_values = sum(observed_data.getObservedDist())
    sum_tot_values = int(sum_tot_values)
    
    return calculateChiSquare(observed_data.getObservedDist(), generateRandomTest(sum_tot_values, 4.0))


def generateRandomTest(number_bids, higher_bound_bid, run_random=False):
    """Generate random ratio to evaluate what distribution under total random conditions.
    higher_bound_bid is a float"""
    bins = []
    random_ratios = []
    
    for i in np.arange(0.0,1.0,0.01):
        bins.append(round(i,2)) 

    for i in range(number_bids):
        max_bid_rd = rd.uniform(0.01, higher_bound_bid)
        clearing_price = rd.uniform(0.01, max_bid_rd - 0.01) + 0.01
        ratio = clearing_price/max_bid_rd
        random_ratios.append(ratio)

    distribution_exp, bins_exp, bars_epx = plt.hist(random_ratios, bins, normed=True,histtype='bar', rwidth=0.9,label='Random Data Set')
    mean_ratio = sum(random_ratios) / len(random_ratios)
    st_dev = np.std(random_ratios)
    
    if run_random == True:        
        plt.xlabel('Ratios')
        plt.ylabel('% Impressions')
        plt.text(0,0.8,round(mean_ratio,2),
                 bbox={'facecolor':'white', 'alpha':0.8,})
        plt.text(0,0.72,round(st_dev,2),
                 bbox={'facecolor':'white', 'alpha':0.8,})
        plt.title('Random 2nd Price Auctions')
        plt.legend()
        plt.show()
        
        expected_data = expectedData(distribution_exp, bins_exp)
        observed_data = observedData(distribution_exp, bins_exp)
        
        print('Mean :', mean_ratio)   
        print('Standard Deviation: ', st_dev)
        
        return calculateChiSquare(observed_data.getObservedDist(),expected_data.getRatioDistribution())
    
    else:
        #Compute mean and std for random set        
        expected_data = expectedData(distribution_exp, bins_exp)
        return expected_data.getRatioDistribution()

def calculateChiSquare(observed_data, expected_ratio):
    tot_observed_data = sum(observed_data)
    tot_observed_data = int(tot_observed_data)
    
    expected_data = []
    for i in range(len(observed_data)):
        expected_data.append(tot_observed_data*0.01)
        
    return chisquare(observed_data, f_exp=expected_data)
    