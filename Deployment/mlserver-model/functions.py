import numpy as np
import matplotlib.pyplot as plt

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
#######                        Plotting Functions                         ######
################################################################################

def plot_digis_ax(data_twodim, run_number, ls, ring, fig=None, axis=None):
    
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
    ax.set_xticklabels(x_ticklabels, ha='right')

    # Set ticks and labels for y-axis
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticklabels, ha='right')
    ax.invert_yaxis()

    # Add color bar for each subplot
    fig.colorbar(im, ax=ax, label="Digi occupancy")

    fig.suptitle(f'Run Number: {run_number}, Lumisection: {ls}', fontsize=18)
    plt.tight_layout()

    #Save the figure and show it
    return fig, ax

def plot_losses(losses, losses_binary, run_number, lumi_number, ring_num, directory="images", saveFig=False, showFig=False):
    fig, axes = plt.subplots(1, 2, figsize=(10, 8))
    
    FONTSIZE = 14
    
    plot_digis_ax(losses, run_number, lumi_number, ring_num, fig, axes[0])
    axes[0].set_title(f'Ring {ring_num} Losses', fontsize=FONTSIZE)

    plot_digis_ax(losses_binary, run_number, lumi_number, ring_num, fig, axes[1])
    axes[1].set_title(f'Ring {ring_num} Binary Losses', fontsize=FONTSIZE)

    if showFig: plt.show()
    plt.close()
    return fig, axes