# RemindMajorRevision

Enhanced version of the scripts for the human study about Rev Eng

# Setup

+ mkvirtualenv -ppython3.6 remind
+ pip install -r requirements.txt

# Usage

Depending on the analysis and the test to run, choose one or more of the following commands:

+ ./basic_blocks_analusis.py --function_time    [Avg time per function, Table 2]
+ ./basic_blocks_analysis.py --cfg              [CFG plot, useful for Figure 7]
+ ./basic_blocks_analysis.py --discarded_bbs    [Discarded BBs, useful for section 6.2]
+ ./birdseye_analysis.py --top_flop             [Top vs Flop, Figure 8]
+ ./birdseye_analysis.py --birdseye             [How many ppl use birdseye overview, 6.3]
+ ./function_analysis.py --strategy             [Strategy adopted to visit functions 6.2]
+ ./function_analysis.py --branch               [If users prefer true/false branch]
+ ./levels_analysis.py --levels                 [Figure 4, discuss with Simo]
+ ./levels_analysis.py --transitions            [Figure 10, discuss with Simo]
+ ./levels_analysis.py --sol_times              [Data of Section 6 (first part)]
+ ./levels_analysis.py --groups                 [Data of Section 6 (second part)]
+ ./levels_analysis.py --threshold              [Threshold used to separate Novices/Experts]
+ ./patterns_analysis.py                        [Figure 9, 11 and data of Sec 6.4]
+ ./speed_analysis.py                           [Section 6.5]

Moreover, you can run the following statistical tests:

+ ./levels_analysis.py --two_sample_test        [2-sample t-test to compare the averages of experts vs novices and confidence interval in milliseconds (Rev E)]
+ ./function_analysis.py --anova                [ANOVA test to see if strategies affect solution time (Rev E)] 
+ ./basic_blocks_analysis.py --statistics       [2-sample t-test to compare the time spent on useless paths for novices/experts (Rev E)]

# Feature plus: p-values correction

It is possible to correct the statistical tests with the Bonferroni method. Run these scripts as it follows:

+ ./levels_analysis.py --two_sample_test
+ ./basic_blocks_analysis.py --statistics
+ ./comments_analysis.py --comments
+ ./function_analysis.py --branch --anova
+ ./patterns_analysis.py --median_times --correlation_multiple_visits
+ ./speed_analysis.py --length_correlations
+ ./other_hp.py


# Collaboration

In the `pickle` directory, you can access two pickle files. 

1. users_data.p - it exports all the data related to ALL the users. Each user has a set of attributes to implement further analysis (level, solution_time, original_kind, redefined_kind, ...). More documentation in the related classes that you can find in the skeleton script that loads the pickle (```load_users_data.py```) that exists in the same directory

2. basic_blocks.p - it exports all the data related to ALL the BBs visits. In its essence it contains the different views separated by user for each single BB as well as some other info for the BB (e.g., in path, function that belongs to, ..). Again, classes are more documented but refer to the skeleton script to know which ones are useful to work with it.
