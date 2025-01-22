# Arquivo: main.py
#  
# :: Aplicação para análise e comparação de dados de movimento gerados por Open Cap
# :: e dados de aceleração adquiridos pela aplicação jumpy em plataforma de força

import os
import sys
from os.path import dirname, abspath
import opensim as osim
import json
import time
from pathlib import Path
import re

# Function files
import functions.osim_functions as osim_f
import functions.post_process_functions as pp_f
import functions.jumpy_functions as jp_f


# Lista apenas os arquivos com a extensão especificada
def list_files(directory, extension):
    try:
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

# Lista diretórios
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


# Lê o arquivo JSON de configurações
def setup(setup_file):
    with open(setup_file) as json_file:
        file_contents = json_file.read()
        setup_dic = json.loads(file_contents)
    return setup_dic


# Realiza o pareamento de arquivos com mesmo número no final para comparação
# (Ex: salto_plataforma_1.txt e salto_opencap_1.txt)
def file_pairing(dir_a, dir_b):
    def get_files_with_numeric_suffix(directory):
        files = {}
        for file in os.listdir(directory):
            if file.endswith('.txt'):
                match = re.search(r'(\d+)\.txt$', file)  # Captura o número antes de .txt
                if match:
                    files[match.group(1)] = file
        return files
    



    
    files_a = get_files_with_numeric_suffix(dir_a)
    files_b = get_files_with_numeric_suffix(dir_b)
    
    if len(files_a) != len(files_b):
        print("Inconsistência no número de arquivos para comparação:")
        print("Arquivos em",dir_a,": ",len(files_a))
        print("Arquivos em",dir_b,": ",len(files_b))
        return None
    
    matched_files = [( os.path.join(dir_a,files_a[num]) , os.path.join(dir_b,files_b[num]) ) for num in files_a if num in files_b]
    
    return matched_files



def mot_file_body_kinematics(mot_file_list,model,model_full_path,bk_output_directory,analyize_file_path):
    

    for mot_file in mot_file_list:
        
        mot_file_name = Path(mot_file).stem

        mot_directory = os.path.join(bk_output_directory,mot_file_name)
        os.makedirs(mot_directory, exist_ok=True) 

        motion = osim.Storage(mot_file)

        time_parameters = osim_f.get_time_parameters(motion)


        # Configura a ferramenta Analyze
        analyze_tool = osim_f.analyse_tool_setup(model,model_full_path,mot_file,mot_directory,*time_parameters)

        analysis_config = osim_f.body_kinematic_analysis(model,*time_parameters)   

        analyze_tool.updAnalysisSet().cloneAndAppend(analysis_config)
        analyze_tool.printToXML(analyize_file_path)
        analyze_tool = osim.AnalyzeTool(analyize_file_path)
        analyze_tool.run()

    
    

def mot_file_com_analysis(mot_file_list,oc_directory,com_output_directory):
    
    for mot_file_path in mot_file_list:
        mot_file_name = Path(mot_file_path).stem
        
        com_data = osim_f.com_analisys(oc_directory,mot_file_name,cutoff_frequency = 10)
        
        file_name = "oc_com_"+mot_file_name+".txt"
        
        com_labels = ["Posição","Velocidade","Aceleração"]
        com_units =  ["m","m/s","m/s^2"]

        for i in range(3):
            var,label,unit = com_data[i],com_labels[i],com_units[i]
            osim_f.save_oc_figure(var,label,unit,file_name,com_output_directory)


        osim_f.save_com_data_to_file(com_data,com_output_directory,file_name)

        

def jumpy_file_analisys(acp_file_list,jp_output_directory):
    for acp_file_path in acp_file_list:
        acp_file_name = Path(acp_file_path).stem
        
        
        time, fp_data = jp_f.runAnalysisCMJSJ(acp_file_path)
        
        file_name = "jumpy_cmj_"+acp_file_name+".txt"

        
        fp_labels = ["Deslocamento","Velocidade","Acelereação"]
        fp_units =  ["m","m/s","m/s^2"]

        for i in range(3):
            var,label,unit = fp_data[i],fp_labels[i], fp_units[i]
            jp_f.save_jp_figure(time,var,label,unit,file_name,jp_output_directory)

        jp_f.save_jp_data_to_file(time,fp_data,jp_output_directory,file_name)


def plot_signals(oc_data,jp_data,cp_directory,file_name,end_prop,end_contact):
    

    oc_sample_rate = 60 
    fp_sample_rate = 1000

    jp_data_downsampled = pp_f.downsample_multicolumn(jp_data,fp_sample_rate,oc_sample_rate)

    time = 0
    pos  = 1
    vel  = 2
    acc  = 3
    
    com_height = pp_f.exract_com_height_oc(oc_data[:,pos])

    #############################################################################################


    time_column       = pp_f.crop_signal(oc_data[:,time] , end_contact)
    oc_com_pos_column = pp_f.crop_signal(oc_data[:,pos]  , end_contact)
    oc_com_vel_column = pp_f.crop_signal(oc_data[:,vel]  , end_contact)
    oc_com_acc_column = pp_f.crop_signal(oc_data[:,acc]  , end_contact)

    
    end_prop_downsampled = round(end_prop * (oc_sample_rate/fp_sample_rate))

    fp_com_disp_column = pp_f.crop_signal(jp_data_downsampled[:,pos] ,end_prop_downsampled)
    fp_com_vel_column  = pp_f.crop_signal(jp_data_downsampled[:,vel] ,end_prop_downsampled)
    fp_com_acc_column  = pp_f.crop_signal(jp_data_downsampled[:,acc] ,end_prop_downsampled)


    fp_com_pos_column = fp_com_disp_column + com_height

    #############################################################################################

    #oc_max_height_index = oc_data[:,pos].argmax()
    #fp_max_height_index = jp_data_downsampled[:,pos].argmax()
#
    #time_column       = pp_f.crop_signal(oc_data[:,time] , oc_max_height_index)
    #oc_com_pos_column = pp_f.crop_signal(oc_data[:,pos]  , oc_max_height_index)
    #oc_com_vel_column = pp_f.crop_signal(oc_data[:,vel]  , oc_max_height_index)
    #oc_com_acc_column = pp_f.crop_signal(oc_data[:,acc]  , oc_max_height_index)
#
    #
    #
#
    #fp_com_disp_column = pp_f.crop_signal(jp_data_downsampled[:,pos] ,fp_max_height_index)
    #fp_com_vel_column  = pp_f.crop_signal(jp_data_downsampled[:,vel] ,fp_max_height_index)
    #fp_com_acc_column  = pp_f.crop_signal(jp_data_downsampled[:,acc] ,fp_max_height_index)
    #
    #fp_com_pos_column = fp_com_disp_column + com_height

    pos_mae = pp_f.compare_signals(fp_com_pos_column,  oc_com_pos_column,time_column,"Posição"   ,cp_directory, file_name)
    vel_mae = pp_f.compare_signals(fp_com_vel_column,  oc_com_vel_column,time_column,"Velocidade",cp_directory, file_name)
    acc_mae = pp_f.compare_signals(fp_com_acc_column,  oc_com_acc_column,time_column,"Aceleração",cp_directory, file_name)

    pp_f.save_mae_to_file(file_name,cp_directory,pos_mae,vel_mae,acc_mae)

def main():
    start_time = time.time()

    main_dir = dirname(abspath(__file__))
    data_path           = os.path.join(main_dir,"data")
    
    setup_dic           = setup("setup.json")
    model_file          = "LaiUhlrich2022_scaled.osim"
    

    analyize_file_path  = "tmp/analyze_setup.xml"

    opencap_directory_list = list_directories(data_path)

    for directory in opencap_directory_list:

        output_directory    = os.path.join(data_path,directory,"output")

        oc_output_directory = os.path.join(output_directory,"opencap_com")
        bk_output_directory = os.path.join(output_directory,"opencap_bk")
        cp_output_directory = os.path.join(output_directory,"compare")
        jp_output_directory = os.path.join(output_directory,"jumpy_kinematics")
        
        os.makedirs(output_directory,    exist_ok=True) 
        os.makedirs(oc_output_directory, exist_ok=True) 
        os.makedirs(bk_output_directory, exist_ok=True) 
        os.makedirs(cp_output_directory, exist_ok=True) 
        os.makedirs(jp_output_directory, exist_ok=True) 

        oc_directory       = os.path.join(data_path,directory,"opencap")
        jp_directory       = os.path.join(data_path,directory,"jumpy")
        
        model_full_path    = os.path.join(oc_directory, "OpenSimData", "Model", model_file)
        movement_directory = os.path.join(oc_directory, "OpenSimData", "Kinematics")

        mot_file_list           = list_files(movement_directory,".mot")
        acp_file_list           = list_files(jp_directory,".acp")  



        model = osim.Model(model_full_path)      


######################################################################################################################################
        mot_file_com_analysis(mot_file_list,oc_directory,oc_output_directory)

        mot_file_body_kinematics(mot_file_list, model, model_full_path, bk_output_directory,analyize_file_path)
        
        jumpy_file_analisys(acp_file_list,jp_output_directory)
        
######################################################################################################################################

        # Comparação

        file_pairs = file_pairing(oc_output_directory, jp_output_directory)

        if not file_pairs:
            continue
        
        i = 0
        time_index = 0
        pos_index  = 1
        vel_index  = 2
        acc_index  = 3

        for (oc_file,jp_file),mot_file_name in zip(file_pairs, mot_file_list):

            oc_data = pp_f.load_data_from_file(oc_file)
            jp_data = pp_f.load_data_from_file(jp_file)
            
            mot_file_name = Path(mot_file_name).stem
            bk_mot_directory = os.path.join(bk_output_directory,mot_file_name)
            
            moments_dic = jp_f.findPhases(jp_data[:,time_index],jp_data[:,pos_index], jp_data[:,vel_index], jp_data[:,acc_index]) 
            end_prop_jp = moments_dic["end_propulsion_idx"]
            print("____________________________________________________")
            print("Inicio salto jumpy: ({time_start:.3f})s \n".format(time_start = jp_data[:,time_index][end_prop_jp]) )
            
            end_prop_oc = pp_f.find_end_propulsion_oc(bk_mot_directory)

            file_name = Path(oc_file).stem + "_" + Path(jp_file).stem + ".jpg"
            print("____________________________________________________")
            plot_signals(oc_data,jp_data,cp_output_directory,file_name,end_prop_jp,end_prop_oc)




    delete_file(analyize_file_path)
    end_time = time.time()
    print("Tempo de execução:",end_time - start_time)

if __name__ == "__main__":
    main()