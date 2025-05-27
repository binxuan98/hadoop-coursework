# -*- coding: utf-8 -*-
"""
Unit Tests for Data Utils Module
数据工具模块单元测试

This module contains unit tests for the data_utils module.
本模块包含data_utils模块的单元测试。
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.data_utils import DataProcessor
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR

class TestDataProcessor(unittest.TestCase):
    """
    Test cases for DataProcessor class
    DataProcessor类的测试用例
    """
    
    def setUp(self):
        """
        Set up test fixtures before each test method
        在每个测试方法之前设置测试装置
        """
        self.processor = DataProcessor()
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create sample test data
        self.sample_data = pd.DataFrame({
            'order_id': ['ORD001', 'ORD002', 'ORD003', 'ORD004', 'ORD005'],
            'customer_id': ['CUST001', 'CUST002', 'CUST001', 'CUST003', 'CUST002'],
            'customer_name': ['Alice', 'Bob', 'Alice', 'Charlie', 'Bob'],
            'customer_email': ['alice@email.com', 'bob@email.com', 'alice@email.com', 'charlie@email.com', 'bob@email.com'],
            'customer_age': [25, 35, 25, 45, 35],
            'customer_gender': ['Female', 'Male', 'Female', 'Male', 'Male'],
            'customer_city': ['New York', 'Los Angeles', 'New York', 'Chicago', 'Los Angeles'],
            'product_id': ['PROD001', 'PROD002', 'PROD003', 'PROD001', 'PROD002'],
            'product_name': ['Laptop', 'Phone', 'Tablet', 'Laptop', 'Phone'],
            'product_category': ['Electronics', 'Electronics', 'Electronics', 'Electronics', 'Electronics'],
            'quantity': [1, 2, 1, 1, 1],
            'unit_price': [999.99, 599.99, 399.99, 999.99, 599.99],
            'total_amount': [999.99, 1199.98, 399.99, 999.99, 599.99],
            'order_date': ['2023-01-15', '2023-01-16', '2023-01-17', '2023-01-18', '2023-01-19']
        })
        
        # Save sample data to temp file
        self.test_file_path = self.temp_dir / 'test_orders.csv'
        self.sample_data.to_csv(self.test_file_path, index=False)
    
    def tearDown(self):
        """
        Clean up after each test method
        每个测试方法后清理
        """
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_load_data(self):
        """
        Test data loading functionality
        测试数据加载功能
        """
        # Test successful loading
        df = self.processor.load_data(self.test_file_path)
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 5)
        self.assertEqual(len(df.columns), 14)
        self.assertIn('order_id', df.columns)
        self.assertIn('customer_id', df.columns)
        self.assertIn('total_amount', df.columns)
        
        # Test loading non-existent file
        with self.assertRaises(FileNotFoundError):
            self.processor.load_data(self.temp_dir / 'non_existent.csv')
    
    def test_clean_data(self):
        """
        Test data cleaning functionality
        测试数据清洗功能
        """
        # Load and clean data
        df = self.processor.load_data(self.test_file_path)
        df_clean = self.processor.clean_data(df)
        
        # Check that data is cleaned
        self.assertIsInstance(df_clean, pd.DataFrame)
        self.assertLessEqual(len(df_clean), len(df))  # Should not increase rows
        
        # Check data types
        self.assertEqual(df_clean['order_date'].dtype, 'datetime64[ns]')
        self.assertTrue(pd.api.types.is_numeric_dtype(df_clean['quantity']))
        self.assertTrue(pd.api.types.is_numeric_dtype(df_clean['unit_price']))
        self.assertTrue(pd.api.types.is_numeric_dtype(df_clean['total_amount']))
        
        # Check for derived columns
        expected_derived_cols = ['order_year', 'order_month', 'order_quarter', 'order_weekday', 'age_group']
        for col in expected_derived_cols:
            self.assertIn(col, df_clean.columns)
        
        # Check no missing values in critical columns
        critical_cols = ['order_id', 'customer_id', 'product_id', 'total_amount']
        for col in critical_cols:
            self.assertEqual(df_clean[col].isnull().sum(), 0)
    
    def test_clean_data_with_missing_values(self):
        """
        Test data cleaning with missing values
        测试包含缺失值的数据清洗
        """
        # Create data with missing values
        df_with_missing = self.sample_data.copy()
        df_with_missing.loc[0, 'customer_name'] = np.nan
        df_with_missing.loc[1, 'total_amount'] = np.nan
        df_with_missing.loc[2, 'quantity'] = np.nan
        
        df_clean = self.processor.clean_data(df_with_missing)
        
        # Should handle missing values appropriately
        self.assertIsInstance(df_clean, pd.DataFrame)
        # Critical columns should not have missing values
        self.assertEqual(df_clean['order_id'].isnull().sum(), 0)
        self.assertEqual(df_clean['customer_id'].isnull().sum(), 0)
    
    def test_clean_data_with_duplicates(self):
        """
        Test data cleaning with duplicate rows
        测试包含重复行的数据清洗
        """
        # Create data with duplicates
        df_with_duplicates = pd.concat([self.sample_data, self.sample_data.iloc[:2]], ignore_index=True)
        
        df_clean = self.processor.clean_data(df_with_duplicates)
        
        # Should remove duplicates
        self.assertLessEqual(len(df_clean), len(df_with_duplicates))
        self.assertEqual(df_clean.duplicated().sum(), 0)
    
    def test_clean_data_with_outliers(self):
        """
        Test data cleaning with outliers
        测试包含异常值的数据清洗
        """
        # Create data with outliers
        df_with_outliers = self.sample_data.copy()
        df_with_outliers.loc[0, 'quantity'] = 1000  # Extreme quantity
        df_with_outliers.loc[1, 'unit_price'] = -100  # Negative price
        df_with_outliers.loc[2, 'customer_age'] = 200  # Impossible age
        
        df_clean = self.processor.clean_data(df_with_outliers)
        
        # Should handle outliers
        self.assertIsInstance(df_clean, pd.DataFrame)
        # All remaining values should be reasonable
        self.assertTrue((df_clean['quantity'] > 0).all())
        self.assertTrue((df_clean['unit_price'] > 0).all())
        self.assertTrue((df_clean['customer_age'] >= 18).all())
        self.assertTrue((df_clean['customer_age'] <= 100).all())
    
    def test_generate_sample_data(self):
        """
        Test sample data generation
        测试示例数据生成
        """
        # Generate sample data
        output_path = self.temp_dir / 'generated_orders.csv'
        result_path = self.processor.generate_sample_data(
            num_orders=100,
            date_range=('2023-01-01', '2023-12-31'),
            output_path=output_path
        )
        
        # Check that file was created
        self.assertTrue(output_path.exists())
        self.assertEqual(result_path, output_path)
        
        # Load and validate generated data
        df = pd.read_csv(output_path)
        
        self.assertEqual(len(df), 100)
        self.assertGreater(len(df.columns), 10)
        
        # Check required columns exist
        required_cols = ['order_id', 'customer_id', 'product_id', 'total_amount', 'order_date']
        for col in required_cols:
            self.assertIn(col, df.columns)
        
        # Check data quality
        self.assertEqual(df['order_id'].nunique(), 100)  # All order IDs should be unique
        self.assertTrue((df['total_amount'] > 0).all())  # All amounts should be positive
        self.assertTrue((df['quantity'] > 0).all())  # All quantities should be positive
    
    def test_generate_data_quality_report(self):
        """
        Test data quality report generation
        测试数据质量报告生成
        """
        df = self.processor.load_data(self.test_file_path)
        df_clean = self.processor.clean_data(df)
        
        # Generate quality report
        quality_report = self.processor._generate_data_quality_report(df_clean)
        
        # Check report structure
        self.assertIsInstance(quality_report, dict)
        
        expected_keys = [
            'total_rows', 'total_columns', 'missing_values_summary',
            'duplicate_rows', 'data_types_summary', 'memory_usage_mb'
        ]
        
        for key in expected_keys:
            self.assertIn(key, quality_report)
        
        # Check report values
        self.assertEqual(quality_report['total_rows'], len(df_clean))
        self.assertEqual(quality_report['total_columns'], len(df_clean.columns))
        self.assertIsInstance(quality_report['missing_values_summary'], dict)
        self.assertIsInstance(quality_report['duplicate_rows'], int)
        self.assertIsInstance(quality_report['memory_usage_mb'], float)
    
    def test_age_group_assignment(self):
        """
        Test age group assignment logic
        测试年龄组分配逻辑
        """
        df = self.processor.load_data(self.test_file_path)
        df_clean = self.processor.clean_data(df)
        
        # Check age group assignments
        age_groups = df_clean['age_group'].unique()
        expected_groups = ['18-25', '26-35', '36-45', '46-60', '60+']
        
        for group in age_groups:
            self.assertIn(group, expected_groups)
        
        # Test specific age assignments
        young_customers = df_clean[df_clean['customer_age'] == 25]
        if len(young_customers) > 0:
            self.assertEqual(young_customers['age_group'].iloc[0], '18-25')
        
        middle_customers = df_clean[df_clean['customer_age'] == 35]
        if len(middle_customers) > 0:
            self.assertEqual(middle_customers['age_group'].iloc[0], '26-35')
    
    def test_data_consistency_validation(self):
        """
        Test data consistency validation
        测试数据一致性验证
        """
        df = self.processor.load_data(self.test_file_path)
        df_clean = self.processor.clean_data(df)
        
        # Check that total_amount = quantity * unit_price (approximately)
        calculated_total = df_clean['quantity'] * df_clean['unit_price']
        difference = abs(df_clean['total_amount'] - calculated_total)
        
        # Allow for small floating point differences
        self.assertTrue((difference < 0.01).all(), "Total amount should equal quantity * unit_price")
        
        # Check that all IDs are properly formatted
        self.assertTrue(df_clean['order_id'].str.startswith('ORD').all())
        self.assertTrue(df_clean['customer_id'].str.startswith('CUST').all())
        self.assertTrue(df_clean['product_id'].str.startswith('PROD').all())

class TestDataProcessorIntegration(unittest.TestCase):
    """
    Integration tests for DataProcessor
    DataProcessor集成测试
    """
    
    def setUp(self):
        """
        Set up integration test fixtures
        设置集成测试装置
        """
        self.processor = DataProcessor()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """
        Clean up after integration tests
        集成测试后清理
        """
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_full_data_pipeline(self):
        """
        Test the complete data processing pipeline
        测试完整的数据处理流水线
        """
        # Generate sample data
        raw_data_path = self.temp_dir / 'raw_orders.csv'
        self.processor.generate_sample_data(
            num_orders=50,
            output_path=raw_data_path
        )
        
        # Load data
        df_raw = self.processor.load_data(raw_data_path)
        
        # Clean data
        df_clean = self.processor.clean_data(df_raw)
        
        # Save processed data
        processed_data_path = self.temp_dir / 'processed_orders.csv'
        df_clean.to_csv(processed_data_path, index=False)
        
        # Verify the pipeline worked
        self.assertTrue(raw_data_path.exists())
        self.assertTrue(processed_data_path.exists())
        
        # Load processed data and verify
        df_final = pd.read_csv(processed_data_path)
        
        self.assertIsInstance(df_final, pd.DataFrame)
        self.assertGreater(len(df_final), 0)
        self.assertLessEqual(len(df_final), 50)  # Should not exceed original
        
        # Check that all required columns exist
        required_cols = [
            'order_id', 'customer_id', 'product_id', 'total_amount',
            'order_year', 'order_month', 'age_group'
        ]
        for col in required_cols:
            self.assertIn(col, df_final.columns)

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)