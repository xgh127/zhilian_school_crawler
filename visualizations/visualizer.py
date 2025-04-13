import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import pandas as pd
import os
import matplotlib.font_manager as fm
import warnings
import jieba

# 字体设置
try:
    font_path = "C:/Windows/Fonts/simhei.ttf"
    if not os.path.exists(font_path):
        font_path = "C:/Windows/Fonts/msyh.ttc"
    font_prop = fm.FontProperties(fname=font_path)
    font_name = font_prop.get_name()

    plt.rcParams['font.family'] = font_name
    plt.rcParams['font.sans-serif'] = [font_name]
    plt.rcParams['axes.unicode_minus'] = False

    if font_name not in fm.fontManager.ttflist:
        fm.fontManager.addfont(font_path)
        print(f"已手动添加字体: {font_name}")
except Exception as e:
    print(f"字体设置错误: {e}")
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']

sns.set(style="whitegrid", font=font_name)

def extract_keywords(text, stopwords=set()):
    words = jieba.lcut(text)
    words = [w.lower() for w in words if w.strip() and w not in stopwords and len(w) > 1]
    return words

def set_font_for_plot(ax, font_properties):
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                 ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontproperties(font_properties)

def plot_wordcloud(df):
    if "job_description" not in df.columns:
        print("⚠️ 缺少 'job_description' 字段，无法生成词云。")
        return

    text = " ".join(df["job_description"].dropna())
    stopwords = set(["岗位", "要求", "负责", "相关", "工作", "经验"])
    words = extract_keywords(text, stopwords)
    word_freq = pd.Series(words).value_counts().to_dict()

    try:
        wordcloud = WordCloud(
            font_path=font_path,
            width=1000,
            height=600,
            background_color="white",
            collocations=False
        ).generate_from_frequencies(word_freq)

        plt.figure(figsize=(12, 6))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout()
        os.makedirs("output/figures", exist_ok=True)
        wordcloud.to_file("output/figures/wordcloud.png")
        plt.close()

        # 关键词柱状图
        top_words = pd.Series(word_freq).nlargest(50)
        plt.figure(figsize=(12, 6))
        ax = sns.barplot(x=top_words.values, y=top_words.index, palette="viridis")
        plt.title("职位描述中前50关键词频率")
        set_font_for_plot(ax, fm.FontProperties(fname=font_path))
        plt.xlabel("出现次数")
        plt.ylabel("关键词")
        plt.tight_layout()
        plt.savefig("output/figures/top50_keywords.png", dpi=300, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"生成词云或词频图时出错: {e}")

def plot_salary_range_distribution(df):
    bins = [0, 10000, 15000, 20000, 25000, float('inf')]
    labels = ['<10k', '10k-15k', '15k-20k', '20k-25k', '>25k']
    df = df.copy()
    df.loc[:, 'salary_range'] = pd.cut(df['avg_salary_k'] * 1000, bins=bins, labels=labels, right=False)
    salary_range_counts = df['salary_range'].value_counts().reindex(labels)

    plt.figure(figsize=(10, 6))
    ax = sns.lineplot(x=salary_range_counts.index, y=salary_range_counts.values,
                      marker="o", linewidth=2.5, color='tomato')

    plt.title("岗位平均薪资区间分布（千元/月）", fontsize=16, fontproperties=font_prop)
    plt.xlabel("平均薪资区间（元/月）", fontsize=12)
    plt.ylabel("岗位数量", fontsize=12)
    plt.ylim(0, salary_range_counts.max() + 10)

    set_font_for_plot(ax, font_prop)
    plt.tight_layout()
    plt.grid(True)
    plt.savefig("output/figures/salary_range_distribution_line.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_salary_overall(df):
    plt.figure(figsize=(8, 6))
    ax = sns.histplot(df["avg_salary_k"] * 1000, bins=25, kde=True, color='skyblue')
    plt.title("岗位平均薪资分布（整体，千元/月）", fontsize=16, fontproperties=font_prop)
    plt.xlabel("平均薪资（元/月）", fontsize=12)
    plt.ylabel("岗位数量", fontsize=12)
    set_font_for_plot(ax, font_prop)
    plt.tight_layout()
    plt.savefig("output/figures/salary_overall.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_city_job_distribution_line(df):
    os.makedirs("output/figures", exist_ok=True)
    city_job_counts = df['city'].value_counts().sort_index()
    plt.figure(figsize=(10, 6))
    ax = sns.lineplot(x=city_job_counts.index, y=city_job_counts.values,
                      marker='o', color='b', linewidth=2.5)
    plt.title("各城市岗位数量分布", fontsize=16, fontproperties=font_prop)
    plt.xlabel("城市", fontsize=12)
    plt.ylabel("岗位数量", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    set_font_for_plot(ax, font_prop)
    plt.tight_layout()
    plt.savefig("output/figures/city_job_distribution_line.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_salary_distribution_line(df):
    plt.figure(figsize=(10, 6))
    salary_counts = df["avg_salary_k"].value_counts().sort_index()
    ax = sns.lineplot(
        x=salary_counts.index,
        y=salary_counts.values,
        marker="o",
        color="green",
        linewidth=2.5
    )
    plt.title("岗位平均薪资分布（折线图，K/月）", fontsize=16, fontproperties=font_prop)
    plt.xlabel("平均薪资（K/月）", fontsize=12)
    plt.ylabel("岗位数量", fontsize=12)
    ax.set_ylim(0, salary_counts.max() * 1.2)
    ax.set_xlim(salary_counts.index.min(), salary_counts.index.max())
    set_font_for_plot(ax, font_prop)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("output/figures/salary_distribution_line.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_salary_range_pie_chart(df, city=None):
    df = df.copy()
    bins = [0, 10000, 15000, 20000, 25000, float('inf')]
    labels = ['<10k', '10k-15k', '15k-20k', '20k-25k', '>25k']
    if city:
        df = df[df["city"] == city]
    df.loc[:, "salary_range"] = pd.cut(df["avg_salary_k"] * 1000, bins=bins, labels=labels, right=False)
    salary_range_counts = df["salary_range"].value_counts().reindex(labels)

    plt.figure(figsize=(8, 8))
    plt.pie(salary_range_counts, labels=labels, autopct="%1.1f%%",
            colors=sns.color_palette("Set3", len(labels)))
    plt.title(f"{'城市 ' + city if city else '全部城市'}薪资区间分布", fontsize=16, fontproperties=font_prop)

    ax = plt.gca()
    set_font_for_plot(ax, font_prop)
    plt.tight_layout()
    filename = f"output/figures/salary_range_pie{'_' + city if city else ''}.png"
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


def plot_education_salary_comparison(df):
    """
    绘制大专、本科学历对应的平均薪资柱状图
    """
    if "education" not in df.columns or "avg_salary_k" not in df.columns:
        print("⚠️ 缺少 'education' 或 'avg_salary_k' 字段，无法绘图。")
        return

    # 过滤异常值并计算每个学历的平均薪资
    edu_salary = df[df["avg_salary_k"].between(2, 50)].groupby("education")["avg_salary_k"].mean()

    # 只保留大专、本科
    edu_order = ["大专", "本科"]
    edu_salary = edu_salary.reindex([e for e in edu_order if e in edu_salary.index])

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=edu_salary.index, y=edu_salary.values, palette="coolwarm")

    plt.title("大专及以上、本科及以上对应的平均薪资（千元/月）", fontsize=16, fontproperties=font_prop)
    plt.xlabel("学历", fontsize=12)
    plt.ylabel("平均薪资（K/月）", fontsize=12)

    for i, v in enumerate(edu_salary.values):
        ax.text(i, v + 0.3, f"{v:.1f}K", ha='center', fontproperties=font_prop)

    set_font_for_plot(ax, font_prop)
    plt.tight_layout()
    plt.savefig("output/figures/education_salary_comparison.png", dpi=300, bbox_inches='tight')
    plt.close()


# 屏蔽警告
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
