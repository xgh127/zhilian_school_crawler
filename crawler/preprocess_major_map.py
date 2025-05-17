import time
import json
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import  NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait


def get_job_class_map( driver):
    # 需要登录才能抓取，这里先登录
    driver.get("https://passport.zhaopin.com/login?")
    time.sleep(5)
    telInput = driver.find_element(By.ID, "register-sms-1_input_1_phone")
    # 输入手机号
    telInput.send_keys("18290207267")
    # 点击获取验证码
    getCodeBtn = driver.find_element(By.CLASS_NAME, "zppp-sms__send")
    getCodeBtn.click()
    
    # 验证码输入
    codeInput = driver.find_element(By.ID, "register-sms-1_input_2_validate_code")
    # 等待控制台输入验证码
    time.sleep(5)
    code = input("请输入验证码：")
    codeInput.send_keys(code)
    # 点击同意协议
    checkbox = driver.find_element(By.XPATH, "//input[@id='accept']")
    checkbox.click()

    # 点击登录
    loginBtn = driver.find_element(By.CLASS_NAME, "zppp-submit")
    loginBtn.click()
    time.sleep(5)
        # 登录完成后，跳转到搜索页面
    # 配置参数
    job_class_code = 1
    MAX_NAJOR_CODE = 12500 # 最大专业代码，根据实际情况调整
    WAIT_TIME = 3  # 显式等待时间
    SAVE_INTERVAL = 50  # 每爬取 SAVE_INTERVAL 个专业后保存一次数据
    job_class_map = {}

    # 尝试读取已保存的进度
    if os.path.exists('job_class_map.json'):
        with open('job_class_map.json', 'r', encoding='utf-8') as f:
            job_class_map = json.load(f)

        if job_class_map:
            # 获取最后一个专业代码
            last_key = list(job_class_map.values())[-1]
            job_class_code = int(last_key) + 1
            print(f"已加载之前保存的进度，从专业代码: {job_class_code} 开始继续爬取")

    endflag = False

    while not endflag:
        url = f"https://xiaoyuan.zhaopin.com/search/index?refcode=4404&cateType=major&city=538%2C539%2C540&degree=4%2C3%2C10%2C1&sourceType=2&position=2%2C5&major={job_class_code}"
        try:
            driver.get(url)
            
            # 等待页面加载完成
            WebDriverWait(driver, WAIT_TIME).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            
            # 尝试查找专业分类元素
            try:
                complex_filter_selected_list = WebDriverWait(driver, WAIT_TIME).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'complex-filter__selected__list'))
                )
                complex_filter_selected_items = complex_filter_selected_list.find_elements(By.CLASS_NAME, 'complex-filter__selected__item')
                
                if complex_filter_selected_items:
                    for item in complex_filter_selected_items:
                        span_element = item.find_element(By.TAG_NAME, 'span')
                        span_text = span_element.text.strip()
                        if span_text.startswith('专业分类:'):
                            span_text = span_text.replace('专业分类:', '').strip()
                            job_class_map[span_text] = job_class_code
                            print(f"专业代码: {job_class_code}，对应分类: {span_text}")
            except (TimeoutException, NoSuchElementException):
                print(f"专业代码: {job_class_code}，未找到专业分类信息或元素")

            # 定期保存数据
            if job_class_code % SAVE_INTERVAL == 0:
                with open('job_class_map.json', 'w', encoding='utf-8') as f:
                    
                    json.dump(job_class_map, f, ensure_ascii=False, indent=4)
                print(f"已保存 {len(job_class_map)} 个专业信息到 job_class_map.json")
            # 检查是否满足结束条件
            if  job_class_code >= MAX_NAJOR_CODE:
                print("🎉 已爬取完毕！")
                endflag = True
            
            job_class_code += 1
        except Exception as e:
            print(f"专业代码: {job_class_code}，发生错误: {str(e)}")
            job_class_code += 1

    # 最后保存数据
    if driver is not None:
        driver.quit()
    with open('job_class_map_all.json', 'w', encoding='utf-8') as f:
        json.dump(job_class_map, f, ensure_ascii=False, indent=4)
    print("爬取完成，数据已保存到 job_class_map_all.json")
    exit()
   
def run_spider():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    all_jobs = []
   
    city_jobs = get_job_class_map(driver)
    all_jobs.extend(city_jobs)

    driver.quit()

if __name__ == "__main__":
    run_spider()

