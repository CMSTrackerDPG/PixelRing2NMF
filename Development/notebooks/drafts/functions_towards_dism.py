import sys
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from pyarrow.parquet import ParquetFile
from pyarrow.parquet import ParquetDataset


################################################################################
#######                        Data Extraction                            ######
################################################################################

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
        
    #Each panel is 8 bins wide and 4 bins tall
    #These equations were obtained by plotting the manually found array indices in Desmos
    #and taking the linear line of best fit. The disk one will be the same for Ring 2, though the panel one will change
    diskIndexStart = 8*disk + 24
    diskIndexEnd = 8*disk + 32
    if ring == 2:
        panelIndexStart = 4*panel + 68
        panelIndexEnd = 4*panel + 72        
    elif ring == 1: 
        panelIndexStart = 4*panel + 44
        panelIndexEnd = 4*panel + 48        
        
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
def powerGroupToDiskPanels(powerGroupString, ring):
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
    if ring == 1:
        if part_number == 1:
            panels = np.array([1, 2, 3])
        elif part_number == 2:
            panels = np.array([4, 5, 6])
        elif part_number == 3:
            panels = np.array([7, 8])
        elif part_number == 4:
            panels = np.array([9, 10, 11])
    elif ring == 2:
        if part_number == 1:
            panels = np.array([1, 2, 3, 4])
        elif part_number == 2:
            panels = np.array([5, 6, 7, 8])
        elif part_number == 3:
            panels = np.array([9, 10, 11, 12, 13])
        elif part_number == 4:
            panels = np.array([14, 15, 16, 17]) 
    
    #Make sure to set the panel numbers negative depending on [I/O]
    panels = panels * panel_minus_pos
    #print("PANELS: ", panels)
    
    #print(f"Disk: {disk_number} \t Panels: {panels}")
    return panels, disk_number

#Now that we have a function that takes in powerGroup Strings and returns the disk number and panels
#We can make another function that will return the specific slice's for a 
#specific powerGroup String
def powerGroupToIndex(powerGroupString, ring):
    #Get the disk number and panels of interest
    panels, disk = powerGroupToDiskPanels(powerGroupString, ring)
    #print(panels)
    #Loop over each panel to get their slice's. Make sure to specify the type or numpy get's mad
    slices = np.empty(len(panels), dtype=type(slice))
    for i, panel in enumerate(panels):
        slices[i], diskSlice = panelDiskToIndex(panel, disk, ring)
    
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
#returns whether or not they would be a single or multi-disk anomaly
def powerGroupsToAnomalyType(powergroup_one, powergroup_two):
    #Extract the relavant information
    m_or_p_one, I_or_O_one, disk_number_one, part_number_one = analyzePowerGroupString(powergroup_one)
    m_or_p_two, I_or_O_two, disk_number_two, part_number_two = analyzePowerGroupString(powergroup_two)
    
    #Check to make sure the anomalies are on the same [m/p], on the same [I/O], on the same part number, and on DIFFERENT DISKS
    if m_or_p_one == m_or_p_two and I_or_O_one == I_or_O_two and part_number_one == part_number_two and disk_number_one != disk_number_two:
        anomaly_type = "Multi-Disk"
    else:
        anomaly_type = "Single-Disk"
    return anomaly_type    

################################################################################
#######                 Add-Remove cross                                  ######
################################################################################


#Remove the cross from the data for training. This can remove the cross for data in the form:
#(num_lumis, 92, 56) OR data of the form (92, 56)
def remove_cross(data, ring):
    #Check if the input parameter is empty. If it is, just return the empty array again
    if data.size == 0:
        return data
    #Be careful because slice is LEFT-inclusive but RIGHT-exclusive D`;
    columnSlice = slice(24, 31+1)
    if ring == 1:
        rowSlice = slice(44, 47+1)
    elif ring == 2:
        rowSlice = slice(68, 71+1)
            
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
