# -*- coding: utf-8 -*-
"""
E-commerce Order Analysis Project
电商订单分析项目

This package contains modules for data processing, analysis, and visualization
of e-commerce order data.

本包包含电商订单数据处理、分析和可视化的模块。
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "E-commerce Order Analysis Project for College Students"

# Import main classes for easy access
from .data_utils import DataProcessor
from .analysis import OrderAnalyzer
from .visualization import DataVisualizer
from .evaluation import ProjectEvaluator

__all__ = [
    "DataProcessor",
    "OrderAnalyzer", 
    "DataVisualizer",
    "ProjectEvaluator"
]