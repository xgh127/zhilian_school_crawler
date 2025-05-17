# Zhilian Spider

本项目是基于 Python 的智联校园招聘数据爬取，用于爬取特定条件下的不同专业的招聘信息。

## 使用说明
主要代码在crawler文件夹下
文件结果如下：

- crawler
  - data 爬取结果数据
  - persist 持久化数据备份
  - crawler.py 爬虫主程序
  - constansts.py 常量定义
  -preprocess_major_map.py 获取网站的所有专业与专业代码的映射关系，便于爬取
  -procecss_data.py 对于爬取中遇到的错误信息进行修正，比如跳过了某个专业的招聘信息等，需要二次爬取
- README.md 说明文档
- requirements.txt 依赖包
- job_class_map.json 职位类别映射关系


## 许可证

MIT License
