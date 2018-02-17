# Advertising Operation Algorithms


**Visit [TeddyCrepineau.com](http://teddycrepineau.com/) for more information**

Hello and welcome to the AdOps repository. This repository houses different useful program fo ad ops professionals. This is an ongoing project and the reporsitory will be updated on a regular basis.

As of today, the repository is comprised of:
- **[kmean algorithm:](https://github.com/TeddyCr/AdOps/tree/master/Domains_Clustering_Kmeans)** based on points and dimensions input in the template, the algorithms will cluster similar domains into k clusters where k is defined once difference in average distance of the points to their cluster is less than the thereshold.
- **[Uniform distribution of bid price / clearing price](https://github.com/TeddyCr/AdOps/tree/master/Exchange_win_clearing_price_ratio)**: this program calculates how bias exchanges are in their bid mechanisms by calculating the ratio of the user input bid prive over the exchange declared clearing price
- **[Check if publisher uses ads.txt](https://github.com/TeddyCr/AdOps/tree/master/has_ads.txt_scraper)**: this program runs through a list of domain names provided by the user and return 1) if the publisher uses the ads.txt or not, and 2) the values of the ads.txt file
- **[Check if exchanges domains are bought from match pub ads.txt file](https://github.com/TeddyCr/AdOps/tree/master/verify_inventory_ads.txt)**: this samll piece of program will scrap the /ads.txt page of a given list of domains, compare it to the domain/exchange pair from your DSP delivery and return any exchanges not listed on the ads.txt page by the publisher
