import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import resample
import opensim as osim
import pandas as pd
import os

def format_numpy_array (data, column_name,time=False):

    column_data = osim.ArrayDouble()

    if (time):
        data.getTimeColumn(column_data)
    else:
        data.getDataColumn(column_name, column_data)

    np_data = np.array([column_data.get(i) for i in range(column_data.getSize())])

    return np_data

def detect_jump(data, stability_time = 1, sample_rate = 60):

    max_height_index = data.argmax()
    stability_window_size = stability_time*sample_rate   # janela de frames para se analisar estabildiade

    stability_window_end   = max_height_index - (1*sample_rate) # 1 segundo antes do ponto mais alto do salto
    stability_window_start = max(stability_window_end-stability_window_size , 0)
    print(stability_window_start,stability_window_end)
   
    jump_start_index = stability_window_end
    
    baseline_data    = data[stability_window_start:stability_window_end]
    base_line_mean   = baseline_data.mean()
    baseline_std     = np.std(baseline_data)
    threshold        = base_line_mean + 3 * baseline_std # Regra empírica do desvio padrão (ajustada para 3 empiricamente :) )

    while(data[jump_start_index] < threshold):
        jump_start_index += 1
    
    print(jump_start_index)
    return jump_start_index, max_height_index

def extract_com_data_oc(output_full_path):
    
    pos_file_path = os.path.join(output_full_path,"analyze_BodyKinematics_pos_global.sto" )
    vel_file_path = os.path.join(output_full_path,"analyze_BodyKinematics_vel_global.sto" )
    acc_file_path = os.path.join(output_full_path,"analyze_BodyKinematics_acc_global.sto" )
    
    pos_data      = osim.Storage(pos_file_path)
    vel_data      = osim.Storage(vel_file_path)
    acc_data      = osim.Storage(acc_file_path)


    time_column = format_numpy_array(pos_data, "", time=True)
    
    com_pos_column = format_numpy_array(pos_data, "center_of_mass_Y")
    com_vel_column = format_numpy_array(vel_data, "center_of_mass_Y")
    com_acc_column = format_numpy_array(acc_data, "center_of_mass_Y")

    max_height_index = com_pos_column.argmax()
    print(max_height_index)

    return  time_column, com_pos_column, com_vel_column, com_acc_column, max_height_index

def extract_com_data_fp(folder_full_path):

    disp_file_path = os.path.join(folder_full_path,"fp_disp.txt" )
    vel_file_path  = os.path.join(folder_full_path,"fp_vel.txt" )
    acc_file_path  = os.path.join(folder_full_path,"fp_acc.txt" )

    disp_data = np.loadtxt(disp_file_path, delimiter=',')
    vel_data  = np.loadtxt(vel_file_path,  delimiter=',')
    acc_data  = np.loadtxt(acc_file_path,  delimiter=',')
    
    max_height_index = disp_data.argmax()
    print(max_height_index)

    return disp_data, vel_data, acc_data, max_height_index

def exract_com_height_oc(pos_data):
    com_height = pos_data[60:120].mean()
    return com_height

def crop_signal(signal, middle_point, sample_rate, time = 1.5):

    start_index = max(middle_point - int(time*sample_rate),  0)           #  Volta até 1.5 segundo do momento de altura máxima
    end_index   = min(middle_point + int(time*sample_rate),  len(signal)) # Avança até 1.5 segundo do momento de altura máxima

    return signal[start_index:end_index]

def compare_signals(fp_signal, oc_signal,oc_time, title, cp_directory,file_name):

    fp_signal_downsampled = resample(fp_signal, len(oc_signal))

    # Plotar ambos os sinais
    plt.figure(figsize=(10, 6))

    # Sinal original de 60 Hz
    plt.plot(oc_time, oc_signal, label="Open Cap", color='red', alpha=0.7)

    # Sinal downsampled de 1000 Hz para 60 Hz
    plt.plot(oc_time, fp_signal_downsampled, label="Plataforma de força", color='green', alpha=0.7)

    # Configurações do gráfico
    plt.xlabel('Tempo (s)')
    plt.ylabel('Amplitude')
    plt.title(title)
    plt.legend()

    file_name = title+"_" +file_name

    var_fig_path = os.path.join(cp_directory,file_name)
    plt.grid(True)
    plt.savefig(var_fig_path, dpi=300,format='png')

    mae = np.mean(np.abs(fp_signal_downsampled - oc_signal))
    print("[{file_name}] MAE: {mae}".format(file_name = file_name, mae=mae))

    return fp_signal_downsampled, oc_signal

def load_data_from_file(file_name):

    data = np.loadtxt(file_name, delimiter=',', skiprows=1)

    time = data[:, 0]
    position = data[:, 1]
    velocity = data[:, 2]
    acceleration = data[:, 3]

    return time, [position, velocity, acceleration]

