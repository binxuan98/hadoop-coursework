#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for E-commerce Order Analysis Project
电商订单分析项目主程序

Author: Your Name
Date: 2024
Description: This is the main script to run the complete e-commerce order analysis.
"""

import sys
import logging
from pathlib import Path
import joblib

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from config import *
from src.data_utils import DataProcessor
from src.analysis import OrderAnalyzer
from src.visualization import DataVisualizer
from src.evaluation import ProjectEvaluator

def setup_logging():
    """
    Setup logging configuration
    设置日志配置
    """
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG["level"]),
        format=LOGGING_CONFIG["format"],
        handlers=[
            logging.FileHandler(LOGGING_CONFIG["log_file"]),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def main():
    """
    Main function to run the complete analysis pipeline
    主函数：运行完整的分析流程
    """
    logger = setup_logging()
    logger.info("Starting E-commerce Order Analysis Project")
    logger.info("开始电商订单分析项目")
    
    try:
        # Step 1: Data Processing
        logger.info("Step 1: Data Processing / 步骤1：数据处理")
        processor = DataProcessor()
        
        # Generate sample data if not exists
        if not SAMPLE_DATA_FILE.exists():
            logger.info("Generating sample data / 生成示例数据")
            processor.generate_sample_data(output_file=SAMPLE_DATA_FILE)
        
        # Add cache mechanism
        if PROCESSED_DATA_FILE.exists():
            logger.info("Loading processed data from cache / 从缓存加载已处理数据")
            try:
                df = joblib.load(PROCESSED_DATA_FILE)
            except Exception as e:
                logger.warning(f"Failed to load cached data: {str(e)}. Loading and cleaning data from scratch. / 加载缓存数据失败: {str(e)}。重新加载和清洗数据。")
                df = processor.load_data(SAMPLE_DATA_FILE)
                cleaned_df = processor.clean_data(df)
                processor.save_data(cleaned_df, PROCESSED_DATA_FILE)
        else:
            # Load and clean data
            logger.info("Loading and cleaning data / 加载和清洗数据")
            df = processor.load_data(SAMPLE_DATA_FILE)
            cleaned_df = processor.clean_data(df)
            processor.save_data(cleaned_df, PROCESSED_DATA_FILE)
        
        # Step 2: Data Analysis
        logger.info("Step 2: Data Analysis / 步骤2：数据分析")
        analyzer = OrderAnalyzer(cleaned_df)
        
        # Perform various analyses
        basic_stats = analyzer.basic_statistics()
        time_analysis = analyzer.time_series_analysis()
        customer_analysis = analyzer.customer_analysis()
        product_analysis = analyzer.product_analysis()
        
        # Step 3: Data Visualization
        logger.info("Step 3: Data Visualization / 步骤3：数据可视化")
        visualizer = DataVisualizer(cleaned_df)
        
        # Generate visualizations
        visualizer.plot_sales_trend()
        visualizer.plot_category_distribution()
        visualizer.plot_customer_demographics()
        visualizer.plot_top_products()
        visualizer.plot_correlation_matrix()
        
        # Step 4: Generate Report
        logger.info("Step 4: Generate Report / 步骤4：生成报告")
        analyzer.generate_report({
            "basic_stats": basic_stats,
            "time_analysis": time_analysis,
            "customer_analysis": customer_analysis,
            "product_analysis": product_analysis
        })
        
        # Step 5: Project Evaluation
        logger.info("Step 5: Project Evaluation / 步骤5：项目评估")
        evaluator = ProjectEvaluator()
        evaluation_score = evaluator.evaluate_project(cleaned_df)
        
        logger.info(f"Analysis completed successfully! / 分析成功完成！")
        logger.info(f"Project evaluation score: {evaluation_score:.2f}/100")
        logger.info(f"项目评估得分: {evaluation_score:.2f}/100")
        
        print("\n" + "="*60)
        print("🎉 E-COMMERCE ORDER ANALYSIS COMPLETED! 🎉")
        print("🎉 电商订单分析完成！ 🎉")
        print("="*60)
        print(f"📊 Total orders processed: {len(cleaned_df):,}")
        print(f"📊 处理的订单总数: {len(cleaned_df):,}")
        print(f"📈 Project score: {evaluation_score:.2f}/100")
        print(f"📈 项目得分: {evaluation_score:.2f}/100")
        print(f"📁 Results saved to: {OUTPUT_DIR}")
        print(f"📁 结果保存至: {OUTPUT_DIR}")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Error occurred during analysis: {str(e)}")
        logger.error(f"分析过程中发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()