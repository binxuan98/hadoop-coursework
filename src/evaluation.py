# -*- coding: utf-8 -*-
"""
Project Evaluation Module for E-commerce Order Analysis
电商订单分析项目评估模块

This module contains functions for evaluating the quality and completeness
of the data analysis project.
本模块包含评估数据分析项目质量和完整性的函数。
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import os

# Import configuration
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import EVALUATION_WEIGHTS, CHARTS_DIR, REPORTS_DIR, PROCESSED_DATA_DIR

class ProjectEvaluator:
    """
    Project evaluation class for assessing data analysis quality
    项目评估类，用于评估数据分析质量
    """
    
    def __init__(self):
        """
        Initialize the ProjectEvaluator
        初始化项目评估器
        """
        self.logger = logging.getLogger(__name__)
        self.weights = EVALUATION_WEIGHTS
        self.evaluation_results = {}
        
    def evaluate_project(self, df: pd.DataFrame) -> float:
        """
        Evaluate the complete project
        评估完整项目
        
        Args:
            df: Cleaned DataFrame
        
        Returns:
            Overall project score (0-100)
        """
        self.logger.info("Starting project evaluation")
        
        # Evaluate each component
        data_cleaning_score = self.evaluate_data_cleaning(df)
        data_analysis_score = self.evaluate_data_analysis()
        visualization_score = self.evaluate_visualization()
        code_quality_score = self.evaluate_code_quality()
        report_writing_score = self.evaluate_report_writing()
        
        # Calculate weighted overall score
        overall_score = (
            data_cleaning_score * self.weights["data_cleaning"] +
            data_analysis_score * self.weights["data_analysis"] +
            visualization_score * self.weights["visualization"] +
            code_quality_score * self.weights["code_quality"] +
            report_writing_score * self.weights["report_writing"]
        )
        
        # Store evaluation results
        self.evaluation_results = {
            "overall_score": overall_score,
            "component_scores": {
                "data_cleaning": data_cleaning_score,
                "data_analysis": data_analysis_score,
                "visualization": visualization_score,
                "code_quality": code_quality_score,
                "report_writing": report_writing_score
            },
            "weights": self.weights,
            "evaluation_date": datetime.now().isoformat(),
            "detailed_feedback": self._generate_detailed_feedback()
        }
        
        # Save evaluation report
        self._save_evaluation_report()
        
        self.logger.info(f"Project evaluation completed. Overall score: {overall_score:.2f}/100")
        return overall_score
    
    def evaluate_data_cleaning(self, df: pd.DataFrame) -> float:
        """
        Evaluate data cleaning quality
        评估数据清洗质量
        
        Args:
            df: Cleaned DataFrame
        
        Returns:
            Data cleaning score (0-100)
        """
        self.logger.info("Evaluating data cleaning quality")
        
        score = 0
        max_score = 100
        
        # Check for missing values (20 points)
        missing_percentage = df.isnull().sum().sum() / (len(df) * len(df.columns))
        if missing_percentage == 0:
            score += 20
        elif missing_percentage < 0.01:
            score += 15
        elif missing_percentage < 0.05:
            score += 10
        else:
            score += 5
        
        # Check for duplicates (15 points)
        duplicate_percentage = df.duplicated().sum() / len(df)
        if duplicate_percentage == 0:
            score += 15
        elif duplicate_percentage < 0.01:
            score += 10
        else:
            score += 5
        
        # Check data types (15 points)
        correct_types = 0
        expected_types = {
            'order_date': 'datetime64[ns]',
            'quantity': ['int64', 'float64'],
            'unit_price': ['float64'],
            'total_amount': ['float64'],
            'customer_age': ['int64', 'float64']
        }
        
        for col, expected in expected_types.items():
            if col in df.columns:
                if isinstance(expected, list):
                    if str(df[col].dtype) in expected:
                        correct_types += 1
                else:
                    if str(df[col].dtype) == expected:
                        correct_types += 1
        
        score += (correct_types / len(expected_types)) * 15
        
        # Check for outliers handling (20 points)
        outlier_score = 0
        numerical_cols = ['quantity', 'unit_price', 'total_amount', 'customer_age']
        
        for col in numerical_cols:
            if col in df.columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                outlier_percentage = len(outliers) / len(df)
                
                if outlier_percentage < 0.05:  # Less than 5% outliers
                    outlier_score += 5
        
        score += outlier_score
        
        # Check for derived columns (15 points)
        derived_cols = ['order_year', 'order_month', 'order_quarter', 'order_weekday', 'age_group']
        derived_score = sum(1 for col in derived_cols if col in df.columns)
        score += (derived_score / len(derived_cols)) * 15
        
        # Check data consistency (15 points)
        consistency_score = 0
        
        # Check if total_amount = quantity * unit_price (approximately)
        if all(col in df.columns for col in ['total_amount', 'quantity', 'unit_price']):
            calculated_total = df['quantity'] * df['unit_price']
            difference = abs(df['total_amount'] - calculated_total)
            if (difference < 0.01).mean() > 0.95:  # 95% of records are consistent
                consistency_score += 15
            elif (difference < 0.1).mean() > 0.90:
                consistency_score += 10
            else:
                consistency_score += 5
        
        score += consistency_score
        
        return min(score, max_score)
    
    def evaluate_data_analysis(self) -> float:
        """
        Evaluate data analysis quality
        评估数据分析质量
        
        Returns:
            Data analysis score (0-100)
        """
        self.logger.info("Evaluating data analysis quality")
        
        score = 0
        max_score = 100
        
        # Check if analysis report exists (30 points)
        report_files = [
            REPORTS_DIR / "analysis_report.json",
            REPORTS_DIR / "analysis_report.md"
        ]
        
        existing_reports = sum(1 for file in report_files if file.exists())
        score += (existing_reports / len(report_files)) * 30
        
        # Check analysis completeness (40 points)
        if (REPORTS_DIR / "analysis_report.json").exists():
            try:
                with open(REPORTS_DIR / "analysis_report.json", 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                required_analyses = [
                    'basic_stats', 'time_analysis', 'customer_analysis', 'product_analysis'
                ]
                
                if 'detailed_analysis' in report_data:
                    completed_analyses = sum(1 for analysis in required_analyses 
                                           if analysis in report_data['detailed_analysis'])
                    score += (completed_analyses / len(required_analyses)) * 40
                
            except Exception as e:
                self.logger.warning(f"Error reading analysis report: {e}")
        
        # Check analysis depth (30 points)
        # This is a simplified check - in practice, you might want more sophisticated metrics
        if (REPORTS_DIR / "analysis_report.json").exists():
            try:
                with open(REPORTS_DIR / "analysis_report.json", 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                depth_indicators = [
                    'executive_summary',
                    'recommendations',
                    'detailed_analysis'
                ]
                
                depth_score = sum(1 for indicator in depth_indicators 
                                if indicator in report_data and report_data[indicator])
                score += (depth_score / len(depth_indicators)) * 30
                
            except Exception as e:
                self.logger.warning(f"Error evaluating analysis depth: {e}")
        
        return min(score, max_score)
    
    def evaluate_visualization(self) -> float:
        """
        Evaluate visualization quality
        评估可视化质量
        
        Returns:
            Visualization score (0-100)
        """
        self.logger.info("Evaluating visualization quality")
        
        score = 0
        max_score = 100
        
        # Check if visualization files exist (50 points)
        expected_charts = [
            "sales_trend.png",
            "category_distribution.png",
            "customer_demographics.png",
            "top_products.png",
            "correlation_matrix.png",
            "seasonal_analysis.png"
        ]
        
        existing_charts = sum(1 for chart in expected_charts 
                            if (CHARTS_DIR / chart).exists())
        score += (existing_charts / len(expected_charts)) * 50
        
        # Check for interactive dashboard (25 points)
        if (CHARTS_DIR / "interactive_dashboard.html").exists():
            score += 25
        
        # Check chart file sizes (reasonable quality) (25 points)
        size_score = 0
        for chart in expected_charts:
            chart_path = CHARTS_DIR / chart
            if chart_path.exists():
                file_size = chart_path.stat().st_size
                if 50000 < file_size < 2000000:  # Between 50KB and 2MB
                    size_score += 1
        
        if expected_charts:
            score += (size_score / len(expected_charts)) * 25
        
        return min(score, max_score)
    
    def evaluate_code_quality(self) -> float:
        """
        Evaluate code quality
        评估代码质量
        
        Returns:
            Code quality score (0-100)
        """
        self.logger.info("Evaluating code quality")
        
        score = 0
        max_score = 100
        
        # Check if all required modules exist (40 points)
        required_modules = [
            "src/data_utils.py",
            "src/analysis.py",
            "src/visualization.py",
            "src/evaluation.py",
            "main.py",
            "config.py"
        ]
        
        project_root = Path(__file__).parent.parent
        existing_modules = sum(1 for module in required_modules 
                             if (project_root / module).exists())
        score += (existing_modules / len(required_modules)) * 40
        
        # Check for proper documentation (30 points)
        # This is a simplified check - count docstrings and comments
        documentation_score = 0
        
        for module_path in required_modules:
            full_path = project_root / module_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Count docstrings and comments
                    docstring_count = content.count('"""')
                    comment_count = content.count('#')
                    
                    if docstring_count >= 2 and comment_count >= 5:
                        documentation_score += 1
                        
                except Exception as e:
                    self.logger.warning(f"Error reading {module_path}: {e}")
        
        if required_modules:
            score += (documentation_score / len(required_modules)) * 30
        
        # Check for error handling (30 points)
        error_handling_score = 0
        
        for module_path in required_modules:
            full_path = project_root / module_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for try-except blocks
                    if 'try:' in content and 'except' in content:
                        error_handling_score += 1
                        
                except Exception as e:
                    self.logger.warning(f"Error reading {module_path}: {e}")
        
        if required_modules:
            score += (error_handling_score / len(required_modules)) * 30
        
        return min(score, max_score)
    
    def evaluate_report_writing(self) -> float:
        """
        Evaluate report writing quality
        评估报告撰写质量
        
        Returns:
            Report writing score (0-100)
        """
        self.logger.info("Evaluating report writing quality")
        
        score = 0
        max_score = 100
        
        # Check if README exists and is comprehensive (40 points)
        readme_path = Path(__file__).parent.parent / "README.md"
        if readme_path.exists():
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                
                required_sections = [
                    '项目简介', '安装', '运行', '数据说明', '分析内容', '评分标准'
                ]
                
                section_score = sum(1 for section in required_sections 
                                  if section in readme_content)
                score += (section_score / len(required_sections)) * 40
                
            except Exception as e:
                self.logger.warning(f"Error reading README: {e}")
        
        # Check if analysis report exists and has proper structure (40 points)
        if (REPORTS_DIR / "analysis_report.md").exists():
            try:
                with open(REPORTS_DIR / "analysis_report.md", 'r', encoding='utf-8') as f:
                    report_content = f.read()
                
                required_elements = [
                    'Executive Summary', 'Key Metrics', 'Insights', 'Recommendations'
                ]
                
                element_score = sum(1 for element in required_elements 
                                  if element in report_content)
                score += (element_score / len(required_elements)) * 40
                
            except Exception as e:
                self.logger.warning(f"Error reading analysis report: {e}")
        
        # Check for proper formatting and language (20 points)
        # This is a simplified check based on file length and structure
        if readme_path.exists():
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for proper markdown formatting
                if content.count('#') >= 5 and content.count('```') >= 2:
                    score += 20
                elif content.count('#') >= 3:
                    score += 15
                else:
                    score += 10
                    
            except Exception as e:
                self.logger.warning(f"Error evaluating formatting: {e}")
        
        return min(score, max_score)
    
    def _generate_detailed_feedback(self) -> Dict:
        """
        Generate detailed feedback for each component
        为每个组件生成详细反馈
        
        Returns:
            Dictionary containing detailed feedback
        """
        feedback = {
            "data_cleaning": {
                "strengths": [],
                "improvements": [],
                "recommendations": []
            },
            "data_analysis": {
                "strengths": [],
                "improvements": [],
                "recommendations": []
            },
            "visualization": {
                "strengths": [],
                "improvements": [],
                "recommendations": []
            },
            "code_quality": {
                "strengths": [],
                "improvements": [],
                "recommendations": []
            },
            "report_writing": {
                "strengths": [],
                "improvements": [],
                "recommendations": []
            }
        }
        
        # Generate feedback based on scores
        scores = self.evaluation_results.get("component_scores", {})
        
        for component, score in scores.items():
            if score >= 90:
                feedback[component]["strengths"].append("Excellent work in this area")
            elif score >= 80:
                feedback[component]["strengths"].append("Good performance with room for minor improvements")
            elif score >= 70:
                feedback[component]["improvements"].append("Satisfactory but needs improvement")
            else:
                feedback[component]["improvements"].append("Significant improvement needed")
        
        # Add specific recommendations
        feedback["data_cleaning"]["recommendations"] = [
            "Ensure all missing values are properly handled",
            "Remove or handle outliers appropriately",
            "Validate data consistency across related fields",
            "Create meaningful derived variables"
        ]
        
        feedback["data_analysis"]["recommendations"] = [
            "Perform comprehensive statistical analysis",
            "Include trend analysis and forecasting",
            "Conduct customer segmentation analysis",
            "Provide actionable business insights"
        ]
        
        feedback["visualization"]["recommendations"] = [
            "Create clear and informative charts",
            "Use appropriate chart types for different data",
            "Include interactive visualizations",
            "Ensure charts are properly labeled and formatted"
        ]
        
        feedback["code_quality"]["recommendations"] = [
            "Write clean, well-documented code",
            "Include proper error handling",
            "Follow Python coding standards",
            "Create modular and reusable functions"
        ]
        
        feedback["report_writing"]["recommendations"] = [
            "Write clear and comprehensive documentation",
            "Include executive summary and key findings",
            "Provide actionable recommendations",
            "Use proper formatting and structure"
        ]
        
        return feedback
    
    def _save_evaluation_report(self) -> None:
        """
        Save evaluation report to file
        保存评估报告到文件
        """
        try:
            # Ensure reports directory exists
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            
            # Save JSON report
            json_path = REPORTS_DIR / "evaluation_report.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.evaluation_results, f, indent=2, ensure_ascii=False, default=str)
            
            # Generate and save markdown report
            markdown_report = self._generate_evaluation_markdown()
            markdown_path = REPORTS_DIR / "evaluation_report.md"
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_report)
            
            self.logger.info(f"Evaluation reports saved: {json_path}, {markdown_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving evaluation report: {e}")
    
    def _generate_evaluation_markdown(self) -> str:
        """
        Generate markdown evaluation report
        生成Markdown评估报告
        
        Returns:
            Markdown formatted evaluation report
        """
        scores = self.evaluation_results["component_scores"]
        overall_score = self.evaluation_results["overall_score"]
        
        # Determine grade
        if overall_score >= 90:
            grade = "A (优秀)"
        elif overall_score >= 80:
            grade = "B (良好)"
        elif overall_score >= 70:
            grade = "C (中等)"
        elif overall_score >= 60:
            grade = "D (及格)"
        else:
            grade = "F (不及格)"
        
        markdown = f"""
# Project Evaluation Report
# 项目评估报告

**Evaluation Date / 评估日期:** {self.evaluation_results['evaluation_date']}

## Overall Score / 总体得分

**Score / 得分:** {overall_score:.2f}/100

**Grade / 等级:** {grade}

## Component Scores / 各组件得分

| Component / 组件 | Score / 得分 | Weight / 权重 | Weighted Score / 加权得分 |
|------------------|--------------|---------------|---------------------------|
| Data Cleaning / 数据清洗 | {scores['data_cleaning']:.1f} | {self.weights['data_cleaning']:.0%} | {scores['data_cleaning'] * self.weights['data_cleaning']:.1f} |
| Data Analysis / 数据分析 | {scores['data_analysis']:.1f} | {self.weights['data_analysis']:.0%} | {scores['data_analysis'] * self.weights['data_analysis']:.1f} |
| Visualization / 可视化 | {scores['visualization']:.1f} | {self.weights['visualization']:.0%} | {scores['visualization'] * self.weights['visualization']:.1f} |
| Code Quality / 代码质量 | {scores['code_quality']:.1f} | {self.weights['code_quality']:.0%} | {scores['code_quality'] * self.weights['code_quality']:.1f} |
| Report Writing / 报告撰写 | {scores['report_writing']:.1f} | {self.weights['report_writing']:.0%} | {scores['report_writing'] * self.weights['report_writing']:.1f} |

## Performance Analysis / 表现分析

### Strengths / 优势
"""
        
        # Add strengths based on high scores
        for component, score in scores.items():
            if score >= 80:
                component_name = {
                    'data_cleaning': 'Data Cleaning / 数据清洗',
                    'data_analysis': 'Data Analysis / 数据分析',
                    'visualization': 'Visualization / 可视化',
                    'code_quality': 'Code Quality / 代码质量',
                    'report_writing': 'Report Writing / 报告撰写'
                }[component]
                markdown += f"- **{component_name}**: Excellent performance ({score:.1f}/100)\n"
        
        markdown += "\n### Areas for Improvement / 需要改进的领域\n\n"
        
        # Add improvement areas based on low scores
        for component, score in scores.items():
            if score < 80:
                component_name = {
                    'data_cleaning': 'Data Cleaning / 数据清洗',
                    'data_analysis': 'Data Analysis / 数据分析',
                    'visualization': 'Visualization / 可视化',
                    'code_quality': 'Code Quality / 代码质量',
                    'report_writing': 'Report Writing / 报告撰写'
                }[component]
                markdown += f"- **{component_name}**: Needs improvement ({score:.1f}/100)\n"
        
        markdown += """

## Recommendations / 建议

1. **Focus on weak areas / 专注于薄弱环节**: Prioritize improving components with scores below 80
2. **Code documentation / 代码文档**: Ensure all functions have proper docstrings and comments
3. **Data validation / 数据验证**: Implement comprehensive data quality checks
4. **Visualization enhancement / 可视化增强**: Create more interactive and informative charts
5. **Report completeness / 报告完整性**: Include all required sections in analysis reports

---

*This evaluation was automatically generated by the Project Evaluation System.*

*本评估由项目评估系统自动生成。*
"""
        
        return markdown
    
    def get_evaluation_summary(self) -> Dict:
        """
        Get a summary of the evaluation results
        获取评估结果摘要
        
        Returns:
            Dictionary containing evaluation summary
        """
        if not self.evaluation_results:
            return {"error": "No evaluation has been performed yet"}
        
        return {
            "overall_score": self.evaluation_results["overall_score"],
            "grade": self._get_grade(self.evaluation_results["overall_score"]),
            "component_scores": self.evaluation_results["component_scores"],
            "evaluation_date": self.evaluation_results["evaluation_date"]
        }
    
    def _get_grade(self, score: float) -> str:
        """
        Convert numerical score to letter grade
        将数字分数转换为字母等级
        
        Args:
            score: Numerical score (0-100)
        
        Returns:
            Letter grade with Chinese translation
        """
        if score >= 90:
            return "A (优秀)"
        elif score >= 80:
            return "B (良好)"
        elif score >= 70:
            return "C (中等)"
        elif score >= 60:
            return "D (及格)"
        else:
            return "F (不及格)"