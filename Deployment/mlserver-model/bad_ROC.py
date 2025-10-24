import itertools
import numpy as np
import pandas as pd
from functions import plot_losses, powerGroupToIndex, powerGroupsToAnomalyType, analyzePowerGroupString

optimized_powerGroupStringsList = np.array(['FPix_BmO_D3_ROG4','FPix_BmO_D2_ROG4','FPix_BmO_D1_ROG4','FPix_BmO_D3_ROG3','FPix_BmO_D2_ROG3','FPix_BmO_D1_ROG3','FPix_BmO_D3_ROG2','FPix_BmO_D2_ROG2','FPix_BmO_D1_ROG2','FPix_BmO_D3_ROG1','FPix_BmO_D2_ROG1','FPix_BmO_D1_ROG1','FPix_BmI_D3_ROG1','FPix_BmI_D2_ROG1','FPix_BmI_D1_ROG1','FPix_BmI_D3_ROG2','FPix_BmI_D2_ROG2','FPix_BmI_D1_ROG2','FPix_BmI_D3_ROG3','FPix_BmI_D2_ROG3','FPix_BmI_D1_ROG3','FPix_BmI_D3_ROG4','FPix_BmI_D2_ROG4','FPix_BmI_D1_ROG4','FPix_BpO_D1_ROG4','FPix_BpO_D2_ROG4','FPix_BpO_D3_ROG4','FPix_BpO_D1_ROG3','FPix_BpO_D2_ROG3','FPix_BpO_D3_ROG3','FPix_BpO_D1_ROG2','FPix_BpO_D2_ROG2','FPix_BpO_D3_ROG2','FPix_BpO_D1_ROG1','FPix_BpO_D2_ROG1','FPix_BpO_D3_ROG1','FPix_BpI_D1_ROG1','FPix_BpI_D2_ROG1','FPix_BpI_D3_ROG1','FPix_BpI_D1_ROG2','FPix_BpI_D2_ROG2','FPix_BpI_D3_ROG2','FPix_BpI_D1_ROG3','FPix_BpI_D2_ROG3','FPix_BpI_D3_ROG3','FPix_BpI_D1_ROG4','FPix_BpI_D2_ROG4','FPix_BpI_D3_ROG4'])
#A list of all of the quarters of the detector
QUARTERS = np.array([['FPix_BmI_D3_ROG1','FPix_BmI_D3_ROG2','FPix_BmI_D3_ROG3','FPix_BmI_D3_ROG4','FPix_BmI_D2_ROG1','FPix_BmI_D2_ROG2','FPix_BmI_D2_ROG3','FPix_BmI_D2_ROG4','FPix_BmI_D1_ROG1','FPix_BmI_D1_ROG2','FPix_BmI_D1_ROG3','FPix_BmI_D1_ROG4'], ['FPix_BmO_D3_ROG1','FPix_BmO_D3_ROG2','FPix_BmO_D3_ROG3','FPix_BmO_D3_ROG4','FPix_BmO_D2_ROG1','FPix_BmO_D2_ROG2','FPix_BmO_D2_ROG3','FPix_BmO_D2_ROG4','FPix_BmO_D1_ROG1','FPix_BmO_D1_ROG2','FPix_BmO_D1_ROG3','FPix_BmO_D1_ROG4'], ['FPix_BpI_D1_ROG1','FPix_BpI_D1_ROG2','FPix_BpI_D1_ROG3','FPix_BpI_D1_ROG4','FPix_BpI_D2_ROG1','FPix_BpI_D2_ROG2','FPix_BpI_D2_ROG3','FPix_BpI_D2_ROG4','FPix_BpI_D3_ROG1','FPix_BpI_D3_ROG2','FPix_BpI_D3_ROG3','FPix_BpI_D3_ROG4'], ['FPix_BpO_D1_ROG1','FPix_BpO_D1_ROG2','FPix_BpO_D1_ROG3','FPix_BpO_D1_ROG4','FPix_BpO_D2_ROG1','FPix_BpO_D2_ROG2','FPix_BpO_D2_ROG3','FPix_BpO_D2_ROG4','FPix_BpO_D3_ROG1','FPix_BpO_D3_ROG2','FPix_BpO_D3_ROG3','FPix_BpO_D3_ROG4']])

RING = 2
    
def search_for_anomalies(losses, thresholds):

    verbose = 0
    mename = 'Ring2'

    loss_threshold = thresholds['loss_threshold']
    ROC_fraction = thresholds['ROC_fraction']
    
    losses_array = np.array(losses[mename]) 
    if verbose: print("Searching for anomalies")
    res = np.zeros(losses_array.shape[0], dtype=bool)

    for i in range(losses_array.shape[0]):  # loop over LS
        full_losses = losses_array[i]
        binary_losses = (full_losses > loss_threshold).astype(int)
        anomalous_powergroups = []

        for j, powergroup in enumerate(optimized_powerGroupStringsList):
                powerGroupSlice, diskSlice = powerGroupToIndex(powergroup, RING)
                num_bad_ROCs = int(np.sum(binary_losses[powerGroupSlice, diskSlice].flatten()))
                total_ROC_in_powergroup = int(binary_losses[powerGroupSlice, diskSlice].flatten().size)
                if verbose: print(powergroup, num_bad_ROCs, total_ROC_in_powergroup, int(num_bad_ROCs/total_ROC_in_powergroup*100),"%" )

                #Access each power group in each lumisection and see if more than 40% of the bins are on
                if num_bad_ROCs >= int(ROC_fraction/100 * total_ROC_in_powergroup):
                    if verbose: print(f"Anomalous Power Group: {powergroup}")
                    anomalous_powergroups.append(powergroup)

        anomalous_powergroups = np.array(anomalous_powergroups)

        #If there are no anomalous powergroups do not proceed further
        if anomalous_powergroups.size == 0:
            if verbose: print("NO Anomalies")
        else:
            if verbose: print("Check Anomaly Type")
            #Create dataframe of anomalous lumisections and powergroups
            anomaly_df = pd.DataFrame({"powergroups": anomalous_powergroups})

            if verbose: print("Anomaly Dataframe: \n", anomaly_df, '\n')

            #Create a pandas dataframe with all anomalies in that LS
            headers = ["Powergroup", "Disk", "Anomaly_Type"]
            dataDict = dict.fromkeys(headers)
            detailed_anomaly_df = pd.DataFrame(columns=headers)

            #Get the lumisection and all of the anomaly powergroups
            #If there is only one powergroup, mark it Single Disk, preparing the detailed Pandas anomaly dataframe, then move on
                #If there is multiple powergroups, iterate through each pair, breaking on the first Multi-disk anomaly after preparing the detailed Pandas anomaly dataframe
                #If there is no Multi-disk anomaly despite there being multiple anomalies in one lumisection, prepare the detailed Pandas anomaly dataframe with EACH anomaly

            dataframe = anomaly_df
            powergroups = dataframe["powergroups"].to_list()

            #If there are 12 anomalous powergroups in one lumisection, check if it's a whole quarter out
            if len(powergroups) == 12:
                    for quarter in QUARTERS:
                        #If all of the powergroups are in one quarter, then we can save and break early
                        if np.all(np.isin(powergroups, quarter)):
                            #Fill in the data dict
                            m_or_p, I_or_O, disk_number, part_number = analyzePowerGroupString(powergroups[0])
                            dataDict["Powergroup"] = ':'.join(powergroups)
                            dataDict["Disk"] = "-1:-2:-3" if disk_number < 0 else "1:2:3"
                            #dataDict["Anomaly_Type"] = "Whole Quarter"
                            dataDict["Anomaly_Type"] = "Multi-Disk"
                            dataFrame = pd.Series(dataDict).to_frame().T
                            detailed_anomaly_df = pd.concat([detailed_anomaly_df, dataFrame])
                    #then continue to the next unique anomaly
                    #continue

            #If there is only one powergroup, mark it as a Single-Disk anomaly
            if len(powergroups) == 1:
                    #Fill in the data dict
                    m_or_p, I_or_O, disk_number, part_number = analyzePowerGroupString(powergroups[0])
                    dataDict["Powergroup"] = powergroups[0]
                    dataDict["Disk"] = disk_number
                    dataDict["Anomaly_Type"] = "Single-Disk"
                    #Convert the data dict to a pandas dataframe and concat it to the detailed data frame 
                    dataFrame = pd.Series(dataDict).to_frame().T
                    detailed_anomaly_df = pd.concat([detailed_anomaly_df, dataFrame])
                    #continue to the next loop
                    
            #If there is more than one anomalous powergroup in that lumisection and it's NOT the whole quarter out
            all_powergroup_combos = itertools.combinations(powergroups, 2)
            #Loop over all pairs of powergroups and search for multi-disk anomalies
            #dataDictList = [] #Create a list to store all of the possible Single-Disk anomalies in case there are multiple anomalies but no Multi-Disk anomaly
            for powergroup_combo in all_powergroup_combos:
                    anomaly_type = powerGroupsToAnomalyType(powergroup_combo[0], powergroup_combo[1])
                    #Extract relevant information
                    m_or_p_one, I_or_O_one, disk_number_one, part_number_one = analyzePowerGroupString(powergroup_combo[0])
                    m_or_p_two, I_or_O_two, disk_number_two, part_number_two = analyzePowerGroupString(powergroup_combo[1])
                    if anomaly_type == "Multi-Disk":
                        #Fill in the data dict
                        dataDict["Powergroup"] = powergroup_combo[0] + ':' + powergroup_combo[1]
                        dataDict["Disk"] = str(disk_number_one) + ':' + str(disk_number_two)
                        dataDict["Anomaly_Type"] = "Multi-Disk"
                        dataFrame = pd.Series(dataDict).to_frame().T
                        detailed_anomaly_df = pd.concat([detailed_anomaly_df, dataFrame])
                    else:
                        #Fill in a data dict for each anomaly
                        dataDict["Powergroup"] = powergroup_combo[0]
                        dataDict["Disk"] = str(disk_number_one)
                        dataDict["Anomaly_Type"] = "Single-Disk"
                        dataFrame = pd.Series(dataDict).to_frame().T
                        detailed_anomaly_df = pd.concat([detailed_anomaly_df, dataFrame])

                        #Fill in second data dict
                        dataDict["Powergroup"] = powergroup_combo[1]
                        dataDict["Disk"] = str(disk_number_two)
                        dataDict["Anomaly_Type"] = "Single-Disk"
                        dataFrame = pd.Series(dataDict).to_frame().T
                        detailed_anomaly_df = pd.concat([detailed_anomaly_df, dataFrame])
               
            #Remove all exact duplicate rows
            detailed_anomaly_df = detailed_anomaly_df.drop_duplicates()

            if verbose: print(detailed_anomaly_df.to_string())
            # Example of anomaly_df from run 386661 (LS 103)
            #Powergroup Disk Anomaly_Type
            #0  FPix_BpO_D1_ROG2:FPix_BpO_D2_ROG2  1:2   Multi-Disk
            #0  FPix_BpO_D1_ROG2:FPix_BpO_D3_ROG2  1:3   Multi-Disk
            #0  FPix_BpO_D2_ROG2:FPix_BpO_D3_ROG2  2:3   Multi-Disk

            if verbose: 
                plot_losses(full_losses, binary_losses, 100, 200, 2, saveFig=False, showFig=True)
                    
            if (detailed_anomaly_df['Anomaly_Type'] == 'Multi-Disk').any():
                res[i] = True

    return res
