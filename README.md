# 智联招聘数据分析项目

这是一个基于 Python 的智联招聘数据爬取与分析项目，用于收集和分析招聘信息，并生成可视化报告。

## 项目功能

- 自动爬取智联招聘网站上的职位信息
- 数据清洗和预处理
- 多维度数据分析
- 丰富的可视化图表生成

## 主要分析维度

- 薪资分布分析
- 城市岗位分布
- 教育背景与薪资关系
- 职位关键词分析
- 薪资区间分布

## 安装说明

1. 克隆项目到本地：
```bash
git clone [项目地址]
```

2. 创建并激活虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行主程序：
```bash
python main.py
```

2. 程序会自动执行以下步骤：
   - 数据爬取（可选）
   - 数据清洗
   - 生成可视化图表

3. 生成的图表将保存在 `output/figures` 目录下

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

## 依赖包

- requests: HTTP 请求
- beautifulsoup4: HTML 解析
- pandas: 数据处理
- matplotlib: 数据可视化
- seaborn: 统计图表
- wordcloud: 词云生成
- selenium: 网页自动化
- webdriver_manager: 浏览器驱动管理
- jieba: 中文分词

## 注意事项

- 请确保网络连接正常
- 建议使用虚拟环境运行项目
- 爬取数据时请遵守网站的使用条款
- 生成的图表会自动保存在 output/figures 目录下

## 许可证

MIT License
