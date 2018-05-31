"""
K-MEANS CLUSTERING OF DOMAINS
=============================
-----------------------------

Author: Teddy Crepineau

----

Created on Tue Nov 14 09:30:35 2017
Latest Update: 11/29/2017

----

Purpose: This program is intended to cluster together similar domain names to facilitate execution and
optimization of campaigns. It is intended to be use against large amount of data. To cluster domains together,
we'll be using a k-mean algorythm (a basic machine learning algorythm used for unsupervised test).

Reference: https://en.wikipedia.org/wiki/K-means_clustering

Assumptions: A point is represented by a domain name, attributs are represented by values
associated with the domain name (IVT, Impressions, viewable impressions, etc.). Attributs will be normalized to 
mitigate the impact of 1 attribut over another

"""

import matplotlib.pyplot as plt
from collections import OrderedDict
import pylab
import random
import pandas as pd


class Points(object):
    """
    Define properties of the points (names, attributs, dimensionality, etc.)
    """
    ## Need to create objects based on domain names name (i.e. abc.com = Points(list_1, list_2))
    ## attributs need to be passed as pyla array
    
    def __init__(self, name, original_attributs, normalized_attributs = None):
        self.name = name
        if normalized_attributs == None:
            self.attributs = original_attributs
        else:
            self.attributs = normalized_attributs
        self.unnormalized_attributs = original_attributs
        
    def euclidianDistance(self, other):
        """
        calculate euclidian distance between 2 points
        """
        res = 0.0
        for i in range(self.dimensionality()):
            res += (self.attributs[i] - other.attributs[i])**2
        
        return res**0.5
    
    def dimensionality(self):
        return len(self.attributs)
    
    def getAttributs(self):
        return self.attributs
    
    def getOrginalAttributs(self):
        return self.unnormalized_attributs
    
    def getName(self):
        return self.name
    
    def __str__(self):
        return self.name


class Cluster(object):
    """
    Abstraction of a cluster for our k-means algorithm
    """
    ## This class should have objects composed of just points names (corresponding to 
    ## domain names). Points are in unique clusters at a time. 
    
    def __init__(self, points):
        self.points = points
        self.centroid = self.computeCentroid()
        
    def computeCentroid(self):
        dim = self.points[0].dimensionality()
        total_value = pylab.array([0.0]*dim)
        for p in self.points:
            total_value += p.getAttributs()
        
        centroid = Points('mean', total_value/len(self.points))

        return centroid
    
    def getCentroid(self):
        return self.centroid
    
    def update(self, points):
        old_centroid = self.getCentroid() 
        self.points = points
        
        if len(self.points) > 0:
            self.centroid = self.computeCentroid()
            return old_centroid.euclidianDistance(self.centroid) 
        else:
            return 0.0
        
    def members(self):
        for p in self.points:
            yield p
        
    def __str__(self):
        names = []
        for p in self.points:
            names.append(p.getName())
        names.sort()
        result = ''
        for p in names:
            result = result + p + ','
        return result[:-1]
            
    
    

def openFile(filename):
    """
    Load file and convert it to a panda dataframe. 
    """
    
    ## Data cleaning & normalization by using Pandas DataFrame
    ## --------------------------------------------------------
    
    input_file = pd.read_table(filename, sep=',') ## 1) Load file into a DataFrame
    input_file_no_na = input_file.dropna(axis=1, how='all') ## 3) Drops columns with only NaN

    input_file_no_na = input_file_no_na.groupby('DOMAINS', as_index=False).sum() ## 5) Add duplicate domains together

    len_init = len(input_file_no_na.columns.values)
    
    if 'BLOCK' in input_file_no_na.columns.values:
        input_file_no_na['BLOCK %'] = input_file_no_na['BLOCK']/input_file_no_na['REQUEST']

    if 'VIEWABLE' in input_file_no_na.columns.values:
        input_file_no_na['IN-VIEW %'] = input_file_no_na['VIEWABLE']/input_file_no_na['MEASURED']

    if 'CLICKS' in input_file_no_na.columns.values:
        input_file_no_na['CLICK %'] = input_file_no_na['CLICKS']/input_file_no_na['IMPRESSION']

    if 'INCIDENTS' in input_file_no_na.columns.values:
        input_file_no_na['INCIDENT %'] = input_file_no_na['INCIDENTS']/input_file_no_na['IMPRESSION']
        
    if 'COMPLETES' in input_file_no_na.columns.values:
        input_file_no_na['100% COMPLETES %'] = input_file_no_na['COMPLETES']/input_file_no_na['IMPRESSION']
    
    
    input_file_no_na = input_file_no_na.dropna()
    
   
    max_values = pd.Series(pd.DataFrame.max(input_file_no_na.iloc[:,len_init:])) ## 6) Store max values of of attributes to normalize data
    min_values = pd.Series(pd.DataFrame.min(input_file_no_na.iloc[:,len_init:])) ## 6') Store min values of of attributes to normalize data
    normalized_data = ((input_file_no_na.iloc[:,len_init:] - min_values) / (max_values - min_values)) ## 7) create new DataFrame with normalized values
    normalized_data.insert(loc=0,column='DOMAINS', value=input_file_no_na.iloc[:,0]) ## 8) Add domain names at the beginning of the new Data Frame 
    column_names = normalized_data.columns.values[1:]
    
    normalized_data = normalized_data.values ## convert object type from pd.df to np.array
    
    
    
    ## Put data into list and pass each list to functions to run our k-mean algorithm
    ## ------------------------------------------------------------------------------
    name = []
    attributs = []
    for i in range(len(normalized_data)):
        name.append(normalized_data[i][0])
        attributs.append(list(normalized_data[i][1:]))
    
    return name, attributs, column_names

def buildPoints(name, attributs):
    """
    Astract point by building points object from input data. Point objects are composed of:
       - names -> in our case domains
       - attributs -> vary depending on data input
    """
    
    points = []    
    for i in range(len(name)):
        point = Points(name[i], pylab.array(attributs[i]), normalized_attributs = None)
        points.append(point)
        
    return points

def runKmeans(points, k, cut_off, iterations):
    """"
    Runs the k-means algorithm
    """
    
    ## Initialize the algorithm by randomly picking intial centroid in Points
    initial_centroid = random.sample(points, k)
    
    ## Create an empty cluster and append k clusters composed of p initial point
    clusters = []
    
    for p in initial_centroid:
        clusters.append(Cluster([p]))
    
    
    ## Book keeping for while loop
    num_iterations = 0
    biggest_change = cut_off
    
    
    ## Iterate through Points,  assign each point to a cluster based on euclidian distance.
    ## Keeps iterating until either maximum of iteration is reached or biggest change in cluster
    ## centroid is lower than cut off
    while num_iterations <= iterations and biggest_change >= cut_off:
        new_cluster = []
        
        for i in range(k):
            new_cluster.append([])
            
        for p in points:
            smallest_distance = p.euclidianDistance(clusters[0].getCentroid())
            index = 0
            for i in range(k):
                distance = p.euclidianDistance(clusters[i].getCentroid())
                if distance < smallest_distance:
                    smallest_distance = distance
                    index = i
                    
            new_cluster[index].append(p)

        biggest_change = 0.0
        for i in range(len(clusters)):
            change = clusters[i].update(new_cluster[i])
            biggest_change = max(biggest_change, change)
        
        num_iterations += 1
     
    max_distance = 0.0
    
    for c in clusters:
        for p in c.members():
            if p.euclidianDistance(c.getCentroid()) > max_distance:
                max_distance = p.euclidianDistance(c.getCentroid())
                
    ## Calculate average distance between all points and their clusters
    cluster_total_value = 0.0
    for c in clusters:
        num_points = len(c.points)
        total_value = 0.0
        for p in c.members():
            total_value += p.euclidianDistance(c.getCentroid())
        cluster_total_value += total_value/num_points
            
    average_dist = cluster_total_value / len(clusters)

    
    return clusters, average_dist


def runTestKmeans(filename, k=0, cut_off=0, iterations=0, threshold=0):
    """
    Main function to run the k-means algorithm. Start with k=1 and run k-means algorithm until difference between average distance of point
    to their cluster is below threshold
    """
    
    domains, features, column_names = openFile(filename)
    points = buildPoints(domains, features)
    
    average_dist_list = []
    
    while len(average_dist_list) <= 1 or average_dist_list[-2] - average_dist_list[-1] >= threshold:
        k += 1
        clusters, average_dist = runKmeans(points, k, cut_off, iterations)
        average_dist_list.append(average_dist)
    
    plt.plot(average_dist_list, '-o')
    plt.xlabel("k")
    plt.ylabel('Average Distance')
    plt.show()
    return displayClusters(clusters, column_names)
    
    
    
def displayClusters(clusters, column_names):  
    """
    Function used to generate the excel files containing the clustered domains
    """
    
    final_clusters = []

    for i in range(len(clusters)):
        final_clusters.append([]) 
        
    for c in clusters:
        for p in c.members():
            final_clusters[clusters.index(c)].append((p.name, p.getAttributs()))
        
    for i in range(len(final_clusters)):
        temp = OrderedDict(final_clusters[i])
        df = pd.DataFrame.from_dict(temp, orient='index') ## convert dictionnary to a pd dataframe

        ## Calculate mean value for the cluster and add them at bottom of group
        mean_values = pd.Series(df.mean())
        df.loc["MEAN"] = mean_values    
        df.columns = [column_names]

        df_description = df.describe() ## create dataframe containing a description of the cluster dataframe
        
        ## Create a new file and write new sheets
        writer = pd.ExcelWriter('domains_cluster_' + str(i) + '.xls')
        df.to_excel(writer, "Domains_Group")
        df_description.to_excel(writer, "Group_Summary")
        writer.save()
    

    return "Your file(s) ha(s)(ve) been succesfuly generated" 
                    

print(runTestKmeans('clustering_template.csv', k=0, cut_off=0.0001, iterations=100, threshold=0.05))












