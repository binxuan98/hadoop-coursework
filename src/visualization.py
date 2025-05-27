# -*- coding: utf-8 -*-
"""
Data Visualization Module for E-commerce Order Analysis
电商订单分析数据可视化模块

This module contains functions for creating various charts and visualizations
for e-commerce order data analysis.
本模块包含为电商订单数据分析创建各种图表和可视化的函数。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple

# Import configuration
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import CHARTS_DIR, VIZ_CONFIG

# Set up matplotlib and seaborn styles
plt.style.use('default')
sns.set_style(VIZ_CONFIG["style"])
sns.set_palette(VIZ_CONFIG["palette"])
plt.rcParams['figure.figsize'] = VIZ_CONFIG["figure_size"]
plt.rcParams['figure.dpi'] = VIZ_CONFIG["dpi"]
plt.rcParams['font.size'] = VIZ_CONFIG["font_size"]
warnings.filterwarnings('ignore')

class DataVisualizer:
    """
    Data visualization class for e-commerce order analysis
    电商订单分析数据可视化类
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the DataVisualizer
        初始化数据可视化器
        
        Args:
            df: DataFrame containing order data
        """
        self.df = df.copy()
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"DataVisualizer initialized with {len(df)} records")
        
        # Ensure output directory exists
        CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    
    def plot_sales_trend(self, save_path: Optional[Path] = None) -> None:
        """
        Plot sales trend over time
        绘制销售趋势图
        
        Args:
            save_path: Path to save the chart
        """
        self.logger.info("Creating sales trend visualization")
        
        # Prepare data
        daily_sales = self.df.groupby('order_date').agg({
            'total_amount': 'sum',
            'order_id': 'count'
        }).rename(columns={'order_id': 'order_count'})
        
        # Create subplot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Plot revenue trend
        ax1.plot(daily_sales.index.values, daily_sales['total_amount'].values, 
                linewidth=2, color='#2E86AB', alpha=0.8)
        ax1.fill_between(daily_sales.index.values, daily_sales['total_amount'].values, 
                        alpha=0.3, color='#2E86AB')
        ax1.set_title('Daily Revenue Trend / 日销售额趋势', 
                     fontsize=VIZ_CONFIG["title_size"], fontweight='bold')
        ax1.set_ylabel('Revenue (¥) / 收入 (¥)', fontsize=VIZ_CONFIG["label_size"])
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Add trend line
        z = np.polyfit(range(len(daily_sales)), daily_sales['total_amount'].values, 1)
        p = np.poly1d(z)
        ax1.plot(daily_sales.index.values, p(range(len(daily_sales))), 
                "r--", alpha=0.8, linewidth=2, label='Trend Line / 趋势线')
        ax1.legend()
        
        # Plot order count trend
        ax2.bar(daily_sales.index.values, daily_sales['order_count'].values, 
               alpha=0.7, color='#A23B72', width=0.8)
        ax2.set_title('Daily Order Count Trend / 日订单数量趋势', 
                     fontsize=VIZ_CONFIG["title_size"], fontweight='bold')
        ax2.set_ylabel('Order Count / 订单数量', fontsize=VIZ_CONFIG["label_size"])
        ax2.set_xlabel('Date / 日期', fontsize=VIZ_CONFIG["label_size"])
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = CHARTS_DIR / "sales_trend.png"
        plt.savefig(save_path, dpi=VIZ_CONFIG["dpi"], bbox_inches='tight')
        plt.show()
        
        self.logger.info(f"Sales trend chart saved to {save_path}")
    
    def plot_category_distribution(self, save_path: Optional[Path] = None) -> None:
        """
        Plot product category distribution
        绘制产品类别分布图
        
        Args:
            save_path: Path to save the chart
        """
        self.logger.info("Creating category distribution visualization")
        
        # Prepare data
        category_stats = self.df.groupby('product_category').agg({
            'total_amount': 'sum',
            'order_id': 'count'
        }).rename(columns={'order_id': 'order_count'})
        
        category_stats = category_stats.sort_values('total_amount', ascending=False)
        
        # Create subplot
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Revenue by category (bar chart)
        bars1 = ax1.bar(range(len(category_stats)), category_stats['total_amount'], 
                        color=sns.color_palette("viridis", len(category_stats)))
        ax1.set_title('Revenue by Product Category / 各产品类别收入', 
                     fontsize=VIZ_CONFIG["title_size"], fontweight='bold')
        ax1.set_ylabel('Revenue (¥) / 收入 (¥)', fontsize=VIZ_CONFIG["label_size"])
        ax1.set_xticks(range(len(category_stats)))
        ax1.set_xticklabels(category_stats.index, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'¥{height:,.0f}', ha='center', va='bottom', fontsize=9)
        
        # 2. Market share pie chart
        colors = sns.color_palette("Set3", len(category_stats))
        wedges, texts, autotexts = ax2.pie(category_stats['total_amount'], 
                                          labels=category_stats.index,
                                          autopct='%1.1f%%', 
                                          colors=colors,
                                          startangle=90)
        ax2.set_title('Market Share by Category / 各类别市场份额', 
                     fontsize=VIZ_CONFIG["title_size"], fontweight='bold')
        
        # 3. Order count by category
        bars3 = ax3.bar(range(len(category_stats)), category_stats['order_count'],
                        color=sns.color_palette("plasma", len(category_stats)))
        ax3.set_title('Order Count by Category / 各类别订单数量', 
                     fontsize=VIZ_CONFIG["title_size"], fontweight='bold')
        ax3.set_ylabel('Order Count / 订单数量', fontsize=VIZ_CONFIG["label_size"])
        ax3.set_xticks(range(len(category_stats)))
        ax3.set_xticklabels(category_stats.index, rotation=45, ha='right')
        ax3.grid(True, alpha=0.3)
        
        # 4. Average order value by category
        avg_order_value = category_stats['total_amount'] / category_stats['order_count']
        bars4 = ax4.bar(range(len(avg_order_value)), avg_order_value,
                        color=sns.color_palette("coolwarm", len(avg_order_value)))
        ax4.set_title('Average Order Value by Category / 各类别平均订单价值', 
                     fontsize=VIZ_CONFIG["title_size"], fontweight='bold')
        ax4.set_ylabel('Average Order Value (¥) / 平均订单价值 (¥)', fontsize=VIZ_CONFIG["label_size"])
        ax4.set_xticks(range(len(avg_order_value)))
        ax4.set_xticklabels(avg_order_value.index, rotation=45, ha='right')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = CHARTS_DIR / "category_distribution.png"
        plt.savefig(save_path, dpi=VIZ_CONFIG["dpi"], bbox_inches='tight')
        plt.show()
        
        self.logger.info(f"Category distribution chart saved to {save_path}")
    
    def plot_customer_demographics(self, save_path: Optional[Path] = None) -> None:
        """
        Plot customer demographics analysis
        绘制客户人口统计分析图
        
        Args:
            save_path: Path to save the chart
        """
        self.logger.info("Creating customer demographics visualization")
        
        # Create subplot
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Age distribution
        age_counts = self.df['age_group'].value_counts()
        bars1 = ax1.bar(age_counts.index, age_counts.values, 
                        color=sns.color_palette("viridis", len(age_counts)))
        ax1.set_title('Customer Age Distribution / 客户年龄分布', 
                     fontsize=VIZ_CONFIG["title_size"], fontweight='bold')
        ax1.set_ylabel('Number of Orders / 订单数量', fontsize=VIZ_CONFIG["label_size"])
        ax1.set_xlabel('Age Group / 年龄组', fontsize=VIZ_CONFIG["label_size"])
        ax1.grid(True, alpha=0.3)
        
        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        # 2. Gender distribution
        gender_revenue = self.df.groupby('customer_gender')['total_amount'].sum()
        colors = ['#FF6B9D', '#4ECDC4']
        wedges, texts, autotexts = ax2.pie(gender_revenue.values, 
                                          labels=gender_revenue.index,
                                          autopct='%1.1f%%', 
                                          colors=colors,
                                          startangle=90)
        ax2.set_title('Revenue by Gender / 按性别分类的收入', 
                     fontsize=VIZ_CONFIG["title_size"], fontweight='bold')
        
        # 3. Top cities by revenue
        city_revenue = self.df.groupby('customer_city')['total_amount'].sum().sort_values(ascending=False).head(10)
        bars3 = ax3.barh(range(len(city_revenue)), city_revenue.values,
                        color=sns.color_palette("plasma", len(city_revenue)))
        ax3.set_title('Top 10 Cities by Revenue / 收入前10城市', 
                     fontsize=VIZ_CONFIG["title_size"], fontweight='bold')
        ax3.set_xlabel('Revenue (¥) / 收入 (¥)', fontsize=VIZ_CONFIG["label_size"])
        ax3.set_yticks(range(len(city_revenue)))
        ax3.set_yticklabels(city_revenue.index)
        ax3.grid(True, alpha=0.3)
        
        # 4. Age group vs Average order value
        age_aov = self.df.groupby('age_group')['total_amount'].mean()
        bars4 = ax4.bar(age_aov.index, age_aov.values,
                        color=sns.color_palette("coolwarm", len(age_aov)))
        ax4.set_title('Average Order Value by Age Group / 各年龄组平均订单价值', 
                     fontsize=VIZ_CONFIG["title_size"], fontweight='bold')
        ax4.set_ylabel('Average Order Value (¥) / 平均订单价值 (¥)', fontsize=VIZ_CONFIG["label_size"])
        ax4.set_xlabel('Age Group / 年龄组', fontsize=VIZ_CONFIG["label_size"])
        ax4.grid(True, alpha=0.3)
        
        # Add value labels
        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'¥{height:.0f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = CHARTS_DIR / "customer_demographics.png"
        plt.savefig(save_path, dpi=VIZ_CONFIG["dpi"], bbox_inches='tight')
        plt.show()
        
        self.logger.info(f"Customer demographics chart saved to {save_path}")
    
    def plot_top_products(self, top_n: int = 15, save_path: Optional[Path] = None) -> None:
        """
        Plot top products analysis
        绘制热门产品分析图
        
        Args:
            top_n: Number of top products to show
            save_path: Path to save the chart
        """
        self.logger.info(f"Creating top {top_n} products visualization")
        
        # Prepare data
        product_stats = self.df.groupby('product_name').agg({
            'total_amount': 'sum',
            'quantity': 'sum',
            'order_id': 'count'
        }).rename(columns={'order_id': 'order_count'})
        
        # Get top products by different metrics
        top_by_revenue = product_stats.nlargest(top_n, 'total_amount')
        top_by_quantity = product_stats.nlargest(top_n, 'quantity')
        
        # Create subplot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
        
        # 1. Top products by revenue
        bars1 = ax1.barh(range(len(top_by_revenue)), top_by_revenue['total_amount'],
                         color=sns.color_palette("viridis", len(top_by_revenue)))
        ax1.set_title(f'Top {top_n} Products by Revenue / 收入前{top_n}产品', 
                     fontsize=VIZ_CONFIG["title_size"], fontweight='bold')
        ax1.set_xlabel('Revenue (¥) / 收入 (¥)', fontsize=VIZ_CONFIG["label_size"])
        ax1.set_yticks(range(len(top_by_revenue)))
        ax1.set_yticklabels([name[:30] + '...' if len(name) > 30 else name 
                            for name in top_by_revenue.index])
        ax1.grid(True, alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width, bar.get_y() + bar.get_height()/2.,
                    f'¥{width:,.0f}', ha='left', va='center', fontsize=9)
        
        # 2. Top products by quantity sold
        bars2 = ax2.barh(range(len(top_by_quantity)), top_by_quantity['quantity'],
                         color=sns.color_palette("plasma", len(top_by_quantity)))
        ax2.set_title(f'Top {top_n} Products by Quantity Sold / 销量前{top_n}产品', 
                     fontsize=VIZ_CONFIG["title_size"], fontweight='bold')
        ax2.set_xlabel('Quantity Sold / 销售数量', fontsize=VIZ_CONFIG["label_size"])
        ax2.set_yticks(range(len(top_by_quantity)))
        ax2.set_yticklabels([name[:30] + '...' if len(name) > 30 else name 
                            for name in top_by_quantity.index])
        ax2.grid(True, alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars2):
            width = bar.get_width()
            ax2.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{int(width)}', ha='left', va='center', fontsize=9)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = CHARTS_DIR / "top_products.png"
        plt.savefig(save_path, dpi=VIZ_CONFIG["dpi"], bbox_inches='tight')
        plt.show()
        
        self.logger.info(f"Top products chart saved to {save_path}")
    
    def plot_correlation_matrix(self, save_path: Optional[Path] = None) -> None:
        """
        Plot correlation matrix of numerical variables
        绘制数值变量相关性矩阵图
        
        Args:
            save_path: Path to save the chart
        """
        self.logger.info("Creating correlation matrix visualization")
        
        # Select numerical columns
        numerical_cols = ['quantity', 'unit_price', 'total_amount', 'customer_age']
        correlation_matrix = self.df[numerical_cols].corr()
        
        # Create heatmap
        plt.figure(figsize=(10, 8))
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        
        sns.heatmap(correlation_matrix, 
                   mask=mask,
                   annot=True, 
                   cmap='RdYlBu_r', 
                   center=0,
                   square=True, 
                   fmt='.3f',
                   cbar_kws={"shrink": .8})
        
        plt.title('Correlation Matrix of Numerical Variables\n数值变量相关性矩阵', 
                 fontsize=VIZ_CONFIG["title_size"], fontweight='bold', pad=20)
        plt.xlabel('Variables / 变量', fontsize=VIZ_CONFIG["label_size"])
        plt.ylabel('Variables / 变量', fontsize=VIZ_CONFIG["label_size"])
        
        # Customize labels
        labels = ['Quantity\n数量', 'Unit Price\n单价', 'Total Amount\n总金额', 'Customer Age\n客户年龄']
        plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
        plt.yticks(range(len(labels)), labels, rotation=0)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = CHARTS_DIR / "correlation_matrix.png"
        plt.savefig(save_path, dpi=VIZ_CONFIG["dpi"], bbox_inches='tight')
        plt.show()
        
        self.logger.info(f"Correlation matrix chart saved to {save_path}")
    
    def plot_seasonal_analysis(self, save_path: Optional[Path] = None) -> None:
        """
        Plot seasonal analysis
        绘制季节性分析图
        
        Args:
            save_path: Path to save the chart
        """
        self.logger.info("Creating seasonal analysis visualization")
        
        # Prepare data
        monthly_sales = self.df.groupby('order_month').agg({
            'total_amount': 'sum',
            'order_id': 'count'
        }).rename(columns={'order_id': 'order_count'})
        
        weekday_sales = self.df.groupby('order_weekday').agg({
            'total_amount': 'sum',
            'order_id': 'count'
        }).rename(columns={'order_id': 'order_count'})
        
        # Reorder weekdays
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_sales = weekday_sales.reindex(weekday_order)
        
        # Create subplot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 1. Monthly sales pattern
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        bars1 = ax1.bar(range(1, 13), monthly_sales['total_amount'],
                        color=sns.color_palette("viridis", 12))
        ax1.set_title('Monthly Sales Pattern / 月度销售模式', 
                     fontsize=VIZ_CONFIG["title_size"], fontweight='bold')
        ax1.set_ylabel('Revenue (¥) / 收入 (¥)', fontsize=VIZ_CONFIG["label_size"])
        ax1.set_xlabel('Month / 月份', fontsize=VIZ_CONFIG["label_size"])
        ax1.set_xticks(range(1, 13))
        ax1.set_xticklabels(month_names)
        ax1.grid(True, alpha=0.3)
        
        # 2. Weekday sales pattern
        weekday_names_cn = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        bars2 = ax2.bar(range(7), weekday_sales['total_amount'],
                        color=sns.color_palette("plasma", 7))
        ax2.set_title('Weekday Sales Pattern / 工作日销售模式', 
                     fontsize=VIZ_CONFIG["title_size"], fontweight='bold')
        ax2.set_ylabel('Revenue (¥) / 收入 (¥)', fontsize=VIZ_CONFIG["label_size"])
        ax2.set_xlabel('Day of Week / 星期', fontsize=VIZ_CONFIG["label_size"])
        ax2.set_xticks(range(7))
        ax2.set_xticklabels([f'{en}\n{cn}' for en, cn in zip(weekday_order, weekday_names_cn)], 
                           rotation=45, ha='right')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = CHARTS_DIR / "seasonal_analysis.png"
        plt.savefig(save_path, dpi=VIZ_CONFIG["dpi"], bbox_inches='tight')
        plt.show()
        
        self.logger.info(f"Seasonal analysis chart saved to {save_path}")
    
    def create_interactive_dashboard(self, save_path: Optional[Path] = None) -> None:
        """
        Create interactive dashboard using Plotly
        使用Plotly创建交互式仪表板
        
        Args:
            save_path: Path to save the HTML file
        """
        self.logger.info("Creating interactive dashboard")
        
        # Prepare data
        daily_sales = self.df.groupby('order_date')['total_amount'].sum().reset_index()
        category_sales = self.df.groupby('product_category')['total_amount'].sum().reset_index()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Daily Sales Trend / 日销售趋势', 
                           'Category Distribution / 类别分布',
                           'Customer Age Distribution / 客户年龄分布', 
                           'Top Products / 热门产品'),
            specs=[[{"secondary_y": False}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # 1. Daily sales trend
        fig.add_trace(
            go.Scatter(x=daily_sales['order_date'], 
                      y=daily_sales['total_amount'],
                      mode='lines+markers',
                      name='Daily Revenue',
                      line=dict(color='#2E86AB', width=3)),
            row=1, col=1
        )
        
        # 2. Category pie chart
        fig.add_trace(
            go.Pie(labels=category_sales['product_category'], 
                  values=category_sales['total_amount'],
                  name="Category Share"),
            row=1, col=2
        )
        
        # 3. Age distribution
        age_counts = self.df['age_group'].value_counts()
        fig.add_trace(
            go.Bar(x=age_counts.index, 
                  y=age_counts.values,
                  name="Age Distribution",
                  marker_color='viridis'),
            row=2, col=1
        )
        
        # 4. Top products
        top_products = self.df.groupby('product_name')['total_amount'].sum().nlargest(10)
        fig.add_trace(
            go.Bar(x=top_products.values, 
                  y=[name[:20] + '...' if len(name) > 20 else name for name in top_products.index],
                  orientation='h',
                  name="Top Products",
                  marker_color='plasma'),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            title_text="E-commerce Order Analysis Dashboard / 电商订单分析仪表板",
            title_x=0.5,
            showlegend=False
        )
        
        if save_path is None:
            save_path = CHARTS_DIR / "interactive_dashboard.html"
        
        fig.write_html(save_path)
        self.logger.info(f"Interactive dashboard saved to {save_path}")
    
    def generate_all_visualizations(self) -> None:
        """
        Generate all visualizations at once
        一次性生成所有可视化图表
        """
        self.logger.info("Generating all visualizations")
        
        try:
            self.plot_sales_trend()
            self.plot_category_distribution()
            self.plot_customer_demographics()
            self.plot_top_products()
            self.plot_correlation_matrix()
            self.plot_seasonal_analysis()
            self.create_interactive_dashboard()
            
            self.logger.info("All visualizations generated successfully")
            
        except Exception as e:
            self.logger.error(f"Error generating visualizations: {str(e)}")
            raise