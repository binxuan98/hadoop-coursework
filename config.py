# -*- coding: utf-8 -*-
"""
Configuration file for E-commerce Order Analysis Project
电商订单分析项目配置文件
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Output directories
OUTPUT_DIR = PROJECT_ROOT / "output"
CHARTS_DIR = OUTPUT_DIR / "charts"
REPORTS_DIR = OUTPUT_DIR / "reports"

# Source code directory
SRC_DIR = PROJECT_ROOT / "src"

# Notebook directory
NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, 
                  OUTPUT_DIR, CHARTS_DIR, REPORTS_DIR, SRC_DIR, NOTEBOOK_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Data file paths
SAMPLE_DATA_FILE = RAW_DATA_DIR / "sample_orders.csv"
PROCESSED_DATA_FILE = PROCESSED_DATA_DIR / "cleaned_orders.csv"

# Analysis parameters
ANALYSIS_CONFIG = {
    "date_format": "%Y-%m-%d",
    "currency_symbol": "¥",
    "default_figsize": (12, 8),
    "color_palette": "viridis",
    "random_seed": 42
}

# Visualization settings
VIZ_CONFIG = {
    "figure_size": (12, 8),
    "dpi": 300,
    "style": "whitegrid",
    "palette": "Set2",
    "font_size": 12,
    "title_size": 16,
    "label_size": 14
}

# Data generation parameters (for sample data)
DATA_GENERATION_CONFIG = {
    "num_orders": 10000,
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "num_customers": 2000,
    "product_categories": [
        "Electronics", "Clothing", "Books", "Home & Garden", 
        "Sports", "Beauty", "Toys", "Food", "Health", "Automotive"
    ],
    "cities": [
        "北京", "上海", "广州", "深圳", "杭州", "南京", "武汉", 
        "成都", "西安", "重庆", "天津", "苏州", "长沙", "郑州", "青岛"
    ]
}

# Evaluation criteria weights
EVALUATION_WEIGHTS = {
    "data_cleaning": 0.20,
    "data_analysis": 0.30,
    "visualization": 0.25,
    "code_quality": 0.15,
    "report_writing": 0.10
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": OUTPUT_DIR / "analysis.log"
}