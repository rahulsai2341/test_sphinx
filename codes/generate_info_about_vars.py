# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 16:39:23 2019

@author: prudhvee.sadha

@edited by: Sai Rahul Kasula
on : 11-06-2019
"""

import pandas as pd
import numpy as np
import statistics as st
from pathlib import Path    

def generate_percentiles_for_numericals(df, numerical_columns, folder, filename, cols_type):
    """
    Fucntion to generate analysis for numerical parameters
    
    Parameters
    ----------
        df : dataframe consisting of numerical variables
        numerical_columns : List of numerical variables
        folder : Folder path to place the file
        filename: name of the file
        cols_type: Type to indicate type of data (prop/intraop)
    
    Returns
    -------
    None
    """
    variables = []
    minimum = []
    maximum = []
    quarter_percentile = []
    median = []
    three_quarters_percentile = []
    average = []
    var = []
    
    #convert the column names to lower case
    var_columns = pd.Series(list(df.columns))
    var_columns = var_columns[var_columns.isin(numerical_columns)]

    df = df[var_columns]
    
    for name, values in df.iteritems():
        # Convert the values to numeric. The strings are converted to NaN and are dropped
        values = pd.to_numeric(values, downcast='float',errors='coerce').dropna().tolist()
        average.append(st.mean(values))
        var.append(st.stdev(values))
        percentiles = np.percentile(values, [25, 50, 75])
        minimum.append(min(values))
        maximum.append(max(values))
        variables.append(name)
        quarter_percentile.append(percentiles[0])
        median.append(percentiles[1])
        three_quarters_percentile.append(percentiles[2])
    percentile_data = {'Variable': variables,
                       '25th Percentile': quarter_percentile,
                       'Median': median,
                       '75th Percentile': three_quarters_percentile,
                       'Minimum':minimum,
                       'Maximum': maximum,
                       'mean': average,
                       'SD': var}
    percentiles_df = pd.DataFrame(percentile_data)
    
    output_dir = Path(out_dir+'\\'+cols_type+'\\'+folder)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = filename+'.csv'
    percentiles_df.to_csv(output_dir/output_file, index=False)
    

def generate_vars_info(data, cols, folder, filename, cols_type):
    """
    Fucntion to generate analysis for binary and categorical parameters
    
    Parameters
    ----------
        df : pandas.DataFrame 
            dataframe consisting of numerical variables
        cols : list
            List of binary or categorical variables
        folder : String
            Folder path to place the file
        filename: String
            name of the file
        cols_type: String
            Type to indicate type of data (prop/intraop and binary/categorical)
    
    Returns
    -------
	
	Notes
    -----
		Flow chart for this function:
			.. image:: flow_charts/test.png
    """
    var_columns = pd.Series(list(data.columns))
    var_columns = var_columns[var_columns.isin(cols)]
    
    data = data[var_columns]
    total = len(data)
    variables = []
    number = []
    category = []
    percentage = []
    
    for name, values in data.iteritems():
        for val, num in values.value_counts().iteritems():
            variables.append(name)
            category.append(val)
            number.append(num)
            percentage.append('{0:.2f}%'.format((float(num)/float(total)) * 100))
        
        
    generated_data = {'Variable': variables, 'Categories':category, 'Number': number, 'Percentage': percentage}
    generated_df = pd.DataFrame(generated_data, columns = ['Variable','Categories','Number','Percentage'])
    
    output_dir = Path(out_dir+'\\'+cols_type+'\\'+folder)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = filename+'.csv'
    generated_df.to_csv(output_dir/output_file, index=False)


def analyze_data_preop(train_cohort, test_cohort):
    """
    Helper function to generate analysis for all preop variables
    
    Parameters
    ----------
        train_cohort : pandas.DataFrame
            Dataframe for training cohort
        test_cohort : pandas.DataFrame
            Dataframe for test cohort
    Returns
    -------
    None
    """
    cohorts = {'train':train_cohort, 'test':test_cohort}
    complications = ['sepsispred','mvcomppred','neurodelpred','icucomppred']
    for cohort, data in cohorts.items():
        for complication in complications:
            generate_vars_info(data, categorical_vars, cohort+'\\'+complication,'Analyzed_data_all', r'preop/categorical')
            generate_vars_info(data, binary_vars, cohort+'\\'+complication,'Analyzed_data_all', r'preop/binary')
            generate_percentiles_for_numericals(data, numerical_vars, cohort+'\\'+complication,'Analyzed_data_all', r'preop/numerical')
            for outcome in range(2):
                data_outcome = data[data[complication]==outcome]
                generate_vars_info(data_outcome, categorical_vars, cohort+'\\'+complication,'Analyzed_data_'+str(outcome), r'preop/categorical')
                generate_vars_info(data_outcome, binary_vars, cohort+'\\'+complication,'Analyzed_data_'+str(outcome), r'preop/binary')
                generate_percentiles_for_numericals(data_outcome, numerical_vars, cohort+'\\'+complication,'Analyzed_data_'+str(outcome), r'preop/numerical')

def generate_preop_analysis():
    """
    Function to generate analysis for all preop variables
    
    Parameters
    ----------
    None
    Returns
    -------
    None
    """
    # Read the file and pre-process it
    df = pd.read_csv(in_dir+r'\preop\All_generated_variables.csv', encoding='latin-1', index_col=False)
    df.anesthesia_start_datetime=pd.to_datetime(df.anesthesia_start_datetime)
    df = df.rename(columns={'sched_start_time':'sched_start_datetime'})
    # Read outcomes file
    outcomes = pd.read_csv(in_dir+r'\preop\outcome_final_modified_0905.csv')
    outcomes = outcomes[['encounter_deiden_id', 'sched_start_datetime','sepsis', 'ICU_gt_2d', 'mv_greater_2days', 'neuro_delirium_comb']]
    col_map = {'sepsis':'sepsispred','mv_greater_2days':'mvcomppred',
               'neuro_delirium_comb':'neurodelpred','ICU_gt_2d':'icucomppred'}
    outcomes = outcomes.rename(columns=col_map)
    
    # Merge outcomes with generated variables
    generated_variables_with_outcomes = df.merge(outcomes, on=['encounter_deiden_id', 'sched_start_datetime'], how='left')
    generated_variables_with_outcomes = generated_variables_with_outcomes[generated_variables_with_outcomes['anesthesia_start_datetime']>'2014-06-01 00:00:00']
    #generated_variables_with_outcomes.to_csv(out_dir+r'/generated_variables_with_outcomes.csv', index=False)
    
    # Divide data into training and test set
    train_cohort = generated_variables_with_outcomes[(generated_variables_with_outcomes['anesthesia_start_datetime']<'2018-03-01 00:00:00') & 
                                                     (generated_variables_with_outcomes['anesthesia_start_datetime']>='2014-06-01 00:00:00')]
    train_cohort = train_cohort[train_cohort.duplicated()==False]
    test_cohort = generated_variables_with_outcomes[(generated_variables_with_outcomes['anesthesia_start_datetime']>='2018-03-01 00:00:00')&
                                                    (generated_variables_with_outcomes['anesthesia_start_datetime']<='2019-03-02 00:00:00')]
    test_cohort = test_cohort[test_cohort.duplicated()==False]
    
    # Analyze data
    analyze_data_preop(train_cohort, test_cohort)

def generate_intraop_analysis():
    """
    Function to generate analysis for all intraop variables
    
    Parameters
    ----------
    None
    Returns
    -------
    None
    """
    filenames = ['ICU_duration', 'MV_duration', 'sepsis', 'neuro_delirium_comb']
    cohorts = ['development', 'test']
    for filename in filenames:
        for cohort in cohorts:
            name = r'\IntraOp_full_' + filename + '_' + cohort + '_cohort.csv'
            df = pd.read_csv(in_dir+r'\intraop'+name)
            df = df.select_dtypes(['number'])
            df = df.drop('patient_deiden_id', axis=1)
            intraop_numerical_vars = list(df.columns)
            generate_percentiles_for_numericals(df, intraop_numerical_vars, cohort+'\\'+filename,'Analyzed_data_all', r'intraop/numerical')
            for outcome in range(2):
                temp_df = df[df['outcome']==outcome]
                generate_percentiles_for_numericals(temp_df, intraop_numerical_vars, cohort+'\\'+filename,'Analyzed_data_'+str(outcome), r'intraop/numerical')
     

'''in_dir = r'S:\2016_223 IDEALIST\4 PROJECTS\ARCHIVED\Archived Users\Rahul\data_analysis\data'
out_dir = r'S:\2016_223 IDEALIST\4 PROJECTS\ARCHIVED\Archived Users\Rahul\data_analysis\results\new'

# Get list of al variables
variable_info = pd.read_csv(in_dir+r'\Idealist_feature_list.csv', index_col=False)

# Divide the variables into categories
numerical_vars = variable_info.loc[variable_info['feature_type'] == 'num']
numerical_vars = numerical_vars['feature_name']
categorical_vars = variable_info.loc[variable_info['feature_type'] == 'cat']
categorical_vars = categorical_vars['feature_name']
binary_vars = variable_info.loc[variable_info['feature_type'] == 'bin']
binary_vars = binary_vars['feature_name']

# Analyze preop variables
# generate_preop_analysis()

# Analyze IntraOp variables
generate_intraop_analysis()'''


