# -*- coding: utf-8 -*-
"""
Data Analysis Module for E-commerce Order Analysis
电商订单分析数据分析模块

This module contains classes and functions for performing various analyses
on e-commerce order data.
本模块包含对电商订单数据进行各种分析的类和函数。
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
import json

# Import configuration
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import REPORTS_DIR, ANALYSIS_CONFIG

class OrderAnalyzer:
    """
    Order analysis class for e-commerce data
    电商数据订单分析类
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the OrderAnalyzer
        初始化订单分析器
        
        Args:
            df: DataFrame containing order data
        """
        self.df = df.copy()
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"OrderAnalyzer initialized with {len(df)} orders")
    
    def basic_statistics(self) -> Dict:
        """
        Calculate basic statistics of the order data
        计算订单数据的基本统计信息
        
        Returns:
            Dictionary containing basic statistics
        """
        self.logger.info("Calculating basic statistics")
        
        stats = {
            "total_orders": len(self.df),
            "total_revenue": self.df['total_amount'].sum(),
            "average_order_value": self.df['total_amount'].mean(),
            "median_order_value": self.df['total_amount'].median(),
            "total_customers": self.df['customer_id'].nunique(),
            "total_products": self.df['product_name'].nunique(),
            "total_categories": self.df['product_category'].nunique(),
            "date_range": {
                "start": self.df['order_date'].min().strftime('%Y-%m-%d'),
                "end": self.df['order_date'].max().strftime('%Y-%m-%d')
            },
            "revenue_statistics": {
                "min": self.df['total_amount'].min(),
                "max": self.df['total_amount'].max(),
                "std": self.df['total_amount'].std(),
                "q25": self.df['total_amount'].quantile(0.25),
                "q75": self.df['total_amount'].quantile(0.75)
            },
            "quantity_statistics": {
                "total_items_sold": self.df['quantity'].sum(),
                "average_quantity_per_order": self.df['quantity'].mean(),
                "max_quantity_in_order": self.df['quantity'].max()
            }
        }
        
        self.logger.info(f"Basic statistics calculated: {stats['total_orders']} orders, "
                        f"{stats['total_revenue']:.2f} total revenue")
        
        return stats
    
    def time_series_analysis(self) -> Dict:
        """
        Perform time series analysis on order data
        对订单数据进行时间序列分析
        
        Returns:
            Dictionary containing time series analysis results
        """
        self.logger.info("Performing time series analysis")
        
        # Daily sales
        daily_sales = self.df.groupby('order_date').agg({
            'total_amount': 'sum',
            'order_id': 'count'
        }).rename(columns={'order_id': 'order_count'})
        
        # Monthly sales
        monthly_sales = self.df.groupby(['order_year', 'order_month']).agg({
            'total_amount': 'sum',
            'order_id': 'count'
        }).rename(columns={'order_id': 'order_count'})
        
        # Quarterly sales
        quarterly_sales = self.df.groupby(['order_year', 'order_quarter']).agg({
            'total_amount': 'sum',
            'order_id': 'count'
        }).rename(columns={'order_id': 'order_count'})
        
        # Weekday analysis
        weekday_sales = self.df.groupby('order_weekday').agg({
            'total_amount': ['sum', 'mean', 'count']
        })
        weekday_sales.columns = ['total_revenue', 'avg_order_value', 'order_count']
        
        # Growth analysis
        monthly_growth = monthly_sales['total_amount'].pct_change().fillna(0)
        
        # Seasonal analysis
        seasonal_analysis = self.df.groupby('order_month').agg({
            'total_amount': ['sum', 'mean', 'count']
        })
        seasonal_analysis.columns = ['total_revenue', 'avg_order_value', 'order_count']
        
        analysis_results = {
            "daily_sales_summary": {
                "avg_daily_revenue": daily_sales['total_amount'].mean(),
                "max_daily_revenue": daily_sales['total_amount'].max(),
                "min_daily_revenue": daily_sales['total_amount'].min(),
                "avg_daily_orders": daily_sales['order_count'].mean()
            },
            "monthly_sales_summary": {
                "best_month": monthly_sales['total_amount'].idxmax(),
                "worst_month": monthly_sales['total_amount'].idxmin(),
                "avg_monthly_revenue": monthly_sales['total_amount'].mean(),
                "monthly_growth_rate": monthly_growth.mean()
            },
            "weekday_patterns": {
                "best_weekday": weekday_sales['total_revenue'].idxmax(),
                "worst_weekday": weekday_sales['total_revenue'].idxmin(),
                "weekday_revenue_ratio": (weekday_sales['total_revenue'].max() / 
                                        weekday_sales['total_revenue'].min())
            },
            "seasonal_trends": {
                "peak_season_month": seasonal_analysis['total_revenue'].idxmax(),
                "low_season_month": seasonal_analysis['total_revenue'].idxmin(),
                "seasonal_variation": seasonal_analysis['total_revenue'].std()
            }
        }
        
        return analysis_results
    
    def customer_analysis(self) -> Dict:
        """
        Perform customer analysis
        进行客户分析
        
        Returns:
            Dictionary containing customer analysis results
        """
        self.logger.info("Performing customer analysis")
        
        # Customer value analysis
        customer_stats = self.df.groupby('customer_id').agg({
            'total_amount': ['sum', 'mean', 'count'],
            'quantity': 'sum',
            'order_date': ['min', 'max']
        })
        
        customer_stats.columns = ['total_spent', 'avg_order_value', 'order_count', 
                                'total_quantity', 'first_order', 'last_order']
        
        # Customer lifetime value (CLV) calculation
        customer_stats['customer_lifetime_days'] = (
            customer_stats['last_order'] - customer_stats['first_order']
        ).dt.days + 1
        
        # Customer segmentation based on RFM analysis
        # Recency: days since last order
        max_date = self.df['order_date'].max()
        customer_stats['recency'] = (max_date - customer_stats['last_order']).dt.days
        
        # Frequency: number of orders
        customer_stats['frequency'] = customer_stats['order_count']
        
        # Monetary: total amount spent
        customer_stats['monetary'] = customer_stats['total_spent']
        
        # Create RFM scores (1-5 scale)
        customer_stats['r_score'] = pd.qcut(customer_stats['recency'], 5, 
                                          labels=[5,4,3,2,1])  # Lower recency = higher score
        customer_stats['f_score'] = pd.qcut(customer_stats['frequency'].rank(method='first'), 5, 
                                          labels=[1,2,3,4,5])
        customer_stats['m_score'] = pd.qcut(customer_stats['monetary'], 5, 
                                          labels=[1,2,3,4,5])
        
        # Demographics analysis
        gender_analysis = self.df.groupby('customer_gender').agg({
            'total_amount': ['sum', 'mean', 'count'],
            'customer_id': 'nunique'
        })
        
        age_group_analysis = self.df.groupby('age_group').agg({
            'total_amount': ['sum', 'mean', 'count'],
            'customer_id': 'nunique'
        })
        
        city_analysis = self.df.groupby('customer_city').agg({
            'total_amount': ['sum', 'mean', 'count'],
            'customer_id': 'nunique'
        }).sort_values(('total_amount', 'sum'), ascending=False)
        
        analysis_results = {
            "customer_value_metrics": {
                "total_customers": len(customer_stats),
                "avg_customer_value": customer_stats['total_spent'].mean(),
                "top_10_percent_value": customer_stats['total_spent'].quantile(0.9),
                "customer_retention_rate": (customer_stats['order_count'] > 1).mean(),
                "avg_orders_per_customer": customer_stats['order_count'].mean(),
                "repeat_customer_percentage": (customer_stats['order_count'] > 1).sum() / len(customer_stats) * 100
            },
            "top_customers": {
                "by_revenue": customer_stats.nlargest(10, 'total_spent')[['total_spent', 'order_count']].to_dict('index'),
                "by_frequency": customer_stats.nlargest(10, 'order_count')[['total_spent', 'order_count']].to_dict('index')
            },
            "demographic_insights": {
                "gender_distribution": self._flatten_multiindex_dict(gender_analysis.to_dict()),
                "age_group_distribution": self._flatten_multiindex_dict(age_group_analysis.to_dict()),
                "top_cities": self._flatten_multiindex_dict(city_analysis.head(10).to_dict()),
                "most_valuable_gender": gender_analysis[('total_amount', 'sum')].idxmax(),
                "most_valuable_age_group": age_group_analysis[('total_amount', 'sum')].idxmax(),
                "most_valuable_city": city_analysis[('total_amount', 'sum')].idxmax()
            },
            "rfm_analysis": {
                "high_value_customers": len(customer_stats[
                    (customer_stats['r_score'].astype(int) >= 4) & 
                    (customer_stats['f_score'].astype(int) >= 4) & 
                    (customer_stats['m_score'].astype(int) >= 4)
                ]),
                "at_risk_customers": len(customer_stats[
                    (customer_stats['r_score'].astype(int) <= 2) & 
                    (customer_stats['f_score'].astype(int) >= 3)
                ]),
                "new_customers": len(customer_stats[customer_stats['order_count'] == 1])
            }
        }
        
        return analysis_results
    
    def _flatten_multiindex_dict(self, multiindex_dict: Dict) -> Dict:
        """
        Flatten MultiIndex dictionary to avoid tuple keys in JSON serialization
        将MultiIndex字典扁平化以避免JSON序列化中的tuple键
        """
        flattened = {}
        for key, value in multiindex_dict.items():
            if isinstance(key, tuple):
                # Convert tuple key to string
                new_key = '_'.join(str(k) for k in key)
                flattened[new_key] = value
            else:
                flattened[key] = value
        return flattened
    
    def product_analysis(self) -> Dict:
        """
        Perform product and category analysis
        进行产品和类别分析
        
        Returns:
            Dictionary containing product analysis results
        """
        self.logger.info("Performing product analysis")
        
        # Product performance analysis
        product_stats = self.df.groupby('product_name').agg({
            'total_amount': ['sum', 'mean', 'count'],
            'quantity': 'sum',
            'unit_price': 'mean'
        })
        product_stats.columns = ['total_revenue', 'avg_order_value', 'order_count', 
                               'total_quantity_sold', 'avg_unit_price']
        
        # Category analysis
        category_stats = self.df.groupby('product_category').agg({
            'total_amount': ['sum', 'mean', 'count'],
            'quantity': 'sum',
            'product_name': 'nunique',
            'customer_id': 'nunique'
        })
        category_stats.columns = ['total_revenue', 'avg_order_value', 'order_count',
                                'total_quantity_sold', 'unique_products', 'unique_customers']
        
        # Price analysis
        price_analysis = self.df.groupby('product_category')['unit_price'].agg([
            'mean', 'median', 'min', 'max', 'std'
        ])
        
        # Product popularity and profitability
        product_performance = product_stats.copy()
        product_performance['revenue_per_order'] = (product_performance['total_revenue'] / 
                                                   product_performance['order_count'])
        product_performance['popularity_score'] = product_performance['order_count']
        product_performance['profitability_score'] = product_performance['total_revenue']
        
        # Category market share
        category_market_share = category_stats['total_revenue'] / category_stats['total_revenue'].sum() * 100
        
        analysis_results = {
            "product_performance": {
                "total_products": len(product_stats),
                "top_products_by_revenue": product_stats.nlargest(10, 'total_revenue').to_dict('index'),
                "top_products_by_quantity": product_stats.nlargest(10, 'total_quantity_sold').to_dict('index'),
                "most_popular_products": product_stats.nlargest(10, 'order_count').to_dict('index'),
                "highest_priced_products": product_stats.nlargest(10, 'avg_unit_price').to_dict('index')
            },
            "category_analysis": {
                "total_categories": len(category_stats),
                "category_revenue_ranking": category_stats.sort_values('total_revenue', ascending=False).to_dict('index'),
                "category_market_share": category_market_share.to_dict(),
                "most_profitable_category": category_stats['total_revenue'].idxmax(),
                "most_popular_category": category_stats['order_count'].idxmax(),
                "category_diversity": category_stats['unique_products'].to_dict()
            },
            "pricing_insights": {
                "price_analysis_by_category": price_analysis.to_dict('index'),
                "overall_avg_price": self.df['unit_price'].mean(),
                "price_range": {
                    "min": self.df['unit_price'].min(),
                    "max": self.df['unit_price'].max()
                },
                "most_expensive_category": price_analysis['mean'].idxmax(),
                "most_affordable_category": price_analysis['mean'].idxmin()
            },
            "inventory_insights": {
                "fast_moving_products": product_stats[product_stats['total_quantity_sold'] > 
                                                     product_stats['total_quantity_sold'].quantile(0.8)].index.tolist(),
                "slow_moving_products": product_stats[product_stats['total_quantity_sold'] < 
                                                     product_stats['total_quantity_sold'].quantile(0.2)].index.tolist(),
                "avg_quantity_per_order": self.df['quantity'].mean()
            }
        }
        
        return analysis_results
    
    def generate_report(self, analysis_results: Dict) -> None:
        """
        Generate comprehensive analysis report
        生成综合分析报告
        
        Args:
            analysis_results: Dictionary containing all analysis results
        """
        self.logger.info("Generating comprehensive analysis report")
        
        report_content = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "data_period": {
                    "start": self.df['order_date'].min().isoformat(),
                    "end": self.df['order_date'].max().isoformat()
                },
                "total_records_analyzed": len(self.df)
            },
            "executive_summary": self._generate_executive_summary(analysis_results),
            "detailed_analysis": analysis_results,
            "recommendations": self._generate_recommendations(analysis_results)
        }
        
        # Save JSON report
        json_report_path = REPORTS_DIR / "analysis_report.json"
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(report_content, f, indent=2, ensure_ascii=False, default=str)
        
        # Generate markdown report
        markdown_report = self._generate_markdown_report(report_content)
        markdown_report_path = REPORTS_DIR / "analysis_report.md"
        with open(markdown_report_path, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        self.logger.info(f"Reports generated: {json_report_path}, {markdown_report_path}")
    
    def _generate_executive_summary(self, analysis_results: Dict) -> Dict:
        """
        Generate executive summary from analysis results
        从分析结果生成执行摘要
        """
        basic_stats = analysis_results['basic_stats']
        customer_analysis = analysis_results['customer_analysis']
        product_analysis = analysis_results['product_analysis']
        
        return {
            "key_metrics": {
                "total_revenue": f"{basic_stats['total_revenue']:,.2f}",
                "total_orders": f"{basic_stats['total_orders']:,}",
                "average_order_value": f"{basic_stats['average_order_value']:.2f}",
                "total_customers": f"{basic_stats['total_customers']:,}",
                "customer_retention_rate": f"{customer_analysis['customer_value_metrics']['customer_retention_rate']:.2%}"
            },
            "top_insights": [
                f"Most profitable category: {product_analysis['category_analysis']['most_profitable_category']}",
                f"Most valuable customer segment: {customer_analysis['demographic_insights']['most_valuable_age_group']}",
                f"Peak sales month: {analysis_results['time_analysis']['monthly_sales_summary']['best_month']}",
                f"Repeat customer rate: {customer_analysis['customer_value_metrics']['repeat_customer_percentage']:.1f}%"
            ]
        }
    
    def _generate_recommendations(self, analysis_results: Dict) -> List[str]:
        """
        Generate business recommendations based on analysis
        基于分析生成业务建议
        """
        recommendations = [
            "Focus marketing efforts on the most profitable product categories",
            "Implement customer retention programs for high-value customers",
            "Optimize inventory for fast-moving products",
            "Develop targeted campaigns for different customer segments",
            "Consider seasonal promotions during peak sales periods",
            "Investigate and address factors causing customer churn",
            "Expand product offerings in high-performing categories",
            "Implement dynamic pricing strategies based on demand patterns"
        ]
        
        return recommendations
    
    def _generate_markdown_report(self, report_content: Dict) -> str:
        """
        Generate markdown formatted report
        生成Markdown格式报告
        """
        markdown = f"""
# E-commerce Order Analysis Report
# 电商订单分析报告

**Generated on:** {report_content['report_metadata']['generated_at']}

**Analysis Period:** {report_content['report_metadata']['data_period']['start']} to {report_content['report_metadata']['data_period']['end']}

**Total Records:** {report_content['report_metadata']['total_records_analyzed']:,}

## Executive Summary / 执行摘要

### Key Metrics / 关键指标
- **Total Revenue / 总收入:** ¥{report_content['executive_summary']['key_metrics']['total_revenue']}
- **Total Orders / 总订单数:** {report_content['executive_summary']['key_metrics']['total_orders']}
- **Average Order Value / 平均订单价值:** ¥{report_content['executive_summary']['key_metrics']['average_order_value']}
- **Total Customers / 总客户数:** {report_content['executive_summary']['key_metrics']['total_customers']}
- **Customer Retention Rate / 客户留存率:** {report_content['executive_summary']['key_metrics']['customer_retention_rate']}

### Top Insights / 主要洞察
"""
        
        for insight in report_content['executive_summary']['top_insights']:
            markdown += f"- {insight}\n"
        
        markdown += """

## Recommendations / 建议

"""
        
        for i, recommendation in enumerate(report_content['recommendations'], 1):
            markdown += f"{i}. {recommendation}\n"
        
        markdown += """

---

*This report was automatically generated by the E-commerce Order Analysis System.*

*本报告由电商订单分析系统自动生成。*
"""
        
        return markdown