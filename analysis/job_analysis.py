import pandas as pd
import json
import re
import os


def load_and_clean_data(path="data/jobs_raw.json"):
    with open(path, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    df = pd.DataFrame(jobs)

    # 列重命名
    df = df.rename(columns={
        "岗位名称": "title",
        "公司名称": "company",
        "城市": "city",
        "薪资": "salary",
        "经验要求": "experience",
        "学历要求": "education",
        "职位标签": "tags",
        "职位要求": "job_description"
    })

    # 统一薪资单位（元 -> 千元）
    def parse_salary_bounds(s):
        match = re.findall(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", s)
        if match:
            low, high = map(float, match[0])
            if "万" in s:
                low *= 10
                high *= 10
            elif "元" in s:
                low /= 1000
                high /= 1000
            return low, high
        return None, None

    df[["salary_low", "salary_high"]] = df["salary"].apply(
        lambda x: pd.Series(parse_salary_bounds(x))
    )

    # 平均薪资（K/月）
    df["avg_salary_k"] = df[["salary_low", "salary_high"]].mean(axis=1)

    # 删除 avg_salary_k 异常值（过低或过高）
    df = df[df["avg_salary_k"].between(2, 50)]

    # 薪资区间比例分摊
    def assign_salary_segments(row):
        segments = {"0-10k": 0, "10k-15k": 0, "15k-20k": 0, "20k-25k": 0, "25k+": 0}
        low, high = row["salary_low"], row["salary_high"]
        if pd.isna(low) or pd.isna(high):
            return segments

        ranges = [
            ("0-10k", 0, 10),
            ("10k-15k", 10, 15),
            ("15k-20k", 15, 20),
            ("20k-25k", 20, 25),
            ("25k+", 25, 100)
        ]
        total_span = high - low
        if total_span <= 0:
            return segments

        for label, r_low, r_high in ranges:
            overlap = max(0, min(high, r_high) - max(low, r_low))
            if overlap > 0:
                segments[label] = round(overlap / total_span, 4)

        return segments

    seg_df = df.apply(assign_salary_segments, axis=1, result_type="expand")
    df = pd.concat([df, seg_df], axis=1)

    os.makedirs("output", exist_ok=True)
    df.to_csv("output/job_analysis_summary.csv", index=False)

    return df
