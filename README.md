# epiDAMIK20-COVID

This repository includes the code for our working paper "Effectiveness and Compliance to Social Distancing DuringCOVID-19". In order to run the code you will need to request and download the data from SafeGraph (https://www.safegraph.com/covid-19-data-consortium). 

## Granger causality

In order to perform the granger causality analysis the following two scripts are used: 

<B>preprocess_granger.py</B>: This script processes the SafeGraph mobility and covid-19 related fatality data from NYT and provides a data frame with the average fraction of daily time spent home over each week and the total number of COVID-19 related deaths. The output from this script is ```granger_ts.csv```, which is the input to the next script.

<B>granger_analysis.Rmd</B>: This is an R markdown that reads the weekly time-series data obtained from the previous script and runs the Granger causality analysis. 

## Demographics analysis with beta regression

We again have two scripts; one for preprocessing the data and one for running the beta regression. 

<B>preprocess_demographics.py</B>: This script processes the SafeGraph mobility data and obtains for each census block group the median percentage of time spent at home for each day in February (pre-lockdown) and April (during lockdown). It creates a an output file ```epiDAMIK_home_pcg.csv``` that has for each census block group (row), the median percentage of time spent home for each day (column). This script also obtains demographic information for each census block group (output files: ```demo_dataage.csv``` and ```demo_datarace.csv```). 
