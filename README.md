# Effects of AI on Complexity and Maintainability
Authors: Elin Skånlund Berntsen & Simona-Ioana Culachi

### Project description
This is our code for the cource "Software Analytics" at University of Groningen in Spring 2026. Our goal was to analyze open-source repositories and see how AI-usages impacts code quality. In order to do this, we used a pre-exsisting data set, which covers self-admitted AI-usage in Open Source enviroments. Our results, including our genereated csv files and plots of the different metrics, is seen [here](csv/). 

Our chosen metrics is insertions, deletions, lines, files, cyclomatic complexity, number of reverted commits, number of failed pipelines, changes in same function after 30 days and duplication percentage. 

### Running Instructions
#### Requirements
Before running the code, it is crucial to set up the proper enviroment. In order to do this, you must first set up a virtual enviroment then run:
```bash
pip install -r requirements.txt
```

It is also required to have a GitHub token to run the code properly. To this, you must [create a personal access token](https://github.com/settings/tokens) and add in a **.env** file under the name *GITHUB_TOKEN*. 


#### Extracting data and metrics
The code is created to be relatively modular and easy to run.

In order to get the data from the repositories, you only need to run: 
```bash
python3 data_extraction.py
```
This code reads the AI commits from the pre-exsiting data set, get the start/end date of said commits and then gets all commits in this time frame. After this, it retrives all of the metrics mentioned. 

It is important to note that this takes a while, especially for repositories that are relatively large. The code is set up in a way so that it also removes the outliers. The final result will be saved in a file called **cleaned_dataset_AI.csv** and **cleaned_dataset_nonAI.csv**. Both of these will be automatically placed in **cvs/{language}/{repo_name}/**.

To change which repository/repositories are analyzed, simply change the list on line 16 in [data_extraction.py](data_extraction.py) and the language on line 14.

In order to get the cyclomatic complexities, simply run
```bash
python3 cyclomatic_complexity
```
It is important to note that this should be ran after you've ran the data extraction, as it builds on the produced data sets. Here you need to change the path at the top if you want to anallyze other repositories. 

#### Plot results and statistical tests
To get the result of all of the metrics, run 
```
python3 plots.py
```
This automatically scans the [csv directory](csv/) and retrives the plots and averages. These are saved in the repositories own results folder, along a summary file that saves data (such as mean of the different values).

To run the statistical tests just run

```
python3 stats_complexity.py
```
and 
```
python3 stats_maintainablilty.py
```

