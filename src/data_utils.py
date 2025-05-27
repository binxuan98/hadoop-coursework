# -*- coding: utf-8 -*-
"""
Data Processing Utilities for E-commerce Order Analysis
电商订单分析数据处理工具

This module contains functions for data generation, loading, cleaning, and preprocessing.
本模块包含数据生成、加载、清洗和预处理功能。
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple

# Import configuration
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import DATA_GENERATION_CONFIG, ANALYSIS_CONFIG

class DataProcessor:
    """
    Data processing class for e-commerce order analysis
    电商订单分析数据处理类
    """
    
    def __init__(self):
        """
        Initialize the DataProcessor
        初始化数据处理器
        """
        self.logger = logging.getLogger(__name__)
        np.random.seed(ANALYSIS_CONFIG["random_seed"])
        random.seed(ANALYSIS_CONFIG["random_seed"])
    
    def generate_sample_data(self, output_file: Optional[Path] = None) -> pd.DataFrame:
        """
        Generate sample e-commerce order data
        生成示例电商订单数据
        
        Args:
            output_file: Path to save the generated data
        
        Returns:
            DataFrame containing sample order data
        """
        self.logger.info("Generating sample e-commerce order data")
        
        config = DATA_GENERATION_CONFIG
        
        # Generate date range
        start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(config["end_date"], "%Y-%m-%d")
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate product data
        products = self._generate_products()
        
        # Generate customer data
        customers = self._generate_customers(config["num_customers"], config["cities"])
        
        # Generate orders
        orders = []
        for i in range(config["num_orders"]):
            order = self._generate_single_order(i+1, date_range, products, customers)
            orders.append(order)
        
        df = pd.DataFrame(orders)
        
        if output_file:
            df.to_csv(output_file, index=False, encoding='utf-8')
            self.logger.info(f"Sample data saved to {output_file}")
        
        self.logger.info(f"Generated {len(df)} sample orders")
        return df
    
    def _generate_products(self) -> List[Dict]:
        """
        Generate product catalog
        生成产品目录
        """
        products = []
        categories = DATA_GENERATION_CONFIG["product_categories"]
        
        product_names = {
            "Electronics": ["iPhone 14", "Samsung Galaxy", "MacBook Pro", "iPad", "AirPods", "Gaming Laptop"],
            "Clothing": ["T-Shirt", "Jeans", "Dress", "Jacket", "Sneakers", "Sweater"],
            "Books": ["Python Programming", "Data Science", "Machine Learning", "Web Development", "AI Handbook"],
            "Home & Garden": ["Coffee Maker", "Vacuum Cleaner", "Garden Tools", "Kitchen Set", "Sofa"],
            "Sports": ["Running Shoes", "Yoga Mat", "Dumbbells", "Tennis Racket", "Basketball"],
            "Beauty": ["Skincare Set", "Makeup Kit", "Perfume", "Hair Dryer", "Face Mask"],
            "Toys": ["LEGO Set", "Board Game", "Action Figure", "Puzzle", "Remote Car"],
            "Food": ["Organic Tea", "Chocolate", "Snack Box", "Coffee Beans", "Honey"],
            "Health": ["Vitamins", "Protein Powder", "First Aid Kit", "Thermometer", "Massage Gun"],
            "Automotive": ["Car Charger", "Dash Cam", "Car Cover", "Tire Pump", "Car Accessories"]
        }
        
        price_ranges = {
            "Electronics": (100, 5000),
            "Clothing": (20, 300),
            "Books": (15, 80),
            "Home & Garden": (30, 800),
            "Sports": (25, 500),
            "Beauty": (10, 200),
            "Toys": (15, 150),
            "Food": (5, 100),
            "Health": (20, 300),
            "Automotive": (25, 400)
        }
        
        for category in categories:
            for product_name in product_names[category]:
                min_price, max_price = price_ranges[category]
                products.append({
                    "category": category,
                    "name": product_name,
                    "base_price": round(np.random.uniform(min_price, max_price), 2)
                })
        
        return products
    
    def _generate_customers(self, num_customers: int, cities: List[str]) -> List[Dict]:
        """
        Generate customer data
        生成客户数据
        """
        customers = []
        for i in range(num_customers):
            customers.append({
                "customer_id": f"CUST_{i+1:06d}",
                "age": np.random.randint(18, 70),
                "gender": np.random.choice(["Male", "Female"], p=[0.48, 0.52]),
                "city": np.random.choice(cities)
            })
        return customers
    
    def _generate_single_order(self, order_id: int, date_range: pd.DatetimeIndex, 
                              products: List[Dict], customers: List[Dict]) -> Dict:
        """
        Generate a single order
        生成单个订单
        """
        # Select random customer and product
        customer = random.choice(customers)
        product = random.choice(products)
        
        # Generate order details
        quantity = np.random.randint(1, 6)
        unit_price = product["base_price"] * np.random.uniform(0.8, 1.2)  # Add price variation
        total_amount = quantity * unit_price
        
        # Add seasonal effects to order date probability
        order_date = np.random.choice(date_range)
        
        # Convert numpy datetime64 to pandas Timestamp for strftime
        if isinstance(order_date, np.datetime64):
            order_date = pd.Timestamp(order_date)
        
        return {
            "order_id": f"ORD_{order_id:08d}",
            "customer_id": customer["customer_id"],
            "product_category": product["category"],
            "product_name": product["name"],
            "quantity": quantity,
            "unit_price": round(unit_price, 2),
            "total_amount": round(total_amount, 2),
            "order_date": order_date.strftime("%Y-%m-%d"),
            "customer_age": customer["age"],
            "customer_gender": customer["gender"],
            "customer_city": customer["city"]
        }
    
    def load_data(self, file_path: Path) -> pd.DataFrame:
        """
        Load data from CSV file
        从CSV文件加载数据
        
        Args:
            file_path: Path to the CSV file
        
        Returns:
            DataFrame containing the loaded data
        """
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            self.logger.info(f"Loaded {len(df)} records from {file_path}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading data from {file_path}: {str(e)}")
            raise
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and preprocess the data
        清洗和预处理数据
        
        Args:
            df: Raw DataFrame
        
        Returns:
            Cleaned DataFrame
        """
        self.logger.info("Starting data cleaning process")
        
        # Create a copy to avoid modifying original data
        cleaned_df = df.copy()
        
        # Convert data types
        cleaned_df['order_date'] = pd.to_datetime(cleaned_df['order_date'])
        cleaned_df['quantity'] = pd.to_numeric(cleaned_df['quantity'], errors='coerce')
        cleaned_df['unit_price'] = pd.to_numeric(cleaned_df['unit_price'], errors='coerce')
        cleaned_df['total_amount'] = pd.to_numeric(cleaned_df['total_amount'], errors='coerce')
        cleaned_df['customer_age'] = pd.to_numeric(cleaned_df['customer_age'], errors='coerce')
        
        # Handle missing values
        initial_rows = len(cleaned_df)
        cleaned_df = cleaned_df.dropna(subset=['order_id', 'customer_id', 'product_name'])
        
        # Fill missing numerical values with median
        numerical_columns = ['quantity', 'unit_price', 'total_amount', 'customer_age']
        for col in numerical_columns:
            if cleaned_df[col].isnull().any():
                median_value = cleaned_df[col].median()
                cleaned_df[col].fillna(median_value, inplace=True)
        
        # Remove duplicates
        cleaned_df = cleaned_df.drop_duplicates(subset=['order_id'])
        
        # Remove outliers (orders with unrealistic values)
        cleaned_df = cleaned_df[
            (cleaned_df['quantity'] > 0) & (cleaned_df['quantity'] <= 100) &
            (cleaned_df['unit_price'] > 0) & (cleaned_df['unit_price'] <= 50000) &
            (cleaned_df['total_amount'] > 0) & (cleaned_df['total_amount'] <= 500000) &
            (cleaned_df['customer_age'] >= 18) & (cleaned_df['customer_age'] <= 100)
        ]
        
        # Add derived columns
        cleaned_df['order_year'] = cleaned_df['order_date'].dt.year
        cleaned_df['order_month'] = cleaned_df['order_date'].dt.month
        cleaned_df['order_quarter'] = cleaned_df['order_date'].dt.quarter
        cleaned_df['order_weekday'] = cleaned_df['order_date'].dt.day_name()
        
        # Add customer age groups
        cleaned_df['age_group'] = pd.cut(
            cleaned_df['customer_age'], 
            bins=[0, 25, 35, 45, 55, 100], 
            labels=['18-25', '26-35', '36-45', '46-55', '55+']
        )
        
        final_rows = len(cleaned_df)
        self.logger.info(f"Data cleaning completed. Rows: {initial_rows} -> {final_rows}")
        
        return cleaned_df
    
    def save_data(self, df: pd.DataFrame, file_path: Path) -> None:
        """
        Save DataFrame to CSV file
        保存DataFrame到CSV文件
        
        Args:
            df: DataFrame to save
            file_path: Output file path
        """
        try:
            df.to_csv(file_path, index=False, encoding='utf-8')
            self.logger.info(f"Data saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving data to {file_path}: {str(e)}")
            raise
    
    def get_data_quality_report(self, df: pd.DataFrame) -> Dict:
        """
        Generate data quality report
        生成数据质量报告
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            Dictionary containing data quality metrics
        """
        report = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "duplicate_rows": df.duplicated().sum(),
            "data_types": df.dtypes.to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "date_range": {
                "start": df['order_date'].min(),
                "end": df['order_date'].max()
            } if 'order_date' in df.columns else None
        }
        
        return report