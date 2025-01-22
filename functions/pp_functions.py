# Post-processing functions file

import opensim as osim
import os 
import numpy as np
######################### Utillity functions #########################
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
    threshold        = base_line_mean + 3 * baseline_std # Regra empírica do desvio padrão

    while(data[jump_start_index] < threshold):
        jump_start_index += 1
    
    return jump_start_index, max_height_index





######################### Post-processing functions #########################

def post_procces_body_kinematics(output_full_path):
    
    folder    = output_full_path.split("\\")[-3]
    file_name = output_full_path.split("\\")[-1]

    pos_file_path = os.path.join(output_full_path,"analyze_BodyKinematics_pos_global.sto" )
    vel_file_path = os.path.join(output_full_path,"analyze_BodyKinematics_vel_global.sto" )
    
    pos_data      = osim.Storage(pos_file_path)
    vel_data      = osim.Storage(vel_file_path)

    output_string = "               [{folder}][{file_name}]\n\n".format(folder = folder, file_name = file_name) 

    time_column = format_numpy_array(pos_data, "", time=True)
    cmy_column  = format_numpy_array(pos_data, "center_of_mass_Y")


    # Análise de altura máxima
    max_height       = cmy_column.max()
    max_height_index = cmy_column.argmax()
    max_height_time  = time_column[max_height_index]


    output_string += "Altura CM[Máxima]: {max_height}m ({max_height_time}s)\n\n".format(max_height = max_height,max_height_time=max_height_time) 
    
######################################################################################################

    
    tyr_pos_column = format_numpy_array(pos_data, "toes_r_Y")
    #tyl_pos_column = format_numpy_array(pos_data, "toes_l_Y")
    #tymean_pos_column = (tyr_pos_column + tyl_pos_column) /2

    jump_start_index, max_height_index = detect_jump(tyr_pos_column)

    output_string += "Altura halúx[início de salto]:{height_start:4f} ({time_start})s \n".format(height_start = tyr_pos_column[jump_start_index],time_start = time_column[jump_start_index]) 
    output_string += "Altura halúx[máxima]:         {height_final:4f} ({time_final})s \n\n".format(height_final = tyr_pos_column[max_height_index],time_final = time_column[max_height_index]) 
######################################################################################################

    tyr_vel_column = format_numpy_array(vel_data, "toes_r_Y")
    #tyl_vel_column = format_numpy_array(vel_data, "toes_l_Y")
    #tymean_vel_column = (tyr_vel_column + tyl_vel_column) /2

    output_string += "Velocidade hálux[início de salto]:\n"

    for i in range(10):
        output_string += "-> {vel:4f} m/s \t({time}s)\n".format(vel = tyr_vel_column[jump_start_index+i],time = time_column[jump_start_index+i]) 

######################################################################################################

    outut_text_file_path = os.path.join(output_full_path, "bk_results.txt") 
    with open(outut_text_file_path, mode="w", encoding='utf-8') as text_output_file:
        text_output_file.write(output_string)
        print(output_string)


