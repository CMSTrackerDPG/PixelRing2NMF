import sys
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from pyarrow.parquet import ParquetFile
from pyarrow.parquet import ParquetDataset

################################################################################
#######                            Constants                              ######
################################################################################

optimized_powerGroupStringsList = np.array(['FPix_BmO_D3_ROG4','FPix_BmO_D2_ROG4','FPix_BmO_D1_ROG4','FPix_BmO_D3_ROG3','FPix_BmO_D2_ROG3','FPix_BmO_D1_ROG3','FPix_BmO_D3_ROG2','FPix_BmO_D2_ROG2','FPix_BmO_D1_ROG2','FPix_BmO_D3_ROG1','FPix_BmO_D2_ROG1','FPix_BmO_D1_ROG1','FPix_BmI_D3_ROG1','FPix_BmI_D2_ROG1','FPix_BmI_D1_ROG1','FPix_BmI_D3_ROG2','FPix_BmI_D2_ROG2','FPix_BmI_D1_ROG2','FPix_BmI_D3_ROG3','FPix_BmI_D2_ROG3','FPix_BmI_D1_ROG3','FPix_BmI_D3_ROG4','FPix_BmI_D2_ROG4','FPix_BmI_D1_ROG4','FPix_BpO_D1_ROG4','FPix_BpO_D2_ROG4','FPix_BpO_D3_ROG4','FPix_BpO_D1_ROG3','FPix_BpO_D2_ROG3','FPix_BpO_D3_ROG3','FPix_BpO_D1_ROG2','FPix_BpO_D2_ROG2','FPix_BpO_D3_ROG2','FPix_BpO_D1_ROG1','FPix_BpO_D2_ROG1','FPix_BpO_D3_ROG1','FPix_BpI_D1_ROG1','FPix_BpI_D2_ROG1','FPix_BpI_D3_ROG1','FPix_BpI_D1_ROG2','FPix_BpI_D2_ROG2','FPix_BpI_D3_ROG2','FPix_BpI_D1_ROG3','FPix_BpI_D2_ROG3','FPix_BpI_D3_ROG3','FPix_BpI_D1_ROG4','FPix_BpI_D2_ROG4','FPix_BpI_D3_ROG4'])
#A list of all of the quarters of the detector
QUARTERS = np.array([['FPix_BmI_D3_ROG1','FPix_BmI_D3_ROG2','FPix_BmI_D3_ROG3','FPix_BmI_D3_ROG4','FPix_BmI_D2_ROG1','FPix_BmI_D2_ROG2','FPix_BmI_D2_ROG3','FPix_BmI_D2_ROG4','FPix_BmI_D1_ROG1','FPix_BmI_D1_ROG2','FPix_BmI_D1_ROG3','FPix_BmI_D1_ROG4'], ['FPix_BmO_D3_ROG1','FPix_BmO_D3_ROG2','FPix_BmO_D3_ROG3','FPix_BmO_D3_ROG4','FPix_BmO_D2_ROG1','FPix_BmO_D2_ROG2','FPix_BmO_D2_ROG3','FPix_BmO_D2_ROG4','FPix_BmO_D1_ROG1','FPix_BmO_D1_ROG2','FPix_BmO_D1_ROG3','FPix_BmO_D1_ROG4'], ['FPix_BpI_D1_ROG1','FPix_BpI_D1_ROG2','FPix_BpI_D1_ROG3','FPix_BpI_D1_ROG4','FPix_BpI_D2_ROG1','FPix_BpI_D2_ROG2','FPix_BpI_D2_ROG3','FPix_BpI_D2_ROG4','FPix_BpI_D3_ROG1','FPix_BpI_D3_ROG2','FPix_BpI_D3_ROG3','FPix_BpI_D3_ROG4'], ['FPix_BpO_D1_ROG1','FPix_BpO_D1_ROG2','FPix_BpO_D1_ROG3','FPix_BpO_D1_ROG4','FPix_BpO_D2_ROG1','FPix_BpO_D2_ROG2','FPix_BpO_D2_ROG3','FPix_BpO_D2_ROG4','FPix_BpO_D3_ROG1','FPix_BpO_D3_ROG2','FPix_BpO_D3_ROG3','FPix_BpO_D3_ROG4']])


################################################################################
#######                        Data Extraction                            ######
################################################################################

#Return all of the available runs
def extract_runs(file):
    #Take in a .parquet data file containing a pandas dataframe of runs/lumis
    #and return all of the available runs        
    df = ParquetDataset(file).read().to_pandas()
    
    return df['run_number'].unique()

def extract_data_2d(file, run_number, lumi_number):
    #Take in a .parquet data file containing a pandas dataframe of runs/lumis
    #and return the 2D array of data from that specific run/lumi number
    #ALSO return the number of xbins and ybins
    
    #Filters to pass into the pandas dataframe
    filters = []
    filters.append( ('run_number', '=', run_number) )
    filters.append( ('ls_number', '=', lumi_number) )
    
    df = ParquetDataset(file, filters=filters).read().to_pandas()
    #For some reason the x/y bins are floats, not integers
    xbins = int(df['x_bin'][0])
    ybins = int(df['y_bin'][0])
    
    #Since we are only looking at ONE run_number, hists is just an array of length one
    hists = np.array(df['data'])
    runs = np.array(df['run_number'])
    lumis = np.array(df['ls_number'])
    
    #Extract the data in the required way
    data = np.stack(hists[0])
    
    return data

#Take in the oms_json file and the specific run number we want to check the DCS flags for
def check_DCS_flags(oms_json, run_number):
    #Turn the json file into a python dictionary
    with open(oms_json, 'r') as f:
        oms_filters = json.load(f)
    filter_keys = [
        'run_number',
        'lumisection_number',
        "beams_stable",
        "cms_active",
        "bpix_ready",
        "fpix_ready",
        "tibtid_ready",
        "tob_ready",
        "tecp_ready",
        "tecm_ready"
    ]
    oms_filters = {key: val for key, val in oms_filters.items() if key in filter_keys}
    #Then turn the dictionary into a dataframe and extract just the desired run number
    df = pd.DataFrame.from_dict(oms_filters)
    run_df = df[df['run_number'] == run_number]
    #Then apply the run number and DCS flags. If ANY are False, then mark as bad
    failed_lumis_df = run_df[(run_df["beams_stable"] == False) | (run_df["cms_active"] == False) |
                          (run_df["bpix_ready"] == False) | (run_df["fpix_ready"] == False) |
                          (run_df["tibtid_ready"] == False) | (run_df["tob_ready"] == False) |
                          (run_df["tecp_ready"] == False) | (run_df["tecm_ready"] == False)]
    #Then extract the bad lumisections
    bad_lumis = failed_lumis_df['lumisection_number'].values
    #Extracting the bad lumisections since there are hopefully LESS bad lumisections, so the 
    #Parquet filter can work less
    return bad_lumis

#TODO: Research how the filters work and see 
#how to exclude single lumisections and sequences of lumis
def extract_data_2d_multi_lumis(file, run_number, lumi_start, lumi_end):
    #Take in a .parquet data file containing a pandas dataframe of runs/lumis
    #and return the 2D array of data from that specific run
    #from INCLUSIVE range lumi_start to lumi_end
    
    #Filters to pass into the pandas dataframe
    filters = []
    filters.append( ('run_number', '=', run_number) )
    filters.append( ('ls_number', '>=', lumi_start) )
    filters.append( ('ls_number', '<=', lumi_end))
    
    df = ParquetDataset(file, filters=filters).read().to_pandas()
    #print(df.head())
    #For some reason the x/y bins are floats, not integers
    xbins = int(df['x_bin'][0])
    ybins = int(df['y_bin'][0])
    
    #Since we are only looking at ONE run_number, hists is just an array of length one
    hists = np.array(df['data'])
    runs = np.array(df['run_number'])
    lumis = np.array(df['ls_number'])
    #print("EXTRACTED LUMISECTIONS: ", lumis)
    
    #Extract the data in the required way
    #print(hists.shape)
    data = np.stack(hists)
    #print(data.shape)
    #Sadly, stack, dstack, vstack, and hstack don't seem to work on the second (92 length) dimension. 
    #Even with the axis parameter, I can't seem to find a way to stack the xbins object into
    #a fully 3D array. So we have to follow Luka and loop over each lumisection. 
    #Luckily this doesn't seem to add much time
    #be careful to iterate over the length of the lumi array, not lumi_end-lumi_start+1, since we could be missing lumis. 
    #Lumisections w/o data are not saved into the parquet file (eg. 2024EraC Ring 1 Run 380043 LS 353-355)
    data2 = np.array([np.stack(data[i]) for i in range(len(lumis))])

    #print("Returned Data Shape: ", data2.shape)
    #Return the data and an array of the lumisections found
    return data2, lumis

#TODO: Research how the filters work and see 
#how to exclude single lumisections and sequences of lumis
#The way we exclude single runs and sequences of runs is by adding the optional extra_filters parameter
#Pass in filters in an array in the form [('ls_number', '!=', 12345), ('ls_number', '>', 56789)]
def extract_data_2d_all_lumis(file, run_number, oms_json=None, extra_filters=None):
    #Take in a .parquet data file containing a pandas dataframe of runs/lumis
    #and return the 2D array of data from that specific run
    #with ALL lumisections
    
    #Filters to pass into the pandas dataframe
    filters = []
    filters.append( ('run_number', '=', run_number) )
    #Sometimes we need to add extra filters to exclude single runs or sequences of runs
    if extra_filters != None:
        for extra_filter in extra_filters:
            filters.append(extra_filter)

    #Filter for the lumisections which pass the DCS flags
    if oms_json != None:
        bad_lumis = check_DCS_flags(oms_json, run_number)
        #bad lumis is just a python list. So sadly we have to add an individual filter for each bad lumisection
        #This is why I chose check_DCS_flags() to return a list of BAD lumisections
        for bad_ls in bad_lumis:
            filters.append( ('ls_number', '!=', bad_ls) )
    
    
    df = ParquetDataset(file, filters=filters).read().to_pandas()
    #print(df.head())
    #After filtering with the OMS JSON, the dataframe can be empty
    if df.empty:
        return np.empty(0), np.empty(0)
    #Just return two empty arrays? Don't want to raise an exception
    
    #For some reason the x/y bins are floats, not integers
    xbins = int(df['x_bin'][0])
    ybins = int(df['y_bin'][0])
    
    #Since we are only looking at ONE run_number, hists is just an array of length one
    hists = np.array(df['data'])
    runs = np.array(df['run_number'])
    lumis = np.array(df['ls_number'])
    #print("EXTRACTED LUMISECTIONS: ", lumis)
    
    #Extract the data in the required way
    #print(hists.shape)
    data = np.stack(hists)
    #print(data.shape)
    #Sadly, stack, dstack, vstack, and hstack don't seem to work on the second (92 length) dimension. 
    #Even with the axis parameter, I can't seem to find a way to stack the xbins object into
    #a fully 3D array. So we have to follow Luka and loop over each lumisection. 
    #Luckily this doesn't seem to add much time
    #be careful to iterate over the length of the lumi array, not lumi_end-lumi_start+1, since we could be missing lumis. 
    #Lumisections w/o data are not saved into the parquet file (eg. 2024EraC Ring 1 Run 380043 LS 353-355)
    data2 = np.array([np.stack(data[i]) for i in range(len(lumis))])

    #print("Returned Data Shape: ", data2.shape)
    #Return the data and an array of the lumisections found
    return data2, lumis


#Extract all of the runs and lumis from a single era
#Pass in a parquet file and optionally the DCS Flags JSON and return a dataframe of the 
#run_number, ls_number, ...
#The way we exclude single runs and sequences of runs is by adding the optional extra_filters parameter
#Pass in filters in an array in the form [('run_number', '!=', 12345), ('run_number', '>', 56789)]
def extract_data_whole_era(file, oms_json=None, extra_filters=None):
    #Take in a .parquet data file containing a pandas dataframe of runs/lumis
    #and return the 2D array of data from that specific run
    #with ALL lumisections
    filter_keys = [
            'run_number',
            'lumisection_number',
            "beams_stable",
            "cms_active",
            "bpix_ready",
            "fpix_ready",
            "tibtid_ready",
            "tob_ready",
            "tecp_ready",
            "tecm_ready"
        ]
    if oms_json == None:
        oms_df = pd.DataFrame(columns = filter_keys)
        oms_df.rename(columns={'lumisection_number': 'ls_number'}, inplace=True)
    else:
        with open(oms_json, 'r') as f:
            oms_filters = json.load(f)
        oms_filters = {key: val for key, val in oms_filters.items() if key in filter_keys}
        #Then turn the dictionary into a dataframe
        oms_df = pd.DataFrame.from_dict(oms_filters)
        #Need to rename one column so we can join
        oms_df.rename(columns={'lumisection_number': 'ls_number'}, inplace=True)
    
    #Sometimes we need to add extra filters to exclude single runs or sequences of runs
    if len(extra_filters) == 0: extra_filters = None #ParquetDataset needs None, not []
    #Import the parquet dataset
    df = ParquetDataset(file, filters=extra_filters).read().to_pandas()
    #join the two dataframes. NOTE: this does NOT create NaN's. It will only contain data that is present in BOTH dataframes
    #It is possible that there is a lumisection that is present in oms_JSON and not in the parquet file, 
    #And vice-versa. If that happens, the extra lumisection will just be thrown out. The number of rows
    #of the resulting dataframe SHOULD BE the minimum of the number of rows of the two dataframes. 
    #However, if there is a run in the Parquet file, but NOT the oms_JSON, then the merged dataframe will
    #have fewer rows than the Parquet dataframe
    #This behavior can be changed, decided upon by Jake Morris 30/06/2025, will discuss with Alessandro
    dataset = pd.merge(df, oms_df, on=['run_number', 'ls_number'])
    
    #Check if there were any runs in the Parquet file (i.e, with data), but not in the OMS JSON file
    if dataset.shape[0] < df.shape[0]:
        print(f"There are {df.shape[0]} rows in the Parquet dataset but only {dataset.shape[0]} rows in the merged dataframe! ")
        print(f"There are {df.shape[0] - dataset.shape[0]} lumisections that were thrown out due to no DCS flags present!\n")
    
    #Filter the merged dataset to only the runs that pass DCS flags. (only if json provided)
    if oms_json != None:
        passed_lumis_df = dataset[(dataset["beams_stable"] == True) & (dataset["cms_active"] == True) &
                              (dataset["bpix_ready"] == True) & (dataset["fpix_ready"] == True) &
                              (dataset["tibtid_ready"] == True) & (dataset["tob_ready"] == True) &
                              (dataset["tecp_ready"] == True) & (dataset["tecm_ready"] == True)]
    else:
        passed_lumis_df = df
    #Since we are only looking at ONE run_number, hists is just an array of length one
    hists = np.array(passed_lumis_df['data'])
    runs = np.array(passed_lumis_df['run_number'])
    lumis = np.array(passed_lumis_df['ls_number'])
    #print("EXTRACTED LUMISECTIONS: ", lumis)

    #Extract the data in the required way
    #print(hists.shape)
    data = np.stack(hists)
    #print(data.shape)
    #Sadly, stack, dstack, vstack, and hstack don't seem to work on the second (92 length) dimension. 
    #Even with the axis parameter, I can't seem to find a way to stack the xbins object into
    #a fully 3D array. So we have to follow Luka and loop over each lumisection. 
    #Luckily this doesn't seem to add much time
    #be careful to iterate over the length of the lumi array, not lumi_end-lumi_start+1, since we could be missing lumis. 
    #Lumisections w/o data are not saved into the parquet file (eg. 2024EraC Ring 1 Run 380043 LS 353-355)
    data2 = np.array([np.stack(data[i]) for i in range(len(lumis))])

    #print("Returned Data Shape: ", data2.shape)
    #Return the data and an array of the lumisections found
    return data2, runs, lumis, passed_lumis_df


################################################################################
#######                 Mapping to Disks/Panels/Powergroups               ######
################################################################################

#return slice objects for a data array WITH A CROSS 
#that correspond to the desired panel on a desired disk on a desired ring
def panelDiskToIndex(panel, disk, ring):
    #Input parameter checking
    if abs(disk) > 3:
        raise Exception("Disk number must be between -3 and 3!")
    if abs(panel) > 18:
        raise Exception("Panel number must be between -11 and 11 for Ring 1 and between -18 and 18 for Ring 2!")
    if ring > 2 or ring < 1:
        raise Exception("Ring number must be either 1 or 2!")
        
    #We are only dealing with Ring 1 right now
    if ring == 2:
        raise Exception("To be implemented! -jm June 11, 2025")
    elif ring == 1: 
    #Each panel is 8 bins wide and 4 bins tall
    #These equations were obtained by plotting the manually found array indices in Desmos
    #and taking the linear line of best fit. The disk one will be the same for Ring 2, though the panel one will change
        panelIndexStart = 4*panel + 44
        panelIndexEnd = 4*panel + 48
        
        diskIndexStart = 8*disk + 24
        diskIndexEnd = 8*disk + 32
        
    panelSlice = slice(panelIndexStart, panelIndexEnd)
    diskSlice = slice(diskIndexStart, diskIndexEnd)
    return panelSlice, diskSlice

#Power groups are able to be specified by
#FPix_B[m/p][I/O]_Disk#_PRT_##
#Where # = [1, 2, 3] and PRT = [1, 2, 3, 4]
#So we can't specify Disk -3, we say Bm[I/O]_D3
#And we also can't specify Panel -11, 
#we say B[m/p]O_D#
#Summary: 
#Negative Disk: m    Positive Disk: p
#Negative Panel: O   Positive Panel: I
def powerGroupToDiskPanels(powerGroupString):
    #Input Parameter checking
    stringParts = powerGroupString.split('_')
    #The whole string should be 16 characters long and
    #split into 4 separate parts 
    #'FPix', 'B[m/p][I/O]', 'D#', 'PRT#'
    if len(powerGroupString) != 16 or len(stringParts) != 4:
        raise Exception("Power Group String Not in Expected Format of: FPix_B[m/p][I/O]_D#_ROG#")
    
    #Extract string parts into useful identifiers
    quarterIdentifier = stringParts[1]
    diskIdentifier = stringParts[2]
    partIdentifier = stringParts[3]
    
    #Extract whether the disk is positive or negative
    disk_minus_positive_char = quarterIdentifier[1]
    if disk_minus_positive_char == 'm':
        disk_minus_pos = -1
    elif disk_minus_positive_char == 'p':
        disk_minus_pos = 1
    else:
        raise Exception("Power Group String had malformed B[m/p]!")
    
    #Extract whether the panel is positive or negative
    panel_minus_positive_char = quarterIdentifier[2]
    if panel_minus_positive_char == 'O':
        panel_minus_pos = -1
    elif panel_minus_positive_char == 'I':
        panel_minus_pos = 1
    else:
        raise Exception("Power Group String had malformed B[I/O]!")
        
    #Extract the disk number
    disk_number = int(diskIdentifier[1])
    #Account for minus or positive
    disk_number = disk_number * disk_minus_pos
    
    #Extract the power groupd part number
    part_number = int(partIdentifier[3])
    
    #Map the part number to the panels
    #NOTE: THIS IS JUST FOR RING 1!!!!
    if part_number == 1:
        panels = np.array([1, 2, 3])
    elif part_number == 2:
        panels = np.array([4, 5, 6])
    elif part_number == 3:
        panels = np.array([7, 8])
    elif part_number == 4:
        panels = np.array([9, 10, 11])
    
    #Make sure to set the panel numbers negative depending on [I/O]
    panels = panels * panel_minus_pos
    #print("PANELS: ", panels)
    
    #print(f"Disk: {disk_number} \t Panels: {panels}")
    return panels, disk_number

#Now that we have a function that takes in powerGroup Strings and returns the disk number and panels
#We can make another function that will return the specific slice's for a 
#specific powerGroup String
def powerGroupToIndex(powerGroupString):
    #Get the disk number and panels of interest
    panels, disk = powerGroupToDiskPanels(powerGroupString)
    #print(panels)
    #Loop over each panel to get their slice's. Make sure to specify the type or numpy get's mad
    slices = np.empty(len(panels), dtype=type(slice))
    for i, panel in enumerate(panels):
        slices[i], diskSlice = panelDiskToIndex(panel, disk, 1)
    
    #Get whether we are Inner or Outer
    stringParts = powerGroupString.split('_')
    #Extract whether the panel is positive or negative. Third character of second part of FPix_B[m/p][I/O]_Disk#_PRT_##
    panel_minus_positive_char = stringParts[1][2]
    if panel_minus_positive_char == 'I':
        start = slices[0].start
        end = slices[-1].stop
    elif panel_minus_positive_char == 'O':
        start = slices[-1].start
        end = slices[0].stop
    else:
        raise Exception("Power Group String had malformed B[I/O]!")
    #If Inner, we want to slice from slice[0].start to slice[-1].stop
    #But if we are Outer, then we want to slice from slice[-1].start to slice[0].stop
    #This is because of the fact that the array indexing starts in the bottom left (see index helper image)
    #So our slicing direction is normal when the panels go [1, 2, 3], but must be backwards
    #When the panels go [-1, -2, -3]. We want to slice [-3, -2, -1]. Could just reverse the array (I think), but eh
    
    #we now have an array of slices [slice(), slice(), optional third slice() depending on PRT]
    #Since we want to slice over the whole powergroup, only slice from start of first slice
    #to end of last slice
    
    
    powerGroupSlice = slice(start, end)
    
    return powerGroupSlice, diskSlice


def analyzePowerGroupString(powerGroupString):
    #Take in a powergroup string in the form FPix_B[m/p][I/O]_Disk#_PRT_#
    #and return m/p, I/O, Disk number, and part number
    #Input Parameter checking
    stringParts = powerGroupString.split('_')
    #The whole string should be 16 characters long and
    #split into 4 separate parts 
    #'FPix', 'B[m/p][I/O]', 'D#', 'PRT#'
    if len(powerGroupString) != 16 or len(stringParts) != 4:
        raise Exception("Power Group String Not in Expected Format of: FPix_B[m/p][I/O]_D#_ROG#")
    
    #Extract string parts into useful identifiers
    quarterIdentifier = stringParts[1]
    diskIdentifier = stringParts[2]
    partIdentifier = stringParts[3]
    
    #Extract whether the disk is positive or negative
    disk_minus_positive_char = quarterIdentifier[1]
    if disk_minus_positive_char == 'm':
        disk_minus_pos = -1
    elif disk_minus_positive_char == 'p':
        disk_minus_pos = 1
    else:
        raise Exception("Power Group String had malformed B[m/p]!")
    
    #Extract whether the panel is positive or negative
    panel_minus_positive_char = quarterIdentifier[2]
    if panel_minus_positive_char != 'O' and panel_minus_positive_char != 'I':
        raise Exception("Power Group String had malformed B[I/O]!")
        
    #Extract the disk number
    disk_number = int(diskIdentifier[1])
    #Account for minus or positive
    disk_number = disk_number * disk_minus_pos
    
    #Extract the power groupd part number
    part_number = int(partIdentifier[3])
    
    #print(f"Disk: {disk_number} \t Panels: {panels}")
    return disk_minus_positive_char, panel_minus_positive_char, disk_number, part_number


#A function which takes in two powergroup strings and 
#returns whether or not they would be a single or multi disk anomaly
def powerGroupsToAnomalyType(powergroup_one, powergroup_two):
    #Extract the relavant information
    m_or_p_one, I_or_O_one, disk_number_one, part_number_one = analyzePowerGroupString(powergroup_one)
    m_or_p_two, I_or_O_two, disk_number_two, part_number_two = analyzePowerGroupString(powergroup_two)
    
    #Check to make sure the anomalies are on the same [m/p], on the same [I/O], on the same part number, and on DIFFERENT DISKS
    if m_or_p_one == m_or_p_two and I_or_O_one == I_or_O_two and part_number_one == part_number_two and disk_number_one != disk_number_two:
        anomaly_type = "Multi Disk"
    else:
        anomaly_type = "Single Disk"
    return anomaly_type


################################################################################
#######                        Plotting Functions                         ######
################################################################################


#Required Functions
cms_style = False
#Produces and saves a png of the specified data, run, lumi, and ring number
def save_digis_png(data_twodim, run_number, ls, ring, savefig=False):
#togliere fi e salvare png firettamente per l'ultimo layer

    # 1x2 grid for the endcap
    fi = ring+1-2
    fig, ax = plt.subplots(1, 1, figsize=(5, 8))
    x_label, y_label = "Disk", "Panel"  # Axis labels for the Endcap
    x_ticks = [8 * (i + 3) + 3.5 for i in range(-3, 4)]
    x_ticklabels = range(-3, 4)
    y_ticks = range(0, 13, 2)  # Define later
    y_ticklabels = range(-6, 7, 2)

    if cms_style:
        FONTSIZE=18
        fig.text(0.06, 0.95, "CMS", fontsize=FONTSIZE*1.25, fontweight='bold', ha="left")
        fig.text(0.14, 0.95, "Preliminary", fontsize=FONTSIZE, style="italic", ha="left")
        fig.text(0.88, 0.95, "2024 (13.6 TeV)", fontsize=FONTSIZE, ha="right")

    # Loop to generate each subplot with the data of the layer or ring
    sample_hist = data_twodim
    ax.set_title(f'Ring {ring}')
    if ring == 1: #Ring 1
        y_ticks = [4 * (i + 11) + 0.5 for i in range(-11, 12, 1)]
        y_ticklabels = range(-11, 12, 1)
    elif ring == 2: #Ring 2
        y_ticks = [4 * (i + 17) + 0.5 for i in range(-17, 18, 2)]
        y_ticklabels = range(-17, 18, 2)

    # Show the heatmap for each layer or ring
    im = ax.imshow(sample_hist, cmap="viridis", aspect='auto')

    # Set axis labels
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    # Set ticks and labels for x-axis
    ax.set_xticks(x_ticks)
    #ax.set_xticklabels(x_ticklabels, rotation=45, ha='right')
    ax.set_xticklabels(x_ticklabels, ha='right')

    # Set ticks and labels for y-axis
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticklabels, ha='right')
    #ax.set_yticklabels(y_ticklabels, rotation=45, ha='right')
    ax.invert_yaxis()

    # Add color bar for each subplot
    fig.colorbar(im, ax=ax, label="Digi occupancy")

    if cms_style:
        plt.tight_layout(rect=[0, 0, 1, 0.95])
    else:
        fig.suptitle(f'Run Number: {run_number}, Lumisection: {ls}', fontsize=12)
        plt.tight_layout()

    #Save the figure and show it
    if savefig: plt.savefig(f"images/run_{run_number}_LS_{ls}_rings.png")
    plt.show()
    plt.close()
    
    
    
def plot_fpix_digi(file, run_number, lumi_number, savefig=False):
    #Pass in a parquet file, a desired run number, and a 
    #desired lumisection from that specific run
    #A digi occupancy plot will be returned for the desired file, run, and lumi number
    
    data = extract_data_2d(file, run_number, lumi_number)
    #Extract the ring number from the filename
    #Our datasets always end in PXRING_#.parquet, so the -9th character is the ring number
    ring_num= int(file[-9])
    
    #Call the plot function with all of the specifics
    save_digis_png(data, run_number, lumi_number, ring_num, savefig)
    
    
def plot_digis_ax(data_twodim, run_number, ls, ring, fig=None, axis=None):
#togliere fi e salvare png firettamente per l'ultimo layer
    
    #Create the fig and ax if they are not passed to the function
    if fig==None or axis==None:
        fig, axis = plt.subplots(1, 1, figsize=(5, 8))
    
    # 1x2 grid for the endcap
    fi = ring+1-2
    fig, ax = fig, axis
    x_label, y_label = "Disk", "Panel"  # Axis labels for the Endcap
    x_ticks = [8 * (i + 3) + 3.5 for i in range(-3, 4)]
    x_ticklabels = range(-3, 4)
    y_ticks = range(0, 13, 2)  # Define later
    y_ticklabels = range(-6, 7, 2)

    if cms_style:
        FONTSIZE=18
        fig.text(0.06, 0.95, "CMS", fontsize=FONTSIZE*1.25, fontweight='bold', ha="left")
        fig.text(0.14, 0.95, "Preliminary", fontsize=FONTSIZE, style="italic", ha="left")
        fig.text(0.88, 0.95, "2024 (13.6 TeV)", fontsize=FONTSIZE, ha="right")

    # Loop to generate each subplot with the data of the layer or ring
    sample_hist = data_twodim
    if ring == 1: #Ring 1
        y_ticks = [4 * (i + 11) + 0.5 for i in range(-11, 12, 1)]
        y_ticklabels = range(-11, 12, 1)
    elif ring == 2: #Ring 2
        y_ticks = [4 * (i + 17) + 0.5 for i in range(-17, 18, 2)]
        y_ticklabels = range(-17, 18, 2)

    # Show the heatmap for each layer or ring
    im = ax.imshow(sample_hist, cmap="viridis", aspect='auto')

    # Set axis labels
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    # Set ticks and labels for x-axis
    ax.set_xticks(x_ticks)
    #ax.set_xticklabels(x_ticklabels, rotation=45, ha='right')
    ax.set_xticklabels(x_ticklabels, ha='right')

    # Set ticks and labels for y-axis
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticklabels, ha='right')
    #ax.set_yticklabels(y_ticklabels, rotation=45, ha='right')
    ax.invert_yaxis()

    # Add color bar for each subplot
    fig.colorbar(im, ax=ax, label="Digi occupancy")

    if cms_style:
        plt.tight_layout(rect=[0, 0, 1, 0.95])
    else:
        fig.suptitle(f'Run Number: {run_number}, Lumisection: {ls}', fontsize=18)
        plt.tight_layout()

    #Save the figure and show it
    return fig, ax

def plot_testing_plots(data, mes_pred, losses, losses_binary, run_number, lumi_number, ring_num, directory="images", saveFig=False, showFig=False):
    #5, 8 is the figsize of one digis plot, and we have 4 side by side. 
    fig, axes = plt.subplots(1, 4, figsize=(20, 8))
    
    FONTSIZE = 14
    
    plot_digis_ax(data, run_number, lumi_number, ring_num, fig, axes[0])
    axes[0].set_title(f'Ring {ring_num} Data', fontsize=FONTSIZE)

    plot_digis_ax(mes_pred, run_number, lumi_number, ring_num, fig, axes[1])
    axes[1].set_title(f'Ring {ring_num} Prediction', fontsize=FONTSIZE)


    plot_digis_ax(losses, run_number, lumi_number, ring_num, fig, axes[2])
    axes[2].set_title(f'Ring {ring_num} Losses', fontsize=FONTSIZE)


    plot_digis_ax(losses_binary, run_number, lumi_number, ring_num, fig, axes[3])
    axes[3].set_title(f'Ring {ring_num} Binary Losses', fontsize=FONTSIZE)
    
    if saveFig:
        #If we don't already have a directory then make it
        if not os.path.exists(directory): os.makedirs(directory)
        plt.savefig(directory + f"/NMF_run_{run_number}_LS_{lumi_number}_ring_1.png")
    if showFig: plt.show()
    plt.close()
    return fig, axes
    

################################################################################
#######                        Data Processing                            ######
################################################################################
    
#This function takes in the data in the form (num_lumis, 92, 56), 
#And returns the array index of the desired lumisection
def lumiToIndex(lumiArr, desired_lumi):
    try:
        index = np.where(lumiArr == desired_lumi)[0][0]
        return index
    except:
        raise Exception('ERROR: Desired Lumisection {} not found in lumisection array!'.format(desired_lumi))
    
#This function takes in a list of data_dictionaries as generated in the Test Whole Era notebook
#{run_number, lumisections, ..., anomalous_lumisections, anomalous_powergroups}
#Recall, the anomalous_lumisections array can contain duplicates due to being need to be kept in sync with the
#anomalous_powergroups array, as there could be multiple anomalous powergroups in a single lumisection
#This is all in a function as it could be useful in other places. But it is currently only used to 
#Communicate to the user how many anomalous lumisections there are. And the code where I would 
#normally put this is already pretty bulky. 
def calcNumAnomalousLumisections(data_dict_list):
    anomalous_lumisections_unique = []
    for data_dict in data_dict_list:
        #Extract the required info from the data_dict
        run_number = data_dict["run_number"]
        anomalous_lumisections = data_dict["anomalous_lumisections"]
        #Find only the unique lumisections with an anomaly in that run
        #And extend the running list with them. 
        anomalous_lumisections_unique.extend(np.unique(anomalous_lumisections))
    #return the total number of anomalous lumisections and all of the anomalous lumisections in that data_dict_list
    return len(anomalous_lumisections_unique), anomalous_lumisections_unique
    
    
#Remove the cross from the data for training. This can remove the cross for data in the form:
#(num_lumis, 92, 56) OR data of the form (92, 56)
def remove_cross(data):
    #Check if the input parameter is empty. If it is, just return the empty array again
    if data.size == 0:
        return data
    #Be careful because slice is LEFT-inclusive but RIGHT-exclusive D`;
    columnSlice = slice(24, 31+1)
    rowSlice = slice(44, 47+1)
    #In order to accomodate arrays that could be shape 
    #(num_lumis, 92, 56) AND (92, 56), we delete the 
    #-1th axis, so the columns, and the -2th axis, the rows. 
    #This will work on data passed to the function in both ways. 
    #So either for multiple lumisections, or one lumisection at a time. 
    data = np.delete(data, columnSlice, axis=-1)
    data = np.delete(data, rowSlice, axis=-2)
    
    return data

#Add the cross back in for visualization. 
#THIS CAN ONLY ADD THE CROSS BACK IN FOR DATA OF THE FORM:
#(num_lumis, 88, 48)
def add_cross(data):
    #Check if the input parameter is empty. If it is, just return the empty array again
    if data.size == 0:
        return data
    #I also don't really know how the below code works. I copied this directly from Luka, changing the 2 to a 4 cause FPIX adds 4 rows between data
    #[int(data.shape[1]/2)]*4 ===> [46, 46, 46, 46]
    #[int(data.shape[2]/2)]*8 ===> [28, 28, 28, 28, 28, 28, 28, 28]
    #I don't really know why this structure correctly adds in the zeros. ¯\_(ツ)_/¯
    data = np.insert(data, [int(data.shape[1]/2)]*4, 0, axis=1)
    data = np.insert(data, [int(data.shape[2]/2)]*8, 0, axis=2)       
    
    return data


# Identify and condense runs of consecutive lumisections for each powergroup
def condense_lumisection_runs(anomaly_df):
    """
    Input: DataFrame with columns 'Lumisection' and 'Powergroup'
    Output: DataFrame with columns ['Powergroup', 'Start_Lumisection', 'End_Lumisection']
    """
    condensed_rows = []
    # Group by powergroup
    for (run_number, powergroup, disk, ring_num, anomaly_type), group in anomaly_df.groupby(['Run_Number', 'Powergroup', 'Disk', 'Ring_Num', 'Anomaly_Type']):
        lumis = sorted(group['Lumisection'].unique())
        #print("ksjfng", group['Disk'])
        if not lumis:
            continue
        start = end = lumis[0]
        for ls in lumis[1:]:
            if ls == end + 1:
                end = ls
            else:
                condensedDict = {'Run_Number': run_number, 'Start_LS': start, 'End_LS': end, 'Num_LS': end-start+1, 'Powergroup': powergroup, 'Disk': disk, 'Ring_Num': ring_num, 'Anomaly_Type': anomaly_type}
                condensed_rows.append(condensedDict)
                start = end = ls
        condensed_rows.append({'Run_Number': run_number, 'Start_LS': start, 'End_LS': end, 'Num_LS': end-start+1, 'Powergroup': powergroup, 'Disk': disk, 'Ring_Num': ring_num, 'Anomaly_Type': anomaly_type})
    return pd.DataFrame(condensed_rows)


# Identify and condense runs of consecutive Start_LS and End_LS for each ['Start_LS', 'End_LS']
def condense_powergroup_overlap(anomaly_df, verbose=False):
    """
    Input: DataFrame with columns 'Lumisection' and 'Powergroup'
    Output: DataFrame with columns ['Powergroup', 'Start_Lumisection', 'End_Lumisection']
    """
    condensed_rows = []
    # Group by powergroup
    for (run_number, start_ls, end_ls, num_ls, ring_num), group in anomaly_df.groupby(['Run_Number', 'Start_LS', 'End_LS', 'Num_LS', 'Ring_Num']):
        #lumis = sorted(group['Lumisection'].unique())
        #print("ksjfng", group["Disk"])
        
        #Get all of the powergroups in this anomalous set and get rid of duplicates
        powergroups_raw = group["Powergroup"].to_list()
        powergroup_list = []
        for powergroup in powergroups_raw:
            powergroups = powergroup.split(':')
            #if verbose: print(powergroups)
            powergroup_list.append(powergroups)
        powergroup_list = np.hstack(powergroup_list)
        powergroup_list = np.unique(powergroup_list)
        #print(powergroup_list) #we now have a list of all of the anomalous powergroups
        powergroup_list_string = ':'.join(powergroup_list)
        if verbose: print(f"There are {len(powergroup_list)} Anomalous Powergroups from Lumisection {start_ls} to {end_ls} in Run Number {run_number}:\n{powergroup_list}\n") #and now it is in string form with colon separators. NOTE: IT MAY NOT BE IN ORDER BY DISK
        
        #Now we find all of the disks with anomalies
        disks_raw = group["Disk"].to_list()
        disk_list = []
        for disk in disks_raw:
            #print("DISK: ", disk)
            disk = str(disk)
            disks = disk.split(':')
            #print(disks)
            disk_list.append(disks)
        disk_list = np.hstack(disk_list)
        disk_list = np.unique(disk_list)
        #print(powergroup_list) #we now have a list of all of the anomalous powergroups
        disk_list_string = ':'.join(disk_list)
        #print(disk_list_string) #and now it is in string form with colon separators. NOTE: IT MAY NOT BE IN ORDER BY DISK
        
        #Now we see if ANY of the anomaly types are Multi Disk, or are they all Single Disk
        anomalies = group["Anomaly_Type"]
        if anomalies.isin(["Whole Quarter"]).any():
            anomaly_type = "Whole Quarter"
        elif anomalies.isin(["Multi Disk"]).any():
            anomaly_type = "Multi Disk"
        else:
            anomaly_type = "Single Disk"
        
        condensed_rows.append({'Run_Number': run_number, 'Start_LS': start_ls, 'End_LS': end_ls, 'Num_LS': num_ls, 'Powergroup': powergroup_list_string, 'Disk': disk_list_string, 'Ring_Num': ring_num, 'Anomaly_Type': anomaly_type})
    return pd.DataFrame(condensed_rows)

