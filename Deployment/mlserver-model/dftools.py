# **A collection of useful basic functions for manipulating pandas dataframes.**  
# 
# Functionality includes (among others):
# - selecting DCS-bit on data or golden json data.
# - selecting specific runs, lumisections, or types of histograms


### imports

# external modules
import numpy as np

# local modules
from omstools import find_oms_attr_for_lumisections

# getter and selector for run numbers

def get_runs(df, runcolumn='run'):
    """
    Return a list of (unique) run numbers present in a df.
    """
    runlist = sorted(list(set(df[runcolumn].values)))
    return runlist

def select_runs(df, runnbs, runcolumn='run'):
    """
    Keep only a subset of runs in a df.
    """
    df = df[df[runcolumn].isin(runnbs)]
    df.reset_index(drop=True, inplace=True)
    return df


# getter and selector for lumisection numbers

def get_ls(df, lumicolumn='lumi'):
    """
    Return a list of ls numbers present in a df.
    Note: the numbers are not required to be unique!
    Note: no check is done on the run number!
    """
    lslist = sorted(list(df[lumicolumn].values))
    return lslist

def select_ls(df, lsnbs, lumicolumn='lumi'):
    """
    Keep only a subset of lumisection numbers in a df.
    Note: no check is done on the run number!
    """
    df = df[df[lumicolumn].isin(lsnbs)]
    df.reset_index(drop=True, inplace=True)
    return df
    
# functions to obtain histograms in np array format

def get_mes(df, datacolumn='data', xbinscolumn='xbins', ybinscolumn='ybins',
            runcolumn='run', lumicolumn='lumi',
            runs=None, lumis=None):
    """
    Get monitoring elements as a numpy array from a dataframe.
    Note: it is assumed that the df contains only one type of monitoring element!
    Note: for now only implemented for 2D monitoring elements!
    Input arguments:
    - df: dataframe
    - runs and lumis: 1D numpy arrays or lists (must be same length) with run and lumisection numbers to select
      (default: no selection is applied)
    Returns:
    - a tuple with the following elements:
      - numpy array of shape (number of instances, ybins, xbins) with the actual mes
      - numpy array of shape (number of instances) with run numbers
      - numpy array of shape (number of instances) with lumisection numbers
    """
    if runs is not None: df = select_runs(df, runs, runcolumn=runcolumn)
    if lumis is not None: df = select_ls(df, lumis, lumicolumn=lumicolumn)
    xbins = int(df[xbinscolumn].values[0])
    ybins = int(df[ybinscolumn].values[0])
    # note: df['data'][idx] yields an array of 1d arrays;
    # need to convert it to a 2d array with np.stack
    mes = np.array([np.stack(df[datacolumn].values[i]).reshape(ybins,xbins) for i in range(len(df))])
    runs = df[runcolumn].values
    lumis = df[lumicolumn].values
    return (mes, runs, lumis)


# advanced filtering

def filter_lumisections(run_numbers, ls_numbers,
        #entries = None,
        #min_entries_filter = None,
        oms_info = None,
        oms_filters = None,
        #hltrate_info = None,
        #hltrate_filters = None
        ):
    '''
    Helper function to filter_dfs that does not rely on the actual dataframes.
    Can also be used standalone as an equivalent to filter_dfs,
    if the dataframes are not available but the equivalent information is.
    Input arguments:
    - run_numbers and ls_numbers: equally long 1D numpy arrays with run and lumisection numbers.
    - entries: dict of the form {<ME name>: <array with number of entries>, ...}.
               note: the array with number of entries is supposed to correspond to
                     run_numbers and ls_numbers; maybe generalize later.
    - min_entries_filter: dict of the form {<ME name>: <minimum number of entries for this ME>}.
    '''

    # initializations
    filter_results = {}
    combined_mask = np.ones(len(run_numbers)).astype(bool)

    # OMS attribute filters
    if oms_filters is not None:
        for oms_filter in oms_filters:
            if len(oms_filter)==1:
                key = oms_filter[0]
                filterstr = key
                mask = find_oms_attr_for_lumisections(run_numbers, ls_numbers, oms_info, key).astype(bool)
            elif len(oms_filter)==3:
                key, operator, target = oms_filter
                filterstr = f'{key} {operator} {target}'
                values = find_oms_attr_for_lumisections(run_numbers, ls_numbers, oms_info, key)
                mask = eval(f'values {operator} {target}', {'values': values})
            else:
                raise Exception(f'Filter {oms_filter} not recognized.')
            # add to the total mask
            combined_mask = ((combined_mask) & (mask))
            # keep track of lumisections that fail
            fail = [(run, ls) for run, ls in zip(run_numbers[~mask], ls_numbers[~mask])]
            filter_results[filterstr] = fail

    # return results
    return (combined_mask, filter_results)
