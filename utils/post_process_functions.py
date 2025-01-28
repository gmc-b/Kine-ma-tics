# Arquivo: post_process_functions.py
#  
# :: Funções para pós processamento de dados opensim e jumpy 

import numpy as np
import matplotlib.pyplot as plt
import opensim as osim
import os
from resampy import resample 
from scipy.signal import correlate



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
    com_height = pos_data[0:60].mean() # Média do centro de massa no primeiro segundo dos dados
    return com_height



def crop_signal(signal, max_height_index, sample_rate=60, time=6):

    window_size = int(time * sample_rate)  # Tamanho fixo do array
    half_size = window_size // 2          # Metade do tamanho fixo

    # Define indices de corte
    start_index = max(max_height_index - half_size, 0)
    end_index = min(max_height_index + half_size, len(signal))

    cropped_signal = signal[start_index:end_index]

    # Criar np array com NaN para padding
    cropped_signal = np.full(window_size, np.nan)

    # Insere no array de tamanho fixo
    start_insert = max(half_size - max_height_index, 0)
    cropped_signal[start_insert:start_insert + len(cropped_signal)] = cropped_signal

    return cropped_signal



def calculate_lag(signal1, signal2):

    # Calcula a correlação cruzada entre os dois sinais
    signal1 = signal1[~np.isnan(signal1)]
    signal2 = signal2[~np.isnan(signal2)]

    correlation = correlate(signal1, signal2, mode='full')

    # Encontra o índice de máxima correlação
    max_corr_index = np.argmax(correlation)  # Índice onde a correlação é máxima

    # Ajusta o índice para determinar o lag (diferença para o indice de maior correlação entre os sinais)
    lag = max_corr_index - (len(signal2) - 1)

    return lag


def sync_signals(signal1, signal2, lag):

    len1, len2 = len(signal1), len(signal2)

    max_len = max(len1,len2)

    # Inicializa np arrays com NaN para padding
    signal1_synced = np.full(max_len, np.nan)
    signal2_synced = np.full(max_len, np.nan)
    print(lag)
    if lag > 0:
        # Corta o início do primeiro sinal e alinha ao segundo
        signal1_synced[:len1-lag] = signal1[lag:]
        signal2_synced[:len2] = signal2
    elif lag < 0:
        lag = abs(lag)
        # Corta o início do segundo sinal e alinha ao primeiro
        signal1_synced[:len1] = signal1
        signal2_synced[:len2-lag] = signal2[lag:]
    else:
        # Sem lag, copia os sinais originais
        signal1_synced[:] = signal1
        signal2_synced[:] = signal2

    return signal1_synced, signal2_synced



def compare_signals(fp_signal, oc_signal,oc_time, title, cp_directory,file_name):


    plt.figure(figsize=(10, 6))
    plt.plot(oc_time, oc_signal, label="Open Cap", color='red', alpha=0.7)
    plt.plot(oc_time, fp_signal, label="Plataforma de força", color='green', alpha=0.7)
    plt.xlabel('Tempo (s)')
    plt.ylabel('Amplitude')
    plt.title(title)
    plt.legend()

    file_name = title+"_" +file_name

    var_fig_path = os.path.join(cp_directory,file_name)
    plt.grid(True)
    plt.savefig(var_fig_path, dpi=300,format='png')

    plt.close()

    mae = normalized_mae(fp_signal, oc_signal)
    print("[{file_name}] MAE: {mae:.4f}".format(file_name = file_name, mae=mae))
    return mae




# utils

def load_data_from_file(file_name):

    data = np.loadtxt(file_name, delimiter=',', skiprows=1)
    return data

def format_numpy_array (data, column_name,time=False):

    column_data = osim.ArrayDouble()

    if (time):
        data.getTimeColumn(column_data)
    else:
        data.getDataColumn(column_name, column_data)

    np_data = np.array([column_data.get(i) for i in range(column_data.getSize())])

    return np_data

def downsample_multicolumn(jp_data, fp_sample_rate, oc_sample_rate):

    downsampled_columns = []

    for i in range(jp_data.shape[1]):
        downsampled_column = resample(jp_data[:, i],fp_sample_rate,oc_sample_rate)
        downsampled_columns.append(downsampled_column)

    jp_data_downsampled = np.column_stack(downsampled_columns)

    return jp_data_downsampled



def normalized_mae(fp_signal, oc_signal):
 
    # Calcula o MAE (Mean Absolute Error) normalizado entre dois sinais numpy,
    # desconsiderando valores NaN e 
    # utiliza amplitude (pico a vale) do da plataforma de força por ser menos ruidoso.
    
    if fp_signal.shape != oc_signal.shape:
        raise ValueError("Os sinais devem ter o mesmo tamanho.")

    
    valid_mask = ~np.isnan(fp_signal) & ~np.isnan(oc_signal) # Máscara para ignorar dados de preenchimento (NaN)
    valid_fp_signal = fp_signal[valid_mask]
    valid_oc_signal = oc_signal[valid_mask]

    if valid_fp_signal.size == 0 or valid_oc_signal.size == 0:
        raise ValueError("Os sinais não contêm valores para cálculo.")

    # Calcula amplitude (pico a vale) do sinal de referência
    amplitude = valid_fp_signal.max() - valid_fp_signal.min()
    if amplitude == 0:
        raise ValueError("A amplitude do sinal de referência é zero, normalização impossível.")

    # Mean Absolute Error 
    mae = np.abs(valid_fp_signal - valid_oc_signal).mean()

    # Normalizar o MAE pela amplitude
    mae_normalized = mae / amplitude

    return mae_normalized

def save_mae_to_file(file_name,cp_directory, pos_mae, vel_mae, acc_mae):

    mae_file = f"mae_{file_name}.txt"
    full_path = os.path.join(cp_directory,mae_file)
    content = (
        f"[{file_name}] Positional MAE: {pos_mae:.4f}\n"
        f"[{file_name}] Velocity MAE: {vel_mae:.4f}\n"
        f"[{file_name}] Acceleration MAE: {acc_mae:.4f}\n"
    )

    with open(full_path, 'w') as file:
        file.write(content)


# Debugging
def show_column_figure(time, var, label, unit, threshold=None, end_prop=None):

    plt.figure(figsize=(8, 6))

    plt.plot(time, var, linestyle='-', color='g', label='Sinal')

    # Adiciona linha horizontal se threshold for fornecido
    if threshold is not None:
        plt.axhline(y=threshold, color='r', linestyle='--', label=f'threshold ({threshold:.2f})')

    # Adiciona linha vertical se end_prop for fornecido
    if end_prop is not None:
        plt.axvline(x=end_prop, color='g', linestyle='--', label=f'End Prop ({end_prop:.2f})')

    # Configurações do gráfico
    plt.title(f'{label} X Tempo')
    plt.xlabel('Tempo (s)')
    plt.ylabel(f"{label} [{unit}]")
    plt.grid()
    plt.legend()

    plt.show()