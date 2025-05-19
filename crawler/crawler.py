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
import argparse


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

def extract_major_info(driver):
    """提取专业信息并导出为 JSON"""
    major_info = {}

    # 点击“更多专业”按钮
    more_major_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".expand-filter__more span"))
    )
    more_major_btn.click()
    time.sleep(1)

    # 提取一级学科
    first_level_options = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".s-cascader__first-level .s-cascader__option"))
    )
    for first_level_option in first_level_options:
        first_level_name = first_level_option.find_element(By.CLASS_NAME, "s-cascader__option-content").text
        major_info[first_level_name] = {}

        # 展开一级学科
        first_level_option.click()
        time.sleep(1)

        # 提取二级学科
        second_level_options = driver.find_elements(By.CSS_SELECTOR, ".s-cascader__second-level .s-cascader__option")
        for second_level_option in second_level_options:
            second_level_name = second_level_option.find_element(By.CLASS_NAME, "s-cascader__option-content").text
            major_info[first_level_name][second_level_name] = []

            # 展开二级学科
            second_level_option.click()
            time.sleep(1)

            # 提取具体专业
            third_level_options = driver.find_elements(By.CSS_SELECTOR, ".s-cascader__third-level .s-cascader__select-option")
            for third_level_option in third_level_options:
                third_level_name = third_level_option.find_element(By.CLASS_NAME, "s-cascader__select-option-content").text
                major_info[first_level_name][second_level_name].append(third_level_name)
                # 每个专业存一次 JSON 文件
                with open('major_info.json', 'w', encoding='utf-8') as f:
                    json.dump(major_info, f, ensure_ascii=False, indent=4)
                print(f"已保存专业：{third_level_name}")

            # 关闭二级学科面板
            second_level_option.click()
            time.sleep(1)

        # 关闭一级学科面板
        first_level_option.click()
        time.sleep(1)

    print("专业信息已成功导出为 major_info.json")
    return major_info


def auto_login(driver):
    driver.get("https://passport.zhaopin.com/additional?appID=8b25de552a844b6c8493333ce98b9caf&redirectURL=https%3A%2F%2Fxiaoyuan.zhaopin.com%2Fredirect%3Furl%3Dhttps%253A%252F%252Fxiaoyuan.zhaopin.com%252Fsearch%252Fjn%253D2%253Fcity%253D538%2526cateType%253Dmajor")
    time.sleep(3)
    # 切换到短信登录
    # 等待二维码登录区域元素加载完成
    qrcode_login_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'zppp-panel-qrcode-bar__img'))
        )
        # 点击二维码登录区域
    qrcode_login_element.click()
    # 切换到账号密码登录
     # 切换到“账密登录”标签
    tab_login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[text()='账密登录']"))
        )
    tab_login_btn.click()
    username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='用户名/手机号/邮箱']"))
        )
    username_input.send_keys("18290207267")

        # 输入密码
    password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='密码']"))
        )
    password_input.send_keys("xgh123456")


    # 勾选同意协议
    checkbox = driver.find_element(By.XPATH, "//input[@id='accept']")
    checkbox.click()

    # 点击登录按钮
    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "zppp-submit"))
    )
    login_btn.click()
    time.sleep(3)

    print("登录成功")

# 页面退出登录会出现登录
def relogin(driver):
    """重新登录"""
    try:
        login_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'main-body__login-guide__button'))
        )
        # 跳转到登录页面
        login_btn.click()
        auto_login(driver)
    except:
        print("重登陆异常，请人工检查")

def get_job_class_map():
    """获取专业代码映射"""
    if os.path.exists('./crawler/persist/job_class_map_v2.json'):
        with open('./crawler/persist/job_class_map_v2.json', 'r', encoding='utf-8') as f:
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


def check_login_status(driver):
    """
    检查是否登录了智联招聘网站。
    
    参数:
        driver (webdriver): Selenium WebDriver 实例。
    
    返回:
        bool: 如果已登录，返回 True；否则返回 False。
    """
    try:
        # 找有没有这个元素，如果有，说明退出登录了
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'main-body__login-guide'))
        )

        return False
    except:
        # 如果没有找到登录引导元素，则说明已登录
        return True




def crawl_major_jobs(driver, major_name, major_code,start_index):
    """读取专业的职位信息（修改版）"""
    print(f"📌 正在抓取 {major_name} 相关职位...")
    # 初始化职位id
    start_ID = 0
    page_index = 0
    try:
        # 初始化数据文件
        data_file = f"./crawler/data/{start_index}_{major_code}_{major_name}.json"
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        if not os.path.exists(data_file):
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
        time.sleep(3)# 新建文件等1s
        url = f"https://xiaoyuan.zhaopin.com/search/index?refcode=4404&cateType=major&city=538%2C539%2C540&degree=4%2C3%2C10%2C1&sourceType=2&position=2%2C5&major={major_code}"
        driver.get(url)
        time.sleep(5)
        
        # 等待主要内容加载,直接获取你想要的信息卡片，别车哪些个更大的list之类的，否则会因为刷新导致定位失败
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "position-card"))
        )
        time.sleep(2) # 等待页面加载完毕
        while True:
            # 第一阶段：收集本页所有职位基础信息
            page_index += 1
            current_time=time.time()
            # 拼接一条log字符串
            # 时间字符串转化为
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))
            log_str = f"【{time_str}】【{major_name}】第 {page_index} 页数据获取开始！"
            save_log(log_str)
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
            index = 0
            while index < (len(position_items)):
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
                    index += 1
                    
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
                    # input("请手动处理该职位，按回车继续")
                    continue
                    # return False

            # 翻页操作
            try:
                next_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".pagination__arrow-next:not(.pagination__arrow-next--disabled)")))
                next_btn.click()
                
                # 等待新页面加载
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "position-list"))
                )
                if not check_login_status(driver):
                    return False
                time.sleep(2)
            except Exception:
                print("⏹ 已到达最后一页")
                if not check_login_status(driver):
                    return False
                else:
                    return True
                  
    except Exception as e:
        print(f"⏸ {major_name} 中断于第{page_index}页：{str(e)}")
        return False

def get_job_positions(driver, job_class_map,args_auto):
    """获取职位信息（有序map版本）"""
    auto_login(driver)
    print("✅ 登录成功，开始爬取数据")
    auto_mode = args_auto

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
    idx = start_index #当前的专业索引               
    # 遍历专业列表
    while idx < len(major_list) and idx >= start_index:
        major_name, major_code = major_list[idx] 
        try:
            print(f"\n🔍 正在处理专业 ({idx+1}/{len(major_list)})：{major_name}")
            
            # 执行爬取（新增异常捕获）
            success = crawl_major_jobs(driver, major_name, major_code,idx+1) # 修改为便于计数的从1开始的索引，所以这里要+1
            
            if not success:
                print(f"⏸ {major_name} 爬取未完成，可能是退出登录了")
                # 重新登录
                auto_login(driver)
                print("🔁 重新登录成功，继续爬取")
            else:
                print(f"✅ {major_name} 爬取完成")
                idx += 1
                # 休息一会接着爬
                time.sleep(3)
            save_progress({
                "last_major": major_name,
                "processed_index": idx,
                "total_count": len(major_list),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
            if not auto_mode:
                print("🚧 已进入人工模式，将依靠输入的专业码读取对应的专业")
                cmd = input("请输入下一个爬取专业的代码（输入 -1退出）：")
                if cmd == "-1":
                    exit(0)
                else:
                    # 转为数字
                    major_code = int(cmd)
                    # 在majar_list中查找对应的专业
                    for i,(name, code) in enumerate(major_list):
                        if code == major_code:
                            idx = i
                            break
                    else:
                        print(f"❌ 未找到专业代码 {major_code}，请检查输入是否正确")
                        exit(1)
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
def save_log(log_data):
    """增强型日志保存"""
    # 创建一个日志文件txt,逐条append日志记录
    log_file = "./crawler/persist/log.txt"
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_data)
            f.write("\n")
    except Exception as e:
        print(f"⚠️ 日志保存失败：{str(e)}")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 日志保存失败：{str(e)}")
def save_progress(progress_data):
    """增强型进度保存"""
    progress_data.update({
        "version": "1.1",
        "status": "interrupted" if progress_data["processed_index"] < progress_data["total_count"]-1 else "completed"
    })
    # 
    try:
        with open('./crawler/persist/progress.json', 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
        print(f"💾 进度已保存：{progress_data['last_major']} ({progress_data['status']})")
    except Exception as e:
        print(f"⚠️ 进度保存失败：{str(e)}")
        # 尝试备份保存
        with open('./crawler/persist/progress_backup.json', 'w') as f:
            json.dump(progress_data, f)


   


def run_spider(args):
    """主函数，运行爬虫"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    try:
        # 获取专业代码映射
        job_class_map = get_job_class_map()

        get_job_positions(driver, job_class_map, args.auto)

        print("爬取完成，数据已保存到 job_positions.json")
    finally:
        driver.quit()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", default=False, help="默认非自动模式，手动输入专业代码")
    args = parser.parse_args()
    run_spider(args)