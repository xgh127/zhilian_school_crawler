import time
import json
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from process_data import extract_empty_file_map


def login(driver):
    """执行登录操作"""
    driver.get("https://passport.zhaopin.com/login?")
    time.sleep(3)
    telInput = driver.find_element(By.ID, "register-sms-1_input_1_phone")
    telInput.send_keys("18290207267")
    getCodeBtn = driver.find_element(By.CLASS_NAME, "zppp-sms__send")
    getCodeBtn.click()
    codeInput = driver.find_element(By.ID, "register-sms-1_input_2_validate_code")
    time.sleep(5)
    code = input("请输入验证码：")
    codeInput.send_keys(code)
    checkbox = driver.find_element(By.XPATH, "//input[@id='accept']")
    checkbox.click()
    loginBtn = driver.find_element(By.CLASS_NAME, "zppp-submit")
    loginBtn.click()
    time.sleep(3)
    print("登录成功")

def get_job_class_map():
    """获取专业代码映射"""
    if os.path.exists('./crawler/persist/job_class_map_new.json'):
        with open('./crawler/persist/job_class_map_new.json', 'r', encoding='utf-8') as f:
            job_class_map = json.load(f)
        return job_class_map
    else:
        return {}
    

def get_base_info(item,start_index):
    """获取职位基础信息"""
    position_card = item
    return {
        "职位ID": start_index,
        "职位名称": position_card.find_element(By.CLASS_NAME, "position-card__job-name").text,
        "城市": position_card.find_element(By.CLASS_NAME, "position-card__city-name").text,
        "薪资": position_card.find_element(By.CLASS_NAME, "position-card__salary").text,
        "公司名称": position_card.find_element(By.CLASS_NAME, "position-card__company__name").text,
        "公司标签": [tag.text for tag in position_card.find_elements(By.CLASS_NAME, "position-card__company__tabs-item")],
        "学历要求": position_card.find_elements(By.CLASS_NAME, "position-card__tags__item")[1].text,
        "是否需要工作经验": position_card.find_elements(By.CLASS_NAME, "position-card__tags__item")[2].text
    }

def get_additional_info(driver):
    """获取职位补充信息"""
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "job-banner"))
    )
    
    try:
        people_count = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".job-banner__desc-text:last-child"))
        ).text
    except TimeoutException:
        people_count = "信息暂无"

    try:
        preferred_majors = [span.text for span in WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "job-info__major-tags"))
        ).find_elements(By.TAG_NAME, "span")]
    except TimeoutException:
        preferred_majors = ["信息暂无"]

    return {
        "招聘人数": people_count,
        "优选专业": ", ".join(preferred_majors)
    }



def save_incrementally(file_path, new_data):
    """增量保存数据"""
    # 读取现有数据
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing = []
    
    # 添加新数据
    existing.append(new_data)
    # 写入文件
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)




def crawl_major_jobs(driver, major_name, major_code,start_index):
    """读取专业的职位信息（修改版）"""
    print(f"📌 正在抓取 {major_name} 相关职位...")
    # 初始化职位id
    start_ID = 0
    try:
        # 初始化数据文件
        data_file = f"./crawler/data/{start_index}_{major_code}_{major_name}.json"
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        if not os.path.exists(data_file):
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

        url = f"https://xiaoyuan.zhaopin.com/search/index?refcode=4404&cateType=major&city=538%2C539%2C540&degree=4%2C3%2C10%2C1&sourceType=2&position=2%2C5&major={major_code}"
        driver.get(url)
        
        # 等待主要内容加载
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "position-card"))
        )

        while True:
            # 第一阶段：收集本页所有职位基础信息
            position_items = driver.find_elements(By.CLASS_NAME, "position-card")
            page_data = []
            position_cards = []
            # 获取所有的卡片信息，保存到position_cards列表中
            for item in position_items:
                try:
                    position_card = item
                    position_cards.append(position_card)
                except Exception as e:
                    print(f"获取职位卡片失败：{str(e)}")
                    continue
            # 获取所有基础信息
            for item in position_cards:
                try:
                    start_ID += 1
                    base_info = get_base_info(item,start_ID)
                    page_data.append(base_info)
                    print(f"【{major_name}】第 {start_ID} 个职位：🔎 已获取 {base_info['职位名称']} 的基础信息")
                except Exception as e:
                    print(f"获取基础信息失败：{str(e)}")
                    continue

            # 第二阶段：逐个获取详细信息
            original_window = driver.current_window_handle
            for index in range(len(position_items)):
                try:
                    # 重新定位元素防止失效
                    item = driver.find_elements(By.CLASS_NAME, "position-list__item")[index]
                    position_card = item.find_element(By.CLASS_NAME, "position-card")
                    
                    # 在新标签页打开详情
                    position_card.click()
                    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
                    driver.switch_to.window(driver.window_handles[-1])
                    
                    # 获取补充信息
                    additional_info = get_additional_info(driver)
                    page_data[index].update(additional_info)
                    
                    # 关闭详情页
                    driver.close()
                    driver.switch_to.window(original_window)
                    
                    # 实时保存数据
                    save_incrementally(data_file, page_data[index])
                    print(f"✅ 已保存 {page_data[index]['职位名称']} 的完整信息")
                    
                except Exception as e:
                    print(f"处理第 {index+1} 个职位时出错：{str(e)}")
                    # 恢复页面状态
                    while len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.close()
                    driver.switch_to.window(original_window)
                    driver.refresh()
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "position-list")))
                    break

            # 翻页操作
            try:
                next_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".pagination__arrow-next:not(.pagination__arrow-next--disabled)")))
                next_btn.click()
                
                # 等待新页面加载
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "position-list"))
                )
                time.sleep(2)
            except Exception:
                print("⏹ 已到达最后一页")
                break
        return True
    except Exception as e:
        print(f"⏸ {major_name} 中断于：{str(e)}")
        return False

def get_job_positions(driver, job_class_map):
    """获取职位信息（有序map版本）"""
    login(driver)
    print("✅ 登录成功，开始爬取数据")

    # 转换为有序列表（保持原顺序）
    major_list = list(job_class_map.items())
    
    # 加载上次进度
    start_index = 0
    if os.path.exists('./crawler/persist/progress.json'):
        with open('./crawler/persist/progress.json', 'r', encoding='utf-8') as f:
            progress = json.load(f)
            last_major = progress.get('last_major')
            
            # 在原始列表中查找索引
            for idx, (name, _) in enumerate(major_list):
                if name == last_major:
                    start_index = idx + 1  # 从下一个专业开始
                    break

    # 遍历专业列表
    for idx in range(start_index, len(major_list)):
        major_name, major_code = major_list[idx]
        
        try:
            print(f"\n🔍 正在处理专业 ({idx+1}/{len(major_list)})：{major_name}")
            
            # 执行爬取（新增异常捕获）
            success = crawl_major_jobs(driver, major_name, major_code,idx+1)
            
            if not success:
                print(f"⏸ {major_name} 爬取未完成，保留进度")
                break
                
            # 更新进度
            save_progress({
                "last_major": major_name,
                "processed_index": idx,
                "total_count": len(major_list),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
        except KeyboardInterrupt:
            print("\n🛑 用户主动中断，保存当前进度")
            save_progress({
                "last_major": major_list[idx-1][0] if idx >0 else "",
                "processed_index": idx-1,
                "total_count": len(major_list),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            break
            
        except Exception as e:
            print(f"❌ 严重错误：{str(e)}")
            save_progress({
                "last_major": major_list[idx-1][0] if idx >0 else "",
                "processed_index": idx-1,
                "total_count": len(major_list),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            raise

def save_progress(progress_data):
    """增强型进度保存"""
    progress_data.update({
        "version": "1.1",
        "status": "interrupted" if progress_data["processed_index"] < progress_data["total_count"]-1 else "completed"
    })
    
    try:
        with open('./crawler/persist/progress.json', 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
        print(f"💾 进度已保存：{progress_data['last_major']} ({progress_data['status']})")
    except Exception as e:
        print(f"⚠️ 进度保存失败：{str(e)}")
        # 尝试备份保存
        with open('./crawler/persist/progress_backup.json', 'w') as f:
            json.dump(progress_data, f)


   


def run_spider():
    """主函数，运行爬虫"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    try:
        # 获取专业代码映射
        job_class_map = get_job_class_map()

        get_job_positions(driver, job_class_map)

        print("爬取完成，数据已保存到 job_positions.json")
    finally:
        driver.quit()


if __name__ == "__main__":
    run_spider()