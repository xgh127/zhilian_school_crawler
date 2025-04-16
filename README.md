# Zhilian Spider

本项目是基于 Python 的智联招聘数据爬取与分析项目，用于收集和分析招聘信息，并生成可视化报告。

## 安装说明

1. 源码安装：
```bash
git clone https://github.com/void678/zhilian-crawler.git
cd zhilian-crawler-main
pip install -r requirements.txt
```

2.运行
```bash
python main.py
```

## 使用说明

1. 本项目是对4个城市招聘者以python为关键字的招聘信息进行爬取，可根据实际情况更改crawler.py文件里的keyword等，需要将main.py文件里第8行crawl_city_jobs()的注释删掉

2. 功能：
   - 数据爬取（可选）
   - 数据清洗
   - 生成可视化图表

3. 实现：
   - 生成的图表将保存在 `output/figures` 目录下

## 项目结构

```
├── main.py              # 主程序入口
├── crawler/             # 爬虫模块
├── analysis/            # 数据分析模块
├── visualizations/      # 可视化模块
├── data/               # 数据存储目录
├── output/             # 输出目录
└── requirements.txt    # 项目依赖
```


## 许可证

MIT License
