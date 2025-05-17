
# 将job_class_map中所有以类结尾的去除，并保存为一个新的json
import json
import os
import constant

def preprocess_job_class_map(job_class_map_path, new_job_class_map_path):
    with open(job_class_map_path, 'r', encoding='utf-8') as f:
        job_class_map = json.load(f)
    new_job_class_map = {}
    for k, v in job_class_map.items():
        if k.endswith('类'):
            continue
        new_job_class_map[k] = v
    with open(new_job_class_map_path, 'w', encoding='utf-8') as f:
        json.dump(new_job_class_map, f, ensure_ascii=False) 
# 读取文件夹下的所有json，并将错误编号ID的重新编号
def renumber_error_id(job_folder_path):
    # 读取文件夹下的所有json
    file_names = os.listdir(job_folder_path)
    # 除了最后一个json文件，其他文件都要重新编号
    for i in range(len(file_names) - 1):
        file_name = file_names[i]
        if file_name.endswith('.json'):
            # 读取第一个数据
            print(f"正在处理{file_name}")
            with open(os.path.join(job_folder_path, file_name), 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not data:
                    continue
                # 直接重新编号
                for i in range(len(data)):
                    data[i]['职位ID'] = i + 1
                # 保存修改后的数据
                with open(os.path.join(job_folder_path, file_name), 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False)
            
# 读取某文件下的所有json文件，并将其中内容为空的文件按照特定格式提取来一个map
def extract_empty_file_map(job_folder_path):
    # 读取文件夹下的所有json
    file_names = os.listdir(job_folder_path)
    empty_file_map = {}
    for file_name in file_names:
        if file_name.endswith('.json'):
            # 读取第一个数据
            print(f"正在处理{file_name}")
            with open(os.path.join(job_folder_path, file_name), 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not data:
                    # 文件格式是idx_major_code_majar_name.json，idx是职位ID，major_code是专业代码，majar_name是专业名称，提取为majar_name:major_code
                    idx = file_name.split('_')[0]
                    major_code = file_name.split('_')[1]
                    majar_name = file_name.split('_')[2].split('.')[0]
                    empty_file_map[majar_name] = major_code
    return empty_file_map
#  preprocess_job_class_map(constant.JOB_CLASS_MAP_PATH, new_job_class_map_path=constant.NEW_JOB_CLASS_MAP_PATH)
#  renumber_error_id(constant.JOB_FOLDER_PATH)
#  preprocess_job_class_map(constant.JOB_CLASS_MAP_PATH, new_job_class_map_path=constant.NEW_JOB_CLASS_MAP_PATH)
if __name__ == '__main__':
    renumber_error_id(constant.JOB_FOLDER_PATH)
    print(extract_empty_file_map(constant.JOB_FOLDER_PATH))
   