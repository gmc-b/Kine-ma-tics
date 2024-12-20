# Open sim analysys function file

import opensim as osim
import os
from kinematic_class import kinematics
import numpy as np

import matplotlib.pyplot as plt

POS = 0
VEL = 1
ACC = 2

def analyse_tool_setup(model,model_full_path,movement_full_path,output_full_path,start_time,final_time,step_interval):
    analyze_tool = osim.AnalyzeTool()
    analyze_tool.setName("analyze")
    analyze_tool.setModelFilename(model_full_path)
    analyze_tool.setModel(model)
    analyze_tool.setCoordinatesFileName(movement_full_path)
    analyze_tool.setStartTime(start_time)
    analyze_tool.setFinalTime(final_time) 
    analyze_tool.setLoadModelAndInput(True)
    analyze_tool.setResultsDir(output_full_path)

    return analyze_tool


def get_time_parameters(motion): 
    step_interval = motion.getStepInterval()
    start_time    = motion.getFirstTime()
    final_time    = motion.getLastTime()

    return [start_time,final_time,step_interval]

######################### Analysis functions #########################

def body_kinematic_analysis(model,start_time,final_time,step_interval):
    body_kinematics = osim.BodyKinematics()
    body_kinematics.setModel(model)
    body_kinematics.setStartTime(start_time)
    body_kinematics.setEndTime(final_time) 
    body_kinematics.setStepInterval(step_interval) 
    body_kinematics.setInDegrees(True)  
    body_kinematics.setRecordCenterOfMass(True)
    return body_kinematics

def com_analisys(directory_path,mot_file_name,cutoff_frequency = 10):
    kinematic = kinematics(directory_path,mot_file_name,"LaiUhlrich2022_scaled",lowpass_cutoff_frequency_for_coordinate_values=cutoff_frequency)
    oc_pos = kinematic.get_center_of_mass_values(lowpass_cutoff_frequency=cutoff_frequency)
    oc_vel = kinematic.get_center_of_mass_speeds(lowpass_cutoff_frequency=cutoff_frequency)
    oc_acc = kinematic.get_center_of_mass_accelerations(lowpass_cutoff_frequency=cutoff_frequency)
    return [oc_pos,oc_vel,oc_acc]

######################### File functions #########################

def save_com_data_to_file(com_data,com_output_directory, file_name):
    pos = 0
    vel = 1
    acc = 2

    file_path = os.path.join(com_output_directory,file_name)


    time = com_data[0]["time"].to_numpy()

    combined_data = np.column_stack((
        time,
        com_data[pos]["y"].to_numpy(),  
        com_data[vel]["y"].to_numpy(),  
        com_data[acc]["y"].to_numpy(),  
    ))
    np.savetxt(
        file_path,
        combined_data,
        delimiter=',',
        fmt='%f',
        header='time,position_y,velocity_y,acceleration_y',
        comments=''
    )
    print(f"Dados salvos em {file_path}")





def save_oc_figure(var,label,unit,file_name,output_directory,show = False):
    plt.figure(figsize=(8, 6))  

    plt.plot(var['time'], var['y'], linestyle='-', color='b', label='Sinal')

    plt.title('{label} X Tempo'.format(label=label))
    plt.xlabel('Tempo (s)')
    plt.ylabel("{label} [{unit}]".format(label=label,unit=unit))
    plt.grid()
    plt.legend()

    fig_name = "fig_"+label+"_"+file_name+".png"

    var_fig_path = os.path.join(output_directory,fig_name)
    plt.savefig(var_fig_path, dpi=300)

    if show:
        plt.show
    plt.close()