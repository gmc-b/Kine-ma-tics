import os
from os.path import dirname, abspath
import opensim as osim
import json
import time
import matplotlib.pyplot as plt
from pathlib import Path
import re

# Function files
import osim_functions as osim_f
import post_process_functions as pp_f
import jumpy_functions as jp_f



def list_files(directory, extension):
    try:
        # Lista apenas os arquivos com a extensão especificada
        files = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f)) and f.endswith(extension)
        ]
        return files
    except FileNotFoundError:
        print(f"O diretório '{directory}' não foi encontrado.")
        return []
    except PermissionError:
        print(f"Permissão negada para acessar '{directory}'.")
        return []
    
def list_directories(data_path):
    try:
        directories = [d for d in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, d))]
        return directories
    except FileNotFoundError:
        print(f"O diretório '{data_path}' não foi encontrado.")
        return []
    except PermissionError:
        print(f"Permissão negada para acessar '{data_path}'.")
        return []


def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print("Um erro ocorreu ao tentar deletar o arquivo {file_path}: {erro}".format(erro = e, file_path=file_path))



def setup(setup_file):
    with open(setup_file) as json_file:
        file_contents = json_file.read()
        setup_dic = json.loads(file_contents)
    return setup_dic


def file_pairing(dir_a, dir_b):
    def get_files_with_numeric_suffix(directory):
        files = {}
        for file in os.listdir(directory):
            if file.endswith('.txt'):
                match = re.search(r'(\d+)\.txt$', file)  # Captura o número antes de .txt
                if match:
                    files[match.group(1)] = file
        return files
    
    # Get files with numeric suffixes
    files_a = get_files_with_numeric_suffix(dir_a)
    files_b = get_files_with_numeric_suffix(dir_b)
    
    # Find matching files by numeric suffix
    matched_files = [( os.path.join(dir_a,files_a[num]) , os.path.join(dir_b,files_b[num]) ) for num in files_a if num in files_b]
    
    return matched_files




def opencap_analisys(mot_file_list,oc_directory,output_directory):
    for mot_file_path in mot_file_list:
        mot_file_name = Path(mot_file_path).stem

        
        com_output_directory   = os.path.join(output_directory,"com")
        os.makedirs(com_output_directory, exist_ok=True)
        com_data = osim_f.com_analisys(oc_directory,mot_file_name,cutoff_frequency = 10)
        
        
        file_name = "com_"+mot_file_name+".txt"
        
        com_labels = ["Posição","Velocidade","Acelereação"]
        com_units =  ["m","m/s","m/s^2"]

        for i in range(3):
            var,label,unit = com_data[i],com_labels[i],com_units[i]
            osim_f.save_oc_figure(var,label,unit,file_name,com_output_directory)


        osim_f.save_com_data_to_file(com_data,com_output_directory,file_name)


def jumpy_analisys(acp_file_list,output_directory):
    for acp_file_path in acp_file_list:
        acp_file_name = Path(acp_file_path).stem
        

        
        jp_output_directory   = os.path.join(output_directory,"jumpy_cmj")
        os.makedirs(jp_output_directory, exist_ok=True)
        time, fp_data = jp_f.runAnalysisCMJSJ(acp_file_path)
        
        file_name = "jumpy_cmj_"+acp_file_name+".txt"

        
        fp_labels = ["Deslocamento","Velocidade","Acelereação"]
        fp_units =  ["m","m/s","m/s^2"]

        for i in range(3):
            var,label,unit = fp_data[i],fp_labels[i], fp_units[i]
            jp_f.save_jp_figure(time,var,label,unit,file_name,jp_output_directory)

        jp_f.save_jp_data_to_file(time,fp_data,jp_output_directory,file_name)

def compare(time_column,oc_data,jp_data,cp_directory,file_name):
    os.makedirs(cp_directory, exist_ok=True) 

    oc_sample_rate = 60 
    fp_sample_rate = 1000

    pos = 0
    vel = 1
    acc = 2
    
    com_height = pp_f.exract_com_height_oc(oc_data[pos])
    oc_max_height_index = oc_data[pos].argmax()

    time_column       = pp_f.crop_signal(time_column  , oc_max_height_index, oc_sample_rate)
    oc_com_pos_column = pp_f.crop_signal(oc_data[pos] , oc_max_height_index, oc_sample_rate)
    oc_com_vel_column = pp_f.crop_signal(oc_data[vel] , oc_max_height_index, oc_sample_rate)
    oc_com_acc_column = pp_f.crop_signal(oc_data[acc] , oc_max_height_index, oc_sample_rate)

    
    fp_max_height_index = jp_data[pos].argmax()
    fp_com_disp_column = pp_f.crop_signal(jp_data[pos] ,fp_max_height_index, fp_sample_rate)
    fp_com_vel_column  = pp_f.crop_signal(jp_data[vel] ,fp_max_height_index, fp_sample_rate)
    fp_com_acc_column  = pp_f.crop_signal(jp_data[acc] ,fp_max_height_index, fp_sample_rate)
    
    fp_com_pos_column = fp_com_disp_column + com_height

    pp_f.compare_signals(fp_com_pos_column,  oc_com_pos_column,time_column,"Posição"   ,cp_directory, file_name)
    pp_f.compare_signals(fp_com_vel_column,  oc_com_vel_column,time_column,"Velocidade",cp_directory, file_name)
    pp_f.compare_signals(fp_com_acc_column,  oc_com_acc_column,time_column,"Aceleração",cp_directory, file_name)

    return

def main():
    start_time = time.time()

    main_dir = dirname(abspath(__file__))
    data_path           = os.path.join(main_dir,"data")
    
    setup_dic           = setup("setup.json")
    tools               = setup_dic["opensim_tools"]
    model_file          = setup_dic["model_file"]
    
    analysis_list       =  tools["analyze"]

    analyize_file_path  = "tmp/analyze_setup.xml"

    opencap_directory_list = list_directories(data_path)

    for directory in opencap_directory_list:

        output_directory   = os.path.join(data_path,directory,"output")

        oc_directory       = os.path.join(data_path,directory,"opencap")
        jp_directory       = os.path.join(data_path,directory,"jumpy")
        
        model_full_path    = os.path.join(oc_directory, "OpenSimData", "Model", model_file)
        movement_directory = os.path.join(oc_directory, "OpenSimData", "Kinematics")

        mot_file_list           = list_files(movement_directory,".mot")
        acp_file_list           = list_files(jp_directory,".acp")  
        os.makedirs(output_directory, exist_ok=True) 

        
        model = osim.Model(model_full_path)      


######################################################################################################################################
        opencap_analisys(mot_file_list,oc_directory,output_directory)

        jumpy_analisys(acp_file_list,output_directory)
        
######################################################################################################################################

        # Comparação
        oc_output_directory = os.path.join(output_directory,"com")
        jp_output_directory = os.path.join(output_directory,"jumpy_cmj")
        cp_output_directory = os.path.join(output_directory,"compare")
        file_pairs = file_pairing(oc_output_directory, jp_output_directory)

        for oc_file,jp_file in file_pairs:
            oc_time, oc_data = pp_f.load_data_from_file(oc_file)
            _, jp_data    = pp_f.load_data_from_file(jp_file)

            file_name = Path(oc_file).stem + "__" + Path(jp_file).stem + ".jpg"

            compare(oc_time,oc_data,jp_data,cp_output_directory,file_name)




    delete_file(analyize_file_path)
    end_time = time.time()
    print("Tempo de execução:",end_time - start_time)

if __name__ == "__main__":
    main()