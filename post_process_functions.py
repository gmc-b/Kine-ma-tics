# Arquivo: post_process_functions.py
#  
# :: Funções para pós processamento de dados open sim e jumpy 

import numpy as np
import matplotlib.pyplot as plt
import opensim as osim
import os
from resampy import resample 



def format_numpy_array (data, column_name,time=False):

    column_data = osim.ArrayDouble()

    if (time):
        data.getTimeColumn(column_data)
    else:
        data.getDataColumn(column_name, column_data)

    np_data = np.array([column_data.get(i) for i in range(column_data.getSize())])

    return np_data

def detect_jump(data, stability_time = 1, sample_rate = 60): 
    # Procura um ponto onde a posição do membro escolhido se afasta 2 vezes o desvio padrão positivamente da média
    
    max_height_index = data.argmax()

    stability_window_end   = stability_time*sample_rate
    stability_window_start = 0

   
    jump_start_index = stability_window_end
    
    baseline_data    = data[stability_window_start:stability_window_end]
    base_line_mean   = baseline_data.mean()
    baseline_std     = np.std(baseline_data)

    threshold        = base_line_mean + 2 * baseline_std # Regra empírica do desvio padrão

    while(data[jump_start_index] < threshold):
        jump_start_index += 1
    
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
    com_height = pos_data[60:120].mean() # Média do centro de massa entre o segundo 1 e 2 dos dados
    return com_height



def crop_signal(signal, max_height_index, sample_rate=60, time=3):

    window_size = int(time * sample_rate)  # Tamanho fixo do array
    half_size = window_size // 2          # Metade do tamanho fixo

    # Definir os índices de corte
    start_index = max(max_height_index - half_size, 0)
    end_index = min(max_height_index + half_size, len(signal))

    # Extrair a parte válida do sinal
    cropped_signal = signal[start_index:end_index]

    # Criar o array de tamanho fixo e preencher com zeros
    fixed_signal = np.full(window_size, np.nan)

    # Determinar onde inserir o sinal extraído no array fixo
    start_insert = max(half_size - max_height_index, 0)
    fixed_signal[start_insert:start_insert + len(cropped_signal)] = cropped_signal

    return fixed_signal



def compare_signals(fp_signal, oc_signal,oc_time, title, cp_directory,file_name):


    # Plotar ambos os sinais
    plt.figure(figsize=(10, 6))

    plt.plot(oc_time, oc_signal, label="Open Cap", color='red', alpha=0.7)

    plt.plot(oc_time, fp_signal, label="Plataforma de força", color='green', alpha=0.7)

    # Configurações do gráfico
    plt.xlabel('Tempo (s)')
    plt.ylabel('Amplitude')
    plt.title(title)
    plt.legend()

    file_name = title+"_" +file_name

    var_fig_path = os.path.join(cp_directory,file_name)
    plt.grid(True)
    plt.savefig(var_fig_path, dpi=300,format='png')

    plt.pyplot.close()

    mae = np.nanmean(np.abs(fp_signal - oc_signal)) # Utiliza nanmean para calcular a média ignorando valores NaN
    print("[{file_name}] MAE: {mae}".format(file_name = file_name, mae=mae))


def load_data_from_file(file_name):

    data = np.loadtxt(file_name, delimiter=',', skiprows=1)
    return data


def downsample_multicolumn(jp_data, fp_sample_rate, oc_sample_rate):

    downsampled_columns = []

    for i in range(jp_data.shape[1]):
        downsampled_column = resample(jp_data[:, i],fp_sample_rate,oc_sample_rate)
        downsampled_columns.append(downsampled_column)

    jp_data_downsampled = np.column_stack(downsampled_columns)

    return jp_data_downsampled
