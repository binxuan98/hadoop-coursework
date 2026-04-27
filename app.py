#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit Web Application for E-commerce Order Analysis
电商订单分析Streamlit网页应用

This module provides a web interface for the e-commerce order analysis system.
本模块为电商订单分析系统提供网页界面。

Author: Data Analysis Team
Date: 2025-05-28
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import json
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from data_utils import DataProcessor
from analysis import OrderAnalyzer
from visualization import DataVisualizer
from config import *

# Page configuration
st.set_page_config(
    page_title="电商订单数据分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (Green Theme)
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #2E8B57;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background-color: #E8F5E9;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #2E8B57;
}
.sidebar-info {
    background-color: #DCEDC8;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}
.section-header {
    color: #2E8B57;
    font-size: 1.5rem;
    font-weight: bold;
    margin-top: 2rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #C8E6C9;
}
.subsection-header {
    color: #388E3C;
    font-size: 1.2rem;
    font-weight: bold;
    margin-top: 1.5rem;
    margin-bottom: 0.8rem;
}
.alert-box {
    background-color: #FFF8E1;
    border-left: 4px solid #FF9800;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.success-box {
    background-color: #E8F5E9;
    border-left: 4px solid #4CAF50;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.warning-box {
    background-color: #FFF3E0;
    border-left: 4px solid #FF5722;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def load_sample_data():
    """Load or generate sample data"""
    processor = DataProcessor()
    
    # Check if sample data exists
    sample_file = DATA_DIR / "raw" / "sample_orders.csv"
    if not sample_file.exists():
        st.info("正在生成示例数据...")
        processor.generate_sample_data(output_file=sample_file)
    
    # Load and clean data
    df = processor.load_data(sample_file)
    cleaned_df = processor.clean_data(df)
    
    return cleaned_df, processor

def create_interactive_charts(df):
    """Create interactive charts using Plotly"""
    
    # Daily sales trend
    daily_sales = df.groupby('order_date').agg({
        'total_amount': 'sum',
        'order_id': 'count'
    }).reset_index()
    daily_sales.columns = ['date', 'revenue', 'orders']
    
    fig_trend = make_subplots(
        rows=2, cols=1,
        subplot_titles=('日销售额趋势', '日订单数量趋势'),
        vertical_spacing=0.1
    )
    
    fig_trend.add_trace(
        go.Scatter(x=daily_sales['date'], y=daily_sales['revenue'],
                  mode='lines+markers', name='销售额',
                  line=dict(color='#2E8B57', width=2)),
        row=1, col=1
    )
    
    fig_trend.add_trace(
        go.Bar(x=daily_sales['date'], y=daily_sales['orders'],
               name='订单数', marker_color='#81C784'),
        row=2, col=1
    )
    
    fig_trend.update_layout(height=600, showlegend=False)
    fig_trend.update_xaxes(title_text="日期", row=2, col=1)
    fig_trend.update_yaxes(title_text="销售额 (¥)", row=1, col=1)
    fig_trend.update_yaxes(title_text="订单数", row=2, col=1)
    
    return fig_trend

def create_category_chart(df):
    """Create category distribution chart"""
    category_stats = df.groupby('product_category').agg({
        'total_amount': 'sum',
        'order_id': 'count',
        'quantity': 'sum'
    }).reset_index()
    category_stats.columns = ['category', 'revenue', 'orders', 'quantity']
    category_stats = category_stats.sort_values('revenue', ascending=False)
    
    fig = px.bar(category_stats, x='category', y='revenue',
                 title='产品类别销售额分布',
                 labels={'revenue': '销售额 (¥)', 'category': '产品类别'},
                 color='revenue',
                 color_continuous_scale='Greens')
    
    fig.update_layout(height=500, xaxis_tickangle=-45)
    return fig

def create_customer_analysis_chart(df):
    """Create customer analysis charts"""
    # Age group analysis
    age_analysis = df.groupby('age_group').agg({
        'total_amount': ['sum', 'mean'],
        'customer_id': 'nunique'
    }).reset_index()
    age_analysis.columns = ['age_group', 'total_revenue', 'avg_order_value', 'customer_count']
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('年龄组销售额分布', '年龄组客户数量'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig.add_trace(
        go.Bar(x=age_analysis['age_group'], y=age_analysis['total_revenue'],
               name='总销售额', marker_color='#2E8B57'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=age_analysis['age_group'], y=age_analysis['customer_count'],
               name='客户数量', marker_color='#81C784'),
        row=1, col=2
    )
    
    fig.update_layout(height=400, showlegend=False)
    fig.update_xaxes(title_text="年龄组", row=1, col=1)
    fig.update_xaxes(title_text="年龄组", row=1, col=2)
    fig.update_yaxes(title_text="销售额 (¥)", row=1, col=1)
    fig.update_yaxes(title_text="客户数量", row=1, col=2)
    
    return fig

# ============================================================
# 商品销售分析模块函数
# ============================================================

def analyze_product_sales(df):
    """
    商品销售分析：热销/滞销商品识别、销量排行、销售贡献占比、销售趋势、价格带分析
    """
    # 商品销售统计
    product_stats = df.groupby('product_name').agg({
        'total_amount': ['sum', 'mean', 'count'],
        'quantity': 'sum',
        'unit_price': 'mean'
    }).reset_index()
    product_stats.columns = ['product_name', 'total_revenue', 'avg_order_value', 'order_count',
                             'total_quantity', 'avg_unit_price']
    
    # 计算销售贡献占比
    total_revenue = product_stats['total_revenue'].sum()
    product_stats['revenue_contribution'] = product_stats['total_revenue'] / total_revenue * 100
    
    # 识别热销和滞销商品（基于销量的分位数）
    q75 = product_stats['total_quantity'].quantile(0.75)
    q25 = product_stats['total_quantity'].quantile(0.25)
    
    product_stats['sales_category'] = pd.cut(
        product_stats['total_quantity'],
        bins=[-float('inf'), q25, q75, float('inf')],
        labels=['滞销商品', '一般商品', '热销商品']
    )
    
    # 价格带分析
    price_bins = [0, 50, 100, 200, 500, 1000, 5000, float('inf')]
    price_labels = ['0-50', '50-100', '100-200', '200-500', '500-1000', '1000-5000', '5000+']
    df['price_band'] = pd.cut(df['unit_price'], bins=price_bins, labels=price_labels)
    
    price_band_stats = df.groupby('price_band').agg({
        'total_amount': 'sum',
        'quantity': 'sum',
        'order_id': 'count'
    }).reset_index()
    price_band_stats.columns = ['price_band', 'revenue', 'quantity', 'orders']
    
    # 商品销售趋势（按月）
    df['month'] = df['order_date'].dt.to_period('M')
    monthly_product = df.groupby(['month', 'product_category']).agg({
        'total_amount': 'sum',
        'quantity': 'sum'
    }).reset_index()
    monthly_product['month'] = monthly_product['month'].astype(str)
    
    return {
        'product_stats': product_stats,
        'hot_products': product_stats[product_stats['sales_category'] == '热销商品'].sort_values('total_quantity', ascending=False),
        'cold_products': product_stats[product_stats['sales_category'] == '滞销商品'].sort_values('total_quantity', ascending=True),
        'price_band_stats': price_band_stats,
        'monthly_product': monthly_product
    }

def create_product_sales_charts(df, product_analysis):
    """
    创建商品销售分析的图表
    """
    product_stats = product_analysis['product_stats']
    price_band_stats = product_analysis['price_band_stats']
    monthly_product = product_analysis['monthly_product']
    hot_products = product_analysis['hot_products']
    cold_products = product_analysis['cold_products']
    
    # 1. 销量排行 TOP 10
    top10_by_quantity = product_stats.nlargest(10, 'total_quantity')
    fig_quantity_rank = px.bar(
        top10_by_quantity, 
        x='total_quantity', 
        y='product_name',
        orientation='h',
        title='商品销量排行 TOP 10',
        labels={'total_quantity': '销量', 'product_name': '商品名称'},
        color='total_quantity',
        color_continuous_scale='Greens'
    )
    fig_quantity_rank.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
    
    # 2. 销售额排行 TOP 10
    top10_by_revenue = product_stats.nlargest(10, 'total_revenue')
    fig_revenue_rank = px.bar(
        top10_by_revenue, 
        x='total_revenue', 
        y='product_name',
        orientation='h',
        title='商品销售额排行 TOP 10',
        labels={'total_revenue': '销售额 (¥)', 'product_name': '商品名称'},
        color='total_revenue',
        color_continuous_scale='Greens'
    )
    fig_revenue_rank.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
    
    # 3. 销售贡献占比饼图
    top10_contribution = product_stats.nlargest(10, 'revenue_contribution')
    other_contribution = product_stats[~product_stats.index.isin(top10_contribution.index)]['revenue_contribution'].sum()
    
    pie_data = pd.concat([
        top10_contribution[['product_name', 'revenue_contribution']],
        pd.DataFrame({'product_name': ['其他商品'], 'revenue_contribution': [other_contribution]})
    ])
    
    fig_contribution = px.pie(
        pie_data, 
        values='revenue_contribution', 
        names='product_name',
        title='商品销售贡献占比',
        color_discrete_sequence=px.colors.sequential.Greens
    )
    fig_contribution.update_layout(height=500)
    
    # 4. 价格带分析图
    fig_price_band = make_subplots(
        rows=2, cols=1,
        subplot_titles=('各价格带销售额分布', '各价格带订单数量分布'),
        vertical_spacing=0.15
    )
    
    fig_price_band.add_trace(
        go.Bar(x=price_band_stats['price_band'], y=price_band_stats['revenue'],
               name='销售额', marker_color='#2E8B57'),
        row=1, col=1
    )
    
    fig_price_band.add_trace(
        go.Bar(x=price_band_stats['price_band'], y=price_band_stats['orders'],
               name='订单数', marker_color='#81C784'),
        row=2, col=1
    )
    
    fig_price_band.update_layout(height=600, showlegend=False)
    fig_price_band.update_xaxes(title_text="价格带", row=2, col=1)
    fig_price_band.update_yaxes(title_text="销售额 (¥)", row=1, col=1)
    fig_price_band.update_yaxes(title_text="订单数", row=2, col=1)
    
    # 5. 商品销售趋势图（按月）
    fig_monthly_trend = px.line(
        monthly_product, 
        x='month', 
        y='total_amount', 
        color='product_category',
        title='各类别商品月度销售趋势',
        labels={'total_amount': '销售额 (¥)', 'month': '月份', 'product_category': '产品类别'},
        color_discrete_sequence=px.colors.sequential.Greens
    )
    fig_monthly_trend.update_layout(height=500)
    
    return {
        'fig_quantity_rank': fig_quantity_rank,
        'fig_revenue_rank': fig_revenue_rank,
        'fig_contribution': fig_contribution,
        'fig_price_band': fig_price_band,
        'fig_monthly_trend': fig_monthly_trend,
        'hot_products': hot_products,
        'cold_products': cold_products
    }

# ============================================================
# 异常订单检测模块函数
# ============================================================

def detect_anomalous_orders(df, large_order_threshold=5000, high_frequency_days=7, high_frequency_count=5):
    """
    异常订单检测：大额订单、高频下单、异常折扣
    """
    anomalies = {}
    
    # 1. 大额订单检测
    large_orders = df[df['total_amount'] >= large_order_threshold].copy()
    large_orders['anomaly_type'] = '大额订单'
    anomalies['large_orders'] = large_orders
    
    # 2. 高频下单检测（同一客户在指定天数内下单次数超过阈值）
    df_sorted = df.sort_values(['customer_id', 'order_date'])
    df_sorted['order_date'] = pd.to_datetime(df_sorted['order_date'])
    
    # 计算每个客户的订单间隔
    customer_orders = df_sorted.groupby('customer_id')
    
    high_freq_customers = []
    for cust_id, group in customer_orders:
        group = group.sort_values('order_date')
        # 检查是否有连续N天内下单超过M次
        for i in range(len(group) - high_frequency_count + 1):
            window_orders = group.iloc[i:i+high_frequency_count]
            days_diff = (window_orders['order_date'].max() - window_orders['order_date'].min()).days
            if days_diff <= high_frequency_days:
                high_freq_customers.append({
                    'customer_id': cust_id,
                    'start_date': window_orders['order_date'].min(),
                    'end_date': window_orders['order_date'].max(),
                    'order_count': high_frequency_count,
                    'days_diff': days_diff
                })
                break
    
    # 获取高频客户的所有订单
    high_freq_customer_ids = [x['customer_id'] for x in high_freq_customers]
    high_freq_orders = df[df['customer_id'].isin(high_freq_customer_ids)].copy()
    high_freq_orders['anomaly_type'] = '高频下单'
    anomalies['high_freq_orders'] = high_freq_orders
    anomalies['high_freq_customers'] = pd.DataFrame(high_freq_customers) if high_freq_customers else pd.DataFrame()
    
    # 3. 异常折扣检测（计算每个商品的平均价格，低于平均价格30%视为异常折扣）
    product_avg_price = df.groupby('product_name')['unit_price'].mean().reset_index()
    product_avg_price.columns = ['product_name', 'avg_price']
    
    df_with_avg = df.merge(product_avg_price, on='product_name', how='left')
    df_with_avg['discount_ratio'] = 1 - (df_with_avg['unit_price'] / df_with_avg['avg_price'])
    
    # 低于平均价格30%视为异常折扣
    discount_threshold = 0.3
    anomalous_discount_orders = df_with_avg[
        (df_with_avg['discount_ratio'] > discount_threshold) & 
        (df_with_avg['unit_price'] > 0)
    ].copy()
    anomalous_discount_orders['anomaly_type'] = '异常折扣'
    anomalies['anomalous_discount'] = anomalous_discount_orders
    
    # 4. 交易波动分析（日销售额的标准差检测）
    daily_sales = df.groupby('order_date')['total_amount'].sum().reset_index()
    daily_sales.columns = ['date', 'revenue']
    
    # 计算Z-score检测异常日
    daily_sales['z_score'] = (daily_sales['revenue'] - daily_sales['revenue'].mean()) / daily_sales['revenue'].std()
    anomaly_days = daily_sales[abs(daily_sales['z_score']) > 2]  # Z-score > 2 视为异常
    
    anomalies['daily_sales'] = daily_sales
    anomalies['anomaly_days'] = anomaly_days
    
    # 5. 合并所有异常订单用于散点图
    all_anomalies = pd.concat([
        large_orders.assign(anomaly_reason='大额订单'),
        high_freq_orders.assign(anomaly_reason='高频下单'),
        anomalous_discount_orders.assign(anomaly_reason='异常折扣')
    ]).drop_duplicates(subset=['order_id'])
    
    anomalies['all_anomalies'] = all_anomalies
    
    return anomalies

def create_anomaly_charts(df, anomalies, large_order_threshold):
    """
    创建异常订单检测的图表
    """
    daily_sales = anomalies['daily_sales']
    anomaly_days = anomalies['anomaly_days']
    all_anomalies = anomalies['all_anomalies']
    
    # 1. 带异常点标记的散点图（订单金额 vs 订单数量）
    df_scatter = df.copy()
    
    # 合并异常原因
    if not all_anomalies.empty and 'order_id' in all_anomalies.columns:
        df_scatter = df_scatter.merge(
            all_anomalies[['order_id', 'anomaly_reason']], 
            on='order_id', 
            how='left'
        )
        df_scatter['anomaly_reason'] = df_scatter['anomaly_reason'].fillna('正常订单')
    else:
        df_scatter['anomaly_reason'] = '正常订单'
    
    # 对数据进行抽样，避免点太多导致渲染问题
    max_points = 2000
    if len(df_scatter) > max_points:
        # 确保异常订单都被保留
        anomaly_mask = df_scatter['anomaly_reason'] != '正常订单'
        anomaly_df = df_scatter[anomaly_mask]
        normal_df = df_scatter[~anomaly_mask]
        
        # 对正常订单进行抽样
        sample_size = max_points - len(anomaly_df)
        if sample_size > 0 and len(normal_df) > sample_size:
            normal_df_sampled = normal_df.sample(n=sample_size, random_state=42)
        else:
            normal_df_sampled = normal_df
        
        df_scatter_sampled = pd.concat([anomaly_df, normal_df_sampled], ignore_index=True)
    else:
        df_scatter_sampled = df_scatter.copy()
    
    # 使用 go.Scatter 而不是 px.scatter，更精确控制
    fig_scatter = go.Figure()
    
    # 定义颜色映射
    color_map = {
        '正常订单': '#81C784',
        '大额订单': '#FF5722',
        '高频下单': '#FF9800',
        '异常折扣': '#E91E63'
    }
    
    # 按类型分组绘制
    for reason in df_scatter_sampled['anomaly_reason'].unique():
        filtered = df_scatter_sampled[df_scatter_sampled['anomaly_reason'] == reason]
        fig_scatter.add_trace(
            go.Scatter(
                x=filtered['quantity'],
                y=filtered['total_amount'],
                mode='markers',
                name=reason,
                marker=dict(
                    color=color_map.get(reason, '#9E9E9E'),
                    size=8,
                    opacity=0.7,
                    line=dict(width=1, color='white')
                ),
                hovertemplate='<b>订单类型:</b> %{text}<br>' +
                             '<b>购买数量:</b> %{x}<br>' +
                             '<b>订单金额:</b> ¥%{y:,.2f}<extra></extra>',
                text=filtered['anomaly_reason']
            )
        )
    
    fig_scatter.update_layout(
        title='订单异常检测散点图',
        xaxis_title='购买数量',
        yaxis_title='订单金额 (¥)',
        height=550,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='closest'
    )
    
    # 2. 交易波动预警图表
    fig_volatility = make_subplots(
        rows=2, cols=1,
        subplot_titles=('日销售额趋势（含异常日标记）', '日销售额Z-Score分布'),
        vertical_spacing=0.15
    )
    
    # 正常日销售额
    normal_days = daily_sales[~daily_sales['date'].isin(anomaly_days['date'])]
    fig_volatility.add_trace(
        go.Scatter(x=normal_days['date'], y=normal_days['revenue'],
                  mode='lines+markers', name='正常日',
                  line=dict(color='#2E8B57', width=2),
                  marker=dict(color='#2E8B57', size=6)),
        row=1, col=1
    )
    
    # 异常日标记
    if not anomaly_days.empty:
        fig_volatility.add_trace(
            go.Scatter(x=anomaly_days['date'], y=anomaly_days['revenue'],
                      mode='markers', name='异常日',
                      marker=dict(color='#FF5722', size=12, symbol='star')),
            row=1, col=1
        )
    
    # Z-Score图
    fig_volatility.add_trace(
        go.Scatter(x=daily_sales['date'], y=daily_sales['z_score'],
                  mode='lines+markers', name='Z-Score',
                  line=dict(color='#2E8B57', width=1),
                  marker=dict(color='#81C784', size=4)),
        row=2, col=1
    )
    
    # 添加阈值线
    fig_volatility.add_hline(y=2, line_dash="dash", line_color="#FF5722", row=2, col=1)
    fig_volatility.add_hline(y=-2, line_dash="dash", line_color="#FF5722", row=2, col=1)
    
    fig_volatility.update_layout(height=600, showlegend=True)
    fig_volatility.update_xaxes(title_text="日期", row=2, col=1)
    fig_volatility.update_yaxes(title_text="销售额 (¥)", row=1, col=1)
    fig_volatility.update_yaxes(title_text="Z-Score", row=2, col=1)
    
    # 3. 异常类型分布饼图
    anomaly_type_counts = all_anomalies['anomaly_type'].value_counts().reset_index()
    anomaly_type_counts.columns = ['anomaly_type', 'count']
    
    fig_anomaly_pie = px.pie(
        anomaly_type_counts,
        values='count',
        names='anomaly_type',
        title='异常订单类型分布',
        color_discrete_sequence=['#FF5722', '#FF9800', '#E91E63']
    )
    fig_anomaly_pie.update_layout(height=450)
    
    return {
        'fig_scatter': fig_scatter,
        'fig_volatility': fig_volatility,
        'fig_anomaly_pie': fig_anomaly_pie
    }

# ============================================================
# 用户留存与复购深化分析模块函数
# ============================================================

def analyze_retention_repurchase(df):
    """
    用户留存与复购深化分析：
    - 新用户首购后7天/30天复购情况
    - 不同渠道用户的留存差异
    - 用户生命周期阶段分布
    """
    # 按客户排序订单
    df_sorted = df.sort_values(['customer_id', 'order_date'])
    df_sorted['order_date'] = pd.to_datetime(df_sorted['order_date'])
    
    # 获取每个客户的首购日期和订单次数
    customer_stats = df_sorted.groupby('customer_id').agg({
        'order_date': ['min', 'max', 'count'],
        'total_amount': ['sum', 'mean']
    }).reset_index()
    customer_stats.columns = ['customer_id', 'first_order_date', 'last_order_date', 
                               'order_count', 'total_spent', 'avg_order_value']
    
    # 1. 新用户首购后复购分析
    # 标记每个客户是否为新用户（首购）以及后续订单
    df_with_order_seq = df_sorted.copy()
    df_with_order_seq['order_sequence'] = df_with_order_seq.groupby('customer_id').cumcount() + 1
    
    # 获取首购订单
    first_orders = df_with_order_seq[df_with_order_seq['order_sequence'] == 1].copy()
    first_orders = first_orders[['customer_id', 'order_date', 'total_amount']]
    first_orders.columns = ['customer_id', 'first_order_date', 'first_order_amount']
    
    # 合并首购信息到所有订单
    df_with_first = df_with_order_seq.merge(first_orders, on='customer_id', how='left')
    df_with_first['days_since_first'] = (df_with_first['order_date'] - df_with_first['first_order_date']).dt.days
    
    # 计算7天和30天复购
    repurchase_7d = df_with_first[
        (df_with_first['order_sequence'] > 1) & 
        (df_with_first['days_since_first'] <= 7)
    ]['customer_id'].nunique()
    
    repurchase_30d = df_with_first[
        (df_with_first['order_sequence'] > 1) & 
        (df_with_first['days_since_first'] <= 30)
    ]['customer_id'].nunique()
    
    total_new_users = first_orders['customer_id'].nunique()
    
    # 2. 不同渠道用户的留存差异（使用城市作为渠道模拟）
    # 按城市分组计算留存率
    city_stats = df_sorted.groupby('customer_city').agg({
        'customer_id': 'nunique',
        'order_id': 'count'
    }).reset_index()
    city_stats.columns = ['city', 'total_customers', 'total_orders']
    
    # 计算每个城市的复购客户数
    repeat_customers_by_city = []
    for city in df_sorted['customer_city'].unique():
        city_df = df_sorted[df_sorted['customer_city'] == city]
        city_customer_stats = city_df.groupby('customer_id')['order_id'].count()
        repeat_count = (city_customer_stats > 1).sum()
        repeat_customers_by_city.append({
            'city': city,
            'repeat_customers': repeat_count
        })
    
    city_repeat_df = pd.DataFrame(repeat_customers_by_city)
    city_stats = city_stats.merge(city_repeat_df, on='city', how='left')
    city_stats['retention_rate'] = city_stats['repeat_customers'] / city_stats['total_customers'] * 100
    
    # 3. 用户生命周期阶段分布
    # 基于RFM进行生命周期阶段划分
    max_date = df_sorted['order_date'].max()
    
    # 计算RFM
    rfm = df_sorted.groupby('customer_id').agg({
        'order_date': lambda x: (max_date - x.max()).days,  # Recency
        'order_id': 'count',  # Frequency
        'total_amount': 'sum'  # Monetary
    }).reset_index()
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    # 划分生命周期阶段
    def classify_lifecycle(row):
        if row['frequency'] == 1:
            if row['recency'] <= 30:
                return '新用户'
            else:
                return '流失新用户'
        elif row['recency'] <= 90:
            if row['frequency'] >= 5:
                return '忠诚用户'
            else:
                return '活跃用户'
        elif row['recency'] <= 180:
            return '沉睡用户'
        else:
            return '流失用户'
    
    rfm['lifecycle_stage'] = rfm.apply(classify_lifecycle, axis=1)
    
    lifecycle_distribution = rfm['lifecycle_stage'].value_counts().reset_index()
    lifecycle_distribution.columns = ['stage', 'count']
    lifecycle_distribution['percentage'] = lifecycle_distribution['count'] / lifecycle_distribution['count'].sum() * 100
    
    # 4. 按月份的新用户和复购用户趋势
    df_sorted['month'] = df_sorted['order_date'].dt.to_period('M')
    
    # 每月新用户数（首购）
    monthly_new_users = df_with_first[df_with_first['order_sequence'] == 1].groupby('month')['customer_id'].nunique().reset_index()
    monthly_new_users.columns = ['month', 'new_users']
    
    # 每月复购用户数（非首购订单的客户）
    monthly_repeat_users = df_with_first[df_with_first['order_sequence'] > 1].groupby('month')['customer_id'].nunique().reset_index()
    monthly_repeat_users.columns = ['month', 'repeat_users']
    
    monthly_trend = monthly_new_users.merge(monthly_repeat_users, on='month', how='outer').fillna(0)
    monthly_trend['month'] = monthly_trend['month'].astype(str)
    
    return {
        'repurchase_7d': repurchase_7d,
        'repurchase_30d': repurchase_30d,
        'total_new_users': total_new_users,
        'repurchase_rate_7d': repurchase_7d / total_new_users * 100 if total_new_users > 0 else 0,
        'repurchase_rate_30d': repurchase_30d / total_new_users * 100 if total_new_users > 0 else 0,
        'city_stats': city_stats.sort_values('retention_rate', ascending=False),
        'lifecycle_distribution': lifecycle_distribution,
        'rfm_data': rfm,
        'monthly_trend': monthly_trend,
        'customer_stats': customer_stats
    }

def create_retention_charts(retention_analysis):
    """
    创建用户留存与复购分析的图表
    """
    lifecycle_dist = retention_analysis['lifecycle_distribution']
    city_stats = retention_analysis['city_stats']
    monthly_trend = retention_analysis['monthly_trend']
    rfm_data = retention_analysis['rfm_data']
    
    # 1. 复购率指标可视化
    repurchase_data = pd.DataFrame({
        'period': ['7天复购', '30天复购'],
        'rate': [retention_analysis['repurchase_rate_7d'], retention_analysis['repurchase_rate_30d']],
        'count': [retention_analysis['repurchase_7d'], retention_analysis['repurchase_30d']]
    })
    
    fig_repurchase = make_subplots(
        rows=1, cols=2,
        subplot_titles=('新用户复购率', '复购用户数量'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig_repurchase.add_trace(
        go.Bar(x=repurchase_data['period'], y=repurchase_data['rate'],
               name='复购率 (%)', marker_color='#2E8B57',
               text=[f"{r:.1f}%" for r in repurchase_data['rate']],
               textposition='auto'),
        row=1, col=1
    )
    
    fig_repurchase.add_trace(
        go.Bar(x=repurchase_data['period'], y=repurchase_data['count'],
               name='用户数', marker_color='#81C784',
               text=[f"{int(c)}人" for c in repurchase_data['count']],
               textposition='auto'),
        row=1, col=2
    )
    
    fig_repurchase.update_layout(height=450, showlegend=False)
    
    # 2. 用户生命周期阶段分布
    lifecycle_colors = {
        '新用户': '#4CAF50',
        '活跃用户': '#8BC34A',
        '忠诚用户': '#2E8B57',
        '沉睡用户': '#FF9800',
        '流失用户': '#FF5722',
        '流失新用户': '#795548'
    }
    
    fig_lifecycle = px.pie(
        lifecycle_dist,
        values='count',
        names='stage',
        title='用户生命周期阶段分布',
        color='stage',
        color_discrete_map=lifecycle_colors,
        hole=0.4
    )
    fig_lifecycle.update_layout(height=500)
    
    # 3. 不同城市用户留存差异
    top10_cities = city_stats.nlargest(10, 'total_customers')
    
    fig_city_retention = make_subplots(
        rows=2, cols=1,
        subplot_titles=('各城市客户数量分布', '各城市留存率对比'),
        vertical_spacing=0.15
    )
    
    fig_city_retention.add_trace(
        go.Bar(x=top10_cities['city'], y=top10_cities['total_customers'],
               name='客户数', marker_color='#2E8B57'),
        row=1, col=1
    )
    
    fig_city_retention.add_trace(
        go.Bar(x=top10_cities['city'], y=top10_cities['retention_rate'],
               name='留存率 (%)', marker_color='#81C784'),
        row=2, col=1
    )
    
    fig_city_retention.update_layout(height=600, showlegend=False)
    fig_city_retention.update_xaxes(title_text="城市", row=2, col=1, tickangle=45)
    fig_city_retention.update_yaxes(title_text="客户数量", row=1, col=1)
    fig_city_retention.update_yaxes(title_text="留存率 (%)", row=2, col=1)
    
    # 4. 新用户与复购用户月度趋势
    fig_monthly_trend = go.Figure()
    
    fig_monthly_trend.add_trace(
        go.Scatter(x=monthly_trend['month'], y=monthly_trend['new_users'],
                  mode='lines+markers', name='新用户',
                  line=dict(color='#2E8B57', width=3),
                  marker=dict(size=8))
    )
    
    fig_monthly_trend.add_trace(
        go.Scatter(x=monthly_trend['month'], y=monthly_trend['repeat_users'],
                  mode='lines+markers', name='复购用户',
                  line=dict(color='#81C784', width=3, dash='dash'),
                  marker=dict(size=8))
    )
    
    fig_monthly_trend.update_layout(
        title='新用户与复购用户月度趋势',
        xaxis_title='月份',
        yaxis_title='用户数量',
        height=450,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    # 5. RFM分布散点图
    # 对数据进行抽样，避免点太多导致渲染问题
    max_points = 2000
    if len(rfm_data) > max_points:
        # 按生命周期阶段分层抽样
        sampled_dfs = []
        for stage in rfm_data['lifecycle_stage'].unique():
            stage_df = rfm_data[rfm_data['lifecycle_stage'] == stage]
            # 每个阶段至少保留几个点
            sample_size = min(len(stage_df), max(5, int(max_points / rfm_data['lifecycle_stage'].nunique())))
            sampled_dfs.append(stage_df.sample(n=sample_size, random_state=42))
        rfm_data_sampled = pd.concat(sampled_dfs, ignore_index=True)
    else:
        rfm_data_sampled = rfm_data.copy()
    
    # 使用 go.Scatter 而不是 px.scatter，更精确控制
    fig_rfm_scatter = go.Figure()
    
    # 按生命周期阶段分组绘制
    for stage in rfm_data_sampled['lifecycle_stage'].unique():
        filtered = rfm_data_sampled[rfm_data_sampled['lifecycle_stage'] == stage]
        fig_rfm_scatter.add_trace(
            go.Scatter(
                x=filtered['recency'],
                y=filtered['monetary'],
                mode='markers',
                name=stage,
                marker=dict(
                    color=lifecycle_colors.get(stage, '#9E9E9E'),
                    size=10,
                    opacity=0.7,
                    line=dict(width=1, color='white')
                ),
                hovertemplate='<b>生命周期阶段:</b> %{text}<br>' +
                             '<b>最近购买天数:</b> %{x} 天<br>' +
                             '<b>消费总金额:</b> ¥%{y:,.2f}<extra></extra>',
                text=filtered['lifecycle_stage']
            )
        )
    
    fig_rfm_scatter.update_layout(
        title='用户RFM分布与生命周期阶段',
        xaxis_title='最近购买天数 (天)',
        yaxis_title='消费总金额 (¥)',
        height=500,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='closest'
    )
    
    return {
        'fig_repurchase': fig_repurchase,
        'fig_lifecycle': fig_lifecycle,
        'fig_city_retention': fig_city_retention,
        'fig_monthly_trend': fig_monthly_trend,
        'fig_rfm_scatter': fig_rfm_scatter
    }

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 电商订单数据分析平台</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.2rem;">E-commerce Order Analysis Platform</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-info"><h3>🔧 分析选项</h3></div>', unsafe_allow_html=True)
        
        # Data source selection
        data_source = st.radio(
            "选择数据源",
            ["使用示例数据", "上传CSV文件"]
        )
        
        # Analysis options
        st.markdown("### 📈 基础分析模块")
        show_basic_stats = st.checkbox("基本统计", value=True)
        show_time_analysis = st.checkbox("时间序列分析", value=True)
        show_customer_analysis = st.checkbox("客户分析", value=True)
        show_product_analysis = st.checkbox("产品分析", value=True)
        
        st.markdown("### 🛍️ 新增分析模块")
        show_product_sales = st.checkbox("商品销售分析", value=True)
        show_anomaly_detection = st.checkbox("异常订单检测", value=True)
        show_retention_analysis = st.checkbox("用户留存与复购分析", value=True)
        
        # Anomaly detection thresholds
        if show_anomaly_detection:
            st.markdown("### ⚠️ 异常检测阈值设置")
            large_order_threshold = st.slider(
                "大额订单阈值 (¥)",
                min_value=1000,
                max_value=20000,
                value=5000,
                step=500,
                help="超过此金额的订单视为大额订单"
            )
            
            high_freq_days = st.slider(
                "高频检测时间窗口 (天)",
                min_value=3,
                max_value=30,
                value=7,
                step=1,
                help="在多少天内统计下单频率"
            )
            
            high_freq_count = st.slider(
                "高频下单次数阈值",
                min_value=3,
                max_value=20,
                value=5,
                step=1,
                help="在时间窗口内下单次数超过此值视为高频"
            )
        else:
            large_order_threshold = 5000
            high_freq_days = 7
            high_freq_count = 5
        
        # Chart options
        st.markdown("### 📊 图表选项")
        chart_theme = st.selectbox(
            "图表主题",
            ["默认", "暗色", "简洁"]
        )
        
        # Date range filter
        st.markdown("### 📅 时间筛选")
        use_date_filter = st.checkbox("启用日期筛选")
    
    # Main content
    try:
        # Load data
        if data_source == "使用示例数据":
            with st.spinner("正在加载示例数据..."):
                df, processor = load_sample_data()
        else:
            uploaded_file = st.file_uploader(
                "选择CSV文件",
                type=['csv'],
                help="请上传包含订单数据的CSV文件"
            )
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    processor = DataProcessor()
                    df = processor.clean_data(df)
                    st.success(f"成功加载 {len(df)} 条订单记录")
                except Exception as e:
                    st.error(f"文件加载失败: {str(e)}")
                    return
            else:
                st.info("请上传CSV文件以开始分析")
                return
        
        # Date filter
        if use_date_filter and 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'])
            min_date = df['order_date'].min().date()
            max_date = df['order_date'].max().date()
            
            date_range = st.sidebar.date_input(
                "选择日期范围",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                df = df[(df['order_date'].dt.date >= start_date) & 
                       (df['order_date'].dt.date <= end_date)]
                st.info(f"已筛选 {start_date} 到 {end_date} 的数据，共 {len(df)} 条记录")
        
        # Initialize analyzer
        analyzer = OrderAnalyzer(df)
        
        # Display basic info
        st.markdown("## 📋 数据概览")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总订单数", f"{len(df):,}")
        with col2:
            st.metric("总销售额", f"¥{df['total_amount'].sum():,.2f}")
        with col3:
            st.metric("平均订单价值", f"¥{df['total_amount'].mean():.2f}")
        with col4:
            st.metric("客户数量", f"{df['customer_id'].nunique():,}")
        
        # Basic Statistics
        if show_basic_stats:
            st.markdown("## 📊 基本统计分析")
            
            basic_stats = analyzer.basic_statistics()
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 订单统计")
                st.json({
                    "总订单数": basic_stats['total_orders'],
                    "总收入": f"¥{basic_stats['total_revenue']:.2f}",
                    "平均订单价值": f"¥{basic_stats['average_order_value']:.2f}",
                    "订单价值中位数": f"¥{basic_stats['median_order_value']:.2f}"
                })
            
            with col2:
                st.markdown("### 客户与产品")
                st.json({
                    "总客户数": basic_stats['total_customers'],
                    "总产品数": basic_stats['total_products'],
                    "产品类别数": basic_stats['total_categories']
                })
        
        # Time Series Analysis
        if show_time_analysis:
            st.markdown("## 📈 时间序列分析")
            
            # Interactive sales trend chart
            fig_trend = create_interactive_charts(df)
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Monthly analysis
            monthly_sales = df.groupby(df['order_date'].dt.to_period('M')).agg({
                'total_amount': 'sum',
                'order_id': 'count'
            }).reset_index()
            monthly_sales['month'] = monthly_sales['order_date'].astype(str)
            
            fig_monthly = px.line(monthly_sales, x='month', y='total_amount',
                                title='月度销售趋势',
                                labels={'total_amount': '销售额 (¥)', 'month': '月份'})
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        # Customer Analysis
        if show_customer_analysis:
            st.markdown("## 👥 客户分析")
            
            customer_analysis = analyzer.customer_analysis()
            
            # Customer metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "平均客户价值", 
                    f"¥{customer_analysis['customer_value_metrics']['avg_customer_value']:.2f}"
                )
            with col2:
                st.metric(
                    "客户留存率", 
                    f"{customer_analysis['customer_value_metrics']['customer_retention_rate']:.1%}"
                )
            with col3:
                st.metric(
                    "平均订单数/客户", 
                    f"{customer_analysis['customer_value_metrics']['avg_orders_per_customer']:.1f}"
                )
            
            # Customer demographics chart
            fig_customer = create_customer_analysis_chart(df)
            st.plotly_chart(fig_customer, use_container_width=True)
        
        # Product Analysis
        if show_product_analysis:
            st.markdown("## 🛍️ 产品分析")
            
            # Category distribution
            fig_category = create_category_chart(df)
            st.plotly_chart(fig_category, use_container_width=True)
            
            # Top products
            top_products = df.groupby('product_name').agg({
                'total_amount': 'sum',
                'quantity': 'sum',
                'order_id': 'count'
            }).reset_index().sort_values('total_amount', ascending=False).head(10)
            
            st.markdown("### 🏆 热销产品 TOP 10")
            st.dataframe(
                top_products.rename(columns={
                    'product_name': '产品名称',
                    'total_amount': '销售额',
                    'quantity': '销量',
                    'order_id': '订单数'
                })
            )
        
        # ============================================================
        # 商品销售分析模块（新增）
        # ============================================================
        if show_product_sales:
            st.markdown('<div class="section-header">📊 商品销售分析</div>', unsafe_allow_html=True)
            
            with st.spinner("正在进行商品销售分析..."):
                product_sales_analysis = analyze_product_sales(df)
                product_charts = create_product_sales_charts(df, product_sales_analysis)
            
            # 热销/滞销商品识别
            st.markdown('<div class="subsection-header">🏷️ 热销商品与滞销商品识别</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                hot_count = len(product_charts['hot_products'])
                st.markdown(f'<div class="success-box">🔥 <strong>热销商品</strong>：{hot_count} 个</div>', unsafe_allow_html=True)
                if not product_charts['hot_products'].empty:
                    st.dataframe(
                        product_charts['hot_products'][['product_name', 'total_quantity', 'total_revenue', 'revenue_contribution']].head(10).rename(columns={
                            'product_name': '商品名称',
                            'total_quantity': '销量',
                            'total_revenue': '销售额',
                            'revenue_contribution': '贡献占比(%)'
                        })
                    )
            
            with col2:
                cold_count = len(product_charts['cold_products'])
                st.markdown(f'<div class="warning-box">❄️ <strong>滞销商品</strong>：{cold_count} 个</div>', unsafe_allow_html=True)
                if not product_charts['cold_products'].empty:
                    st.dataframe(
                        product_charts['cold_products'][['product_name', 'total_quantity', 'total_revenue', 'revenue_contribution']].head(10).rename(columns={
                            'product_name': '商品名称',
                            'total_quantity': '销量',
                            'total_revenue': '销售额',
                            'revenue_contribution': '贡献占比(%)'
                        })
                    )
            
            # 商品销量和销售额排行
            st.markdown('<div class="subsection-header">📈 商品销量与销售额排行</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(product_charts['fig_quantity_rank'], use_container_width=True)
            with col2:
                st.plotly_chart(product_charts['fig_revenue_rank'], use_container_width=True)
            
            # 商品销售贡献占比
            st.markdown('<div class="subsection-header">🥧 商品销售贡献占比</div>', unsafe_allow_html=True)
            st.plotly_chart(product_charts['fig_contribution'], use_container_width=True)
            
            # 商品销售趋势图
            st.markdown('<div class="subsection-header">📉 商品销售趋势图</div>', unsafe_allow_html=True)
            st.plotly_chart(product_charts['fig_monthly_trend'], use_container_width=True)
            
            # 商品价格带分析
            st.markdown('<div class="subsection-header">💰 商品价格带分析</div>', unsafe_allow_html=True)
            st.plotly_chart(product_charts['fig_price_band'], use_container_width=True)
            
            # 价格带统计表格
            st.markdown("**价格带销售统计详情**")
            price_band_df = product_sales_analysis['price_band_stats'].rename(columns={
                'price_band': '价格带',
                'revenue': '销售额',
                'quantity': '销量',
                'orders': '订单数'
            })
            st.dataframe(price_band_df)
        
        # ============================================================
        # 异常订单检测模块（新增）
        # ============================================================
        if show_anomaly_detection:
            st.markdown('<div class="section-header">⚠️ 异常订单检测</div>', unsafe_allow_html=True)
            
            with st.spinner("正在进行异常订单检测..."):
                anomalies = detect_anomalous_orders(
                    df, 
                    large_order_threshold=large_order_threshold,
                    high_frequency_days=high_freq_days,
                    high_frequency_count=high_freq_count
                )
                anomaly_charts = create_anomaly_charts(df, anomalies, large_order_threshold)
            
            # 异常订单统计概览
            st.markdown('<div class="subsection-header">📊 异常订单统计概览</div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                large_count = len(anomalies['large_orders'])
                st.metric("大额订单数", f"{large_count:,}")
            
            with col2:
                high_freq_count_actual = len(anomalies['high_freq_customers']) if not anomalies['high_freq_customers'].empty else 0
                st.metric("高频下单客户", f"{high_freq_count_actual:,}")
            
            with col3:
                discount_count = len(anomalies['anomalous_discount'])
                st.metric("异常折扣订单", f"{discount_count:,}")
            
            with col4:
                anomaly_day_count = len(anomalies['anomaly_days'])
                st.metric("异常交易日", f"{anomaly_day_count:,}")
            
            # 带异常点标记的散点图
            st.markdown('<div class="subsection-header">🔍 订单异常检测散点图</div>', unsafe_allow_html=True)
            st.plotly_chart(anomaly_charts['fig_scatter'], use_container_width=True)
            
            # 交易波动预警图表
            st.markdown('<div class="subsection-header">📉 交易波动预警图表</div>', unsafe_allow_html=True)
            st.plotly_chart(anomaly_charts['fig_volatility'], use_container_width=True)
            
            # 异常类型分布
            st.markdown('<div class="subsection-header">🥧 异常订单类型分布</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.plotly_chart(anomaly_charts['fig_anomaly_pie'], use_container_width=True)
            
            # 异常订单详情表格
            st.markdown('<div class="subsection-header">📋 异常订单详情表格</div>', unsafe_allow_html=True)
            
            # 显示各种异常订单详情
            tab1, tab2, tab3 = st.tabs(["大额订单", "高频下单", "异常折扣"])
            
            with tab1:
                if not anomalies['large_orders'].empty:
                    large_display = anomalies['large_orders'][['order_id', 'customer_id', 'product_name', 'quantity', 'unit_price', 'total_amount', 'order_date']].copy()
                    large_display = large_display.rename(columns={
                        'order_id': '订单ID',
                        'customer_id': '客户ID',
                        'product_name': '商品名称',
                        'quantity': '数量',
                        'unit_price': '单价',
                        'total_amount': '订单金额',
                        'order_date': '订单日期'
                    })
                    st.dataframe(large_display)
                else:
                    st.info("未检测到大额订单")
            
            with tab2:
                if not anomalies['high_freq_customers'].empty:
                    st.markdown("**高频下单客户列表**")
                    hf_customers = anomalies['high_freq_customers'].copy()
                    hf_customers = hf_customers.rename(columns={
                        'customer_id': '客户ID',
                        'start_date': '起始日期',
                        'end_date': '结束日期',
                        'order_count': '下单次数',
                        'days_diff': '间隔天数'
                    })
                    st.dataframe(hf_customers)
                    
                    st.markdown("**高频客户订单详情**")
                    hf_orders = anomalies['high_freq_orders'][['order_id', 'customer_id', 'product_name', 'total_amount', 'order_date']].copy()
                    hf_orders = hf_orders.rename(columns={
                        'order_id': '订单ID',
                        'customer_id': '客户ID',
                        'product_name': '商品名称',
                        'total_amount': '订单金额',
                        'order_date': '订单日期'
                    })
                    st.dataframe(hf_orders)
                else:
                    st.info("未检测到高频下单客户")
            
            with tab3:
                if not anomalies['anomalous_discount'].empty:
                    discount_display = anomalies['anomalous_discount'][['order_id', 'customer_id', 'product_name', 'unit_price', 'avg_price', 'discount_ratio', 'total_amount', 'order_date']].copy()
                    discount_display['discount_ratio'] = discount_display['discount_ratio'].apply(lambda x: f"{x*100:.1f}%")
                    discount_display = discount_display.rename(columns={
                        'order_id': '订单ID',
                        'customer_id': '客户ID',
                        'product_name': '商品名称',
                        'unit_price': '实际单价',
                        'avg_price': '商品均价',
                        'discount_ratio': '折扣比例',
                        'total_amount': '订单金额',
                        'order_date': '订单日期'
                    })
                    st.dataframe(discount_display)
                else:
                    st.info("未检测到异常折扣订单")
        
        # ============================================================
        # 用户留存与复购深化分析模块（新增）
        # ============================================================
        if show_retention_analysis:
            st.markdown('<div class="section-header">👥 用户留存与复购深化分析</div>', unsafe_allow_html=True)
            
            with st.spinner("正在进行用户留存与复购分析..."):
                retention_analysis = analyze_retention_repurchase(df)
                retention_charts = create_retention_charts(retention_analysis)
            
            # 核心指标概览
            st.markdown('<div class="subsection-header">📊 新用户复购核心指标</div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("总新用户数", f"{retention_analysis['total_new_users']:,}")
            
            with col2:
                st.metric(
                    "7天复购用户", 
                    f"{retention_analysis['repurchase_7d']:,}",
                    f"{retention_analysis['repurchase_rate_7d']:.1f}%"
                )
            
            with col3:
                st.metric(
                    "30天复购用户", 
                    f"{retention_analysis['repurchase_30d']:,}",
                    f"{retention_analysis['repurchase_rate_30d']:.1f}%"
                )
            
            with col4:
                lifecycle_count = len(retention_analysis['lifecycle_distribution'])
                st.metric("生命周期阶段数", f"{lifecycle_count}")
            
            # 新用户复购分析
            st.markdown('<div class="subsection-header">📈 新用户首购后复购情况</div>', unsafe_allow_html=True)
            st.plotly_chart(retention_charts['fig_repurchase'], use_container_width=True)
            
            # 新用户与复购用户月度趋势
            st.markdown('<div class="subsection-header">📅 新用户与复购用户月度趋势</div>', unsafe_allow_html=True)
            st.plotly_chart(retention_charts['fig_monthly_trend'], use_container_width=True)
            
            # 用户生命周期阶段分布
            st.markdown('<div class="subsection-header">🔄 用户生命周期阶段分布</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.plotly_chart(retention_charts['fig_lifecycle'], use_container_width=True)
            
            with col2:
                st.markdown("**生命周期阶段详细统计**")
                lifecycle_df = retention_analysis['lifecycle_distribution'].rename(columns={
                    'stage': '生命周期阶段',
                    'count': '用户数量',
                    'percentage': '占比(%)'
                })
                lifecycle_df['占比(%)'] = lifecycle_df['占比(%)'].apply(lambda x: f"{x:.1f}%")
                st.dataframe(lifecycle_df)
            
            # 不同渠道用户的留存差异（城市作为渠道）
            st.markdown('<div class="subsection-header">🌍 不同渠道用户的留存差异</div>', unsafe_allow_html=True)
            st.plotly_chart(retention_charts['fig_city_retention'], use_container_width=True)
            
            # 城市留存详情表格
            st.markdown("**各城市留存详情**")
            city_df = retention_analysis['city_stats'].rename(columns={
                'city': '城市',
                'total_customers': '总客户数',
                'total_orders': '总订单数',
                'repeat_customers': '复购客户数',
                'retention_rate': '留存率(%)'
            })
            city_df['留存率(%)'] = city_df['留存率(%)'].apply(lambda x: f"{x:.1f}%")
            st.dataframe(city_df.head(15))
            
            # RFM分布散点图
            st.markdown('<div class="subsection-header">🎯 用户RFM分布与生命周期阶段</div>', unsafe_allow_html=True)
            st.plotly_chart(retention_charts['fig_rfm_scatter'], use_container_width=True)
        
        # Export options
        st.markdown("## 📥 导出选项")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("生成完整报告"):
                with st.spinner("正在生成报告..."):
                    # Generate comprehensive analysis
                    basic_stats = analyzer.basic_statistics()
                    time_analysis = analyzer.time_series_analysis()
                    customer_analysis = analyzer.customer_analysis()
                    product_analysis = analyzer.product_analysis()
                    
                    analysis_results = {
                        'basic_stats': basic_stats,
                        'time_analysis': time_analysis,
                        'customer_analysis': customer_analysis,
                        'product_analysis': product_analysis
                    }
                    
                    # Generate report
                    analyzer.generate_report(analysis_results)
                    st.success("报告已生成并保存到 output/reports/ 目录")
        
        with col2:
            # Download processed data
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8')
            st.download_button(
                label="下载处理后数据",
                data=csv_buffer.getvalue(),
                file_name=f"processed_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col3:
            # Download analysis summary
            if st.button("下载分析摘要"):
                summary = {
                    "分析时间": datetime.now().isoformat(),
                    "数据记录数": len(df),
                    "分析期间": f"{df['order_date'].min()} 到 {df['order_date'].max()}",
                    "总销售额": float(df['total_amount'].sum()),
                    "平均订单价值": float(df['total_amount'].mean()),
                    "客户数量": int(df['customer_id'].nunique())
                }
                
                json_str = json.dumps(summary, ensure_ascii=False, indent=2)
                st.download_button(
                    label="下载JSON摘要",
                    data=json_str,
                    file_name=f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    except Exception as e:
        st.error(f"分析过程中发生错误: {str(e)}")
        st.exception(e)
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666;">'
        '🚀 电商订单数据分析平台 | 基于 Streamlit 构建'
        '</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()