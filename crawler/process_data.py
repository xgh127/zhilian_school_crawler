
# 将job_class_map中所有以类结尾的去除，并保存为一个新的json
import json
import os
import constant
import pandas as pd
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
# 将指定目录下的json文件转excel文件


def json_to_excel(job_folder_path, output_path):
    # 读取文件夹下的所有json
    file_names = os.listdir(job_folder_path)
    # 将每个json文件转为excel，并保存到output_path目录下
    for file_name in file_names:
        if file_name.endswith('.json'):
           # 保存为excel文件
            print(f"正在处理{file_name}")
            with open(os.path.join(job_folder_path, file_name), 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 将data转为dataframe
                df = pd.DataFrame(data)
                # 保存为excel文件
                df.to_excel(os.path.join(output_path, file_name.split('.')[0] + '.xlsx'), index=False)


 # 匹配persist下的major_info.json和job_class_map_new.json,  只保留job_class_map_new.json中在major_info.json中出现的专业信息
def match_major_info_and_job_class_map(major_info_path, job_class_map_path, output_path):
    # 读取major_info.json
    with open(major_info_path, 'r', encoding='utf-8') as f:
        major_info = json.load(f)
        third_level_majors = set()
        
        for first_level, second_levels in major_info.items():
            for second_level, third_levels in second_levels.items():
                for third_level in third_levels:
                    third_level_majors.add(third_level)

       
    # 读取job_class_map_new.json
    with open(job_class_map_path, 'r', encoding='utf-8') as f:
        job_class_map = json.load(f)
    # 匹配major_info.json和job_class_map_new.json,  只保留job_class_map_new.json中在major_info.json中出现的专业信息
    new_job_class_map = {}
    for k, v in job_class_map.items():
       # 如果key在major_info.json中的三级专业中
       if k in third_level_majors:
           # 则添加到new_job_class_map中
           new_job_class_map[k] = v
    with open(os.path.join(output_path, 'job_class_map_v2.json'), 'w', encoding='utf-8') as f:
        json.dump(new_job_class_map, f, ensure_ascii=False)
if __name__ == '__main__':
    # renumber_error_id(constant.JOB_FOLDER_PATH)
    # print(extract_empty_file_map(constant.JOB_FOLDER_PATH))
    # json_to_excel("./crawler/finished_data", output_path='./crawler/excel_data')
    match_major_info_and_job_class_map("./crawler/persist/major_info.json", "./crawler/persist/job_class_map_new.json", "./crawler/persist")

   