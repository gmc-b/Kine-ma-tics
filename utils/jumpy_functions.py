# Arquivo: jumpy_functions.py
# Adaptação de jumpy_simple.py
#
# :: O arquivo utiliza funções adaptadas da aplicação jumpy, adaptando
# :: funcionalidades necessárias para a aplicação atual


from scipy import signal, integrate
import matplotlib.pyplot as plt
import numpy as np
import os
g = 9.7838



def integrateSignal(signal, fs):
    out = []
    aux = 0
    for i in range(0, len(signal) - 1):
        sigInst = integrate.trapz(signal[i:i + 2]) / fs
        aux = aux + sigInst
        out.append(aux)

    out.append(out[-1])
    out = np.array(out)
    return out

def find(array_condition, start=0, end=-1, num=1, order='first', direction='foward'):
    if direction == 'foward':
        if end == -1:
            end = len(array_condition)
        values = []
        arr_values = np.where(array_condition[start:end])[0]
        if order == 'first':
            values = arr_values[:num]
        elif order == 'last':
            values = arr_values[-num:len(arr_values)]
        elif order == 'mean':
            values.append(np.mean(arr_values))
        if len(values) == 1:
            return values[0] + start
        else:
            return np.array(values) + start
    elif direction == 'backwards':
        values = []
        arr_values = np.where(array_condition[end:start])[0]
        if order == 'first':
            values = arr_values[-num:len(arr_values)]
        elif order == 'last':
            values = arr_values[:num]
        elif order == 'mean':
            values.append(np.mean(arr_values))
        if len(values) == 1:
            return values[0] + end
        else:
            return np.array(values) + end
        

def mass_input():
    flag_float = False
    while(not flag_float):
        print("Não foi possível determinar a massa do voluntário pelo arquivo")
        print("Por favor insira manualmente (Exemplo de formato:")
        print("Massa [Kg]: 75.45")
        try:
            mass = float(input("Massa [Kg]: "))
            if mass>0:
                flag_float = True
        except:
            print("Não foi possível converter o valor para número decimal.")
            print("Certifique-se que esteja usando apenas caractéres numéricos")
            print("e ponto para separação de decimais")

    return mass

def readForceFile(file_path):

    i=1
    var_names = []
    mass = 0
    data_rate = 0

    with open(file_path, 'r') as f:
        first = True
        for line_str in f:
            if first:
                if (("Countermovement" in line_str) or ("CMJ" in line_str)):
                    jump_type = "CMJ"
                elif (("Weighted" in line_str) or ("WSJ" in line_str)):
                    jump_type = "WSJ"
                elif (("Squat" in line_str) or ("SJ" in line_str)):
                    jump_type = "SJ"
                elif (("Isometric" in line_str) or ("ISO" in line_str)):
                    jump_type = "ISO"
                first = False

            # Parâmetros
            if "(body weight)" in line_str:
                try:
                    mass = float(line_str.split(f'\t')[0])
                    if mass==0:
                        mass = mass_input()
                except:
                    mass = mass_input()
            
            if "Time (s)" in line_str:
                var_names = line_str.split(f'\t')
                break

            if "data rate" in line_str:
                data_rate = extract_frequency(line_str)

            i+=1
    force_data_arr = np.loadtxt(file_path, skiprows=i)
    force_data_dic = {}
    for key in var_names:
        force_data_dic[key] = force_data_arr[:, var_names.index(key)]
    
    return force_data_dic, var_names, jump_type, mass, data_rate


def getAcelVelDisp(force, fs, mass):
    acel = (force / mass) - g
    vel = integrateSignal(acel, fs)
    disp = integrateSignal(vel, fs)
    return acel, vel, disp




def getDataFromACP(file_path):
    fp_data, var_names, jump_type, mass, data_rate = readForceFile(file_path)
    force = fp_data['Raw Fz (N)']
    time = fp_data['Time (s)']
    fs = int(1/(time[1]-time[0]))
    return force, time, fs,mass, data_rate

def filterForceSignal(time, force, fs, band_type, filter_type, cutoff_freq_Hz, N):
    Wn = cutoff_freq_Hz / fs * 2
    num, den = signal.iirfilter(N, cutoff_freq_Hz, btype=band_type, analog=False, ftype=filter_type, fs=fs, output='ba')
    filtered_force = signal.filtfilt(num, den, force)
    return filtered_force



def runAnalysisCMJSJ(file_path):
    
    force, time, fs,mass, data_rate = getDataFromACP(file_path)
    
    force = filterForceSignal(time, force, fs, 'lowpass', 'butter', 30, 4)
    
    acc, vel, disp = getAcelVelDisp(force, fs, mass)



    return time, [disp, vel, acc], data_rate
    
######################################################################################################



def findPhases(cropped_time, disp, vel, acel):

    # Find unweighting and braking phases
    end_unweighting, end_braking = findUnweightingBraking(acel, vel, disp)
    # Find propulsion and flight phases
    end_propulsion, end_flight = findPropulsionFlight(acel, disp, cropped_time, end_braking)

    # Organize data processed 
    moments_dic = {
            'init_movement_idx': 0, 'init_movement': cropped_time[0],
            'end_unweighting_idx': end_unweighting, 'end_unweighting': cropped_time[end_unweighting],
            'end_braking_idx': end_braking, 'end_braking': cropped_time[end_braking],
            'end_propulsion_idx': end_propulsion, 'end_propulsion': cropped_time[end_propulsion],

            }

    return moments_dic


def findUnweightingBraking(acel, vel, disp, flgCMJ = True):
    if flgCMJ:
        acel_min_idx = np.argmin(acel)
        peak_vel_idx = np.argmax(vel[:acel_min_idx])
        end_unweighting = np.argmin(vel[:peak_vel_idx])
        end_braking = np.argmin(disp[:peak_vel_idx])
    else:
        end_unweighting = 0
        end_braking = 0

    return end_unweighting, end_braking

def findPropulsionFlight(acel, disp, cropped_time, end_braking):
    min_acel_idx = np.argmin(acel)
    max_acel_idx = np.argmax(acel[min_acel_idx:]) + min_acel_idx
    flight_center_idx = np.argmax(disp[:max_acel_idx])
    flight_center_acel = acel[flight_center_idx]
    aux_thres = flight_center_acel*0.9
    aux1 = find(acel < aux_thres, start=end_braking, end=flight_center_idx, order='first')
    aux2 = find(acel < aux_thres, start=max_acel_idx, end=flight_center_idx, order='first', direction='backwards')
    aux_center = int((aux2 + aux1)/2)
    num_samples = int(0.5*(aux2 - aux1))
    samples_segment = acel[aux_center - int(num_samples/2): aux_center + int(num_samples/2)]
    samples_time = cropped_time[aux_center - int(num_samples/2): aux_center + int(num_samples/2)]
    flight_thres = np.mean(samples_segment) + np.std(samples_segment) * 5
    end_propulsion = find(acel < flight_thres, start=aux1, end=flight_center_idx, order='first')
    end_flight = find(acel < flight_thres, start=aux2, end=flight_center_idx, order='first', direction='backwards')
    return end_propulsion, end_flight
######################################################################################################





######################### File functions #########################

import re

def extract_frequency(string):
    # Extrai a frequência (inteiro) de uma string no formato:
    # "XXXX @ YYYY (number of samples, data rate)"

    match = re.search(r'@ (\d+)', string)  # Busca um número após "@ "
    
    if match:
        num = int(match.group(1))  # Retorna o número encontrado como inteiro
    else:
        flag_nofreq = True
        while flag_nofreq:
            user_input = input("Frequência não encontrada. Insira manualmente um valor inteiro: ")
            if user_input.isdigit():
                num =  int(user_input)
                flag_nofreq = False
            else:
                print("Entrada inválida. Digite um número inteiro.")

    return num

def save_jp_data_to_file(time,fp_data,jp_output_directory,file_name):
    disp, vel, acc = fp_data[0],fp_data[1],fp_data[2]

    combined_data = np.column_stack((time,disp,vel,acc ))

    file_path = os.path.join(jp_output_directory,file_name)

    np.savetxt(
        file_path,
        combined_data,
        delimiter=',',
        fmt='%f',
        header='time,displacement_y,velocity_y,acceleration_y',
        comments=''
    )
    print(f"Dados salvos em {file_path}")


def plot_com_data_to_file(com_data, filename='plot.png', x_label='Time', y_label='Y', title='COM Data Plot'):


    plt.figure()
    plt.plot(com_data['time'], com_data['y'], label='COM Y Position', color='blue')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.close()

    print(f"Gráfico salvo como {filename}")

def save_jp_figure(time,var,label,unit,file_name,output_directory,show = False):
    plt.figure(figsize=(8, 6))  

    plt.plot(time, var, linestyle='-', color='b', label='Sinal')

    plt.title('{label} X Tempo'.format(label=label))
    plt.xlabel('Tempo (s)')
    plt.ylabel("{label} [{unit}]".format(label=label,unit=unit))
    plt.grid()
    plt.legend()

    fig_name = "fig_"+label+"_"+file_name+".png"

    var_fig_path = os.path.join(output_directory,fig_name)
    plt.savefig(var_fig_path, dpi=300)

    if show:
        plt.show()
    plt.close()