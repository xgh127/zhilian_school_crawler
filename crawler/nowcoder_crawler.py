import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

KEYWORD = "Python"
CITIES = {
    "北京": "530",
    "上海": "538",
    "广州": "763",
    "深圳": "765"
}
MAX_PAGE = 10  # 每个城市抓取页数

def crawl_city_jobs(city_name, city_code, driver):
    print(f"📍 抓取城市：{city_name}")
    jobs = []

    for page in range(1, MAX_PAGE + 1):
        url = f"https://sou.zhaopin.com/?p={page}&jl={city_code}&kw={KEYWORD}"
        driver.get(url)
        time.sleep(3)

        job_cards = driver.find_elements(By.CSS_SELECTOR, ".joblist-box__item")

        if not job_cards:
            print("  ⚠️ 未找到职位卡片，可能到达末页")
            break

        for card in job_cards:
            try:
                title = card.find_element(By.CSS_SELECTOR, ".jobinfo__name").text
                salary = card.find_element(By.CSS_SELECTOR, ".jobinfo__salary").text
                company = card.find_element(By.CSS_SELECTOR, ".companyinfo__name").text
                detail_url = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

                # 职位标签
                tags = [tag.text for tag in card.find_elements(By.CSS_SELECTOR, ".jobinfo__tag .joblist-box__item-tag")]

                # 经验和学历
                exp = ""
                edu = ""
                for info in card.find_elements(By.CSS_SELECTOR, ".jobinfo__other-info-item"):
                    text = info.text.strip()
                    if "年" in text or "经验" in text:
                        exp = text
                    elif "本科" in text or "大专" in text or "学历" in text:
                        edu = text

                # 打开职位详情页获取职位描述
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(detail_url)
                time.sleep(2)

                try:
                    job_desc = driver.find_element(By.CLASS_NAME, "describtion__detail-content").text
                except:
                    job_desc = ""

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                jobs.append({
                    "岗位名称": title,
                    "公司名称": company,
                    "城市": city_name,
                    "薪资": salary,
                    "经验要求": exp,
                    "学历要求": edu,
                    "职位标签": ", ".join(tags),
                    "职位要求": job_desc  # ✅ 新增字段
                })

            except Exception as e:
                print(f"  ⚠️ 职位解析失败，跳过：{e}")
                continue

    return jobs

def run_spider():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    all_jobs = []
    for name, code in CITIES.items():
        city_jobs = crawl_city_jobs(name, code, driver)
        all_jobs.extend(city_jobs)

    driver.quit()

    with open("jobs_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 共抓取 {len(all_jobs)} 条岗位数据，已保存为 jobs_raw.json")

if __name__ == "__main__":
    run_spider()

