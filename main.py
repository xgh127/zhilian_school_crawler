import os
from crawler.nowcoder_crawler import crawl_city_jobs #,, run_spider
from analysis.job_analysis import load_and_clean_data
from visualizations.visualizer import *

if __name__ == "__main__":
    # Uncomment to crawl data
    # print("开始爬取数据...")
    # crawl_city_jobs()

    #run_spider()

    print("加载与清洗数据...")
    df = load_and_clean_data()

    print("生成图表...")
    os.makedirs("output/figures", exist_ok=True)

    # 绘制各类图表
    plot_wordcloud(df)  # 绘制词云
    plot_salary_overall(df)  # 绘制薪资总体分布图
    plot_city_job_distribution_line(df)  # 绘制城市岗位数量折线图
    plot_salary_range_distribution(df)  # 绘制薪资区间分布折线图
    plot_salary_distribution_line(df)  # 绘制薪资分布折线图

    # 新增薪资区间饼图（全局）
    plot_salary_range_pie_chart(df)  # 绘制薪资区间的饼图

    # 可选：绘制指定城市的薪资区间饼图（例如“北京”）
    plot_salary_range_pie_chart(df, city="北京")  # 绘制指定城市的薪资区间饼图
    plot_salary_range_pie_chart(df, city="上海")  # 绘制指定城市的薪资区间饼图
    plot_salary_range_pie_chart(df, city="广州")  # 绘制指定城市的薪资区间饼图
    plot_salary_range_pie_chart(df, city="深圳")  # 绘制指定城市的薪资区间饼图

    plot_education_salary_comparison(df)

    print("分析完成，图表保存在 output/figures")
