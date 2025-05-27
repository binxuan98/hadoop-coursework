# -*- coding: utf-8 -*-
"""
Unit Tests for Analysis Module
分析模块单元测试

This module contains unit tests for the analysis module.
本模块包含analysis模块的单元测试。
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
import json
import sys
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.analysis import OrderAnalyzer
from src.data_utils import DataProcessor

class TestOrderAnalyzer(unittest.TestCase):
    """
    Test cases for OrderAnalyzer class
    OrderAnalyzer类的测试用例
    """
    
    def setUp(self):
        """
        Set up test fixtures before each test method
        在每个测试方法之前设置测试装置
        """
        # Create sample test data
        np.random.seed(42)  # For reproducible results
        
        # Generate date range
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Create sample orders
        n_orders = 100
        self.sample_data = pd.DataFrame({
            'order_id': [f'ORD{i:04d}' for i in range(1, n_orders + 1)],
            'customer_id': [f'CUST{np.random.randint(1, 21):03d}' for _ in range(n_orders)],
            'customer_name': [f'Customer_{i}' for i in np.random.randint(1, 21, n_orders)],
            'customer_email': [f'customer{i}@email.com' for i in np.random.randint(1, 21, n_orders)],
            'customer_age': np.random.randint(18, 70, n_orders),
            'customer_gender': np.random.choice(['Male', 'Female'], n_orders),
            'customer_city': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'], n_orders),
            'product_id': [f'PROD{np.random.randint(1, 11):03d}' for _ in range(n_orders)],
            'product_name': np.random.choice(['Laptop', 'Phone', 'Tablet', 'Headphones', 'Watch'], n_orders),
            'product_category': np.random.choice(['Electronics', 'Accessories', 'Computers'], n_orders),
            'quantity': np.random.randint(1, 5, n_orders),
            'unit_price': np.round(np.random.uniform(50, 1000, n_orders), 2),
            'order_date': np.random.choice(date_range, n_orders)
        })
        
        # Calculate total_amount
        self.sample_data['total_amount'] = self.sample_data['quantity'] * self.sample_data['unit_price']
        
        # Add derived columns (simulating cleaned data)
        self.sample_data['order_year'] = self.sample_data['order_date'].dt.year
        self.sample_data['order_month'] = self.sample_data['order_date'].dt.month
        self.sample_data['order_quarter'] = self.sample_data['order_date'].dt.quarter
        self.sample_data['order_weekday'] = self.sample_data['order_date'].dt.day_name()
        
        # Add age groups
        self.sample_data['age_group'] = pd.cut(
            self.sample_data['customer_age'],
            bins=[0, 25, 35, 45, 60, 100],
            labels=['18-25', '26-35', '36-45', '46-60', '60+'],
            right=False
        )
        
        # Initialize analyzer
        self.analyzer = OrderAnalyzer(self.sample_data)
        
        # Set up temp directory for reports
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """
        Clean up after each test method
        每个测试方法后清理
        """
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """
        Test OrderAnalyzer initialization
        测试OrderAnalyzer初始化
        """
        self.assertIsInstance(self.analyzer.df, pd.DataFrame)
        self.assertEqual(len(self.analyzer.df), 100)
        self.assertGreater(len(self.analyzer.df.columns), 10)
    
    def test_get_basic_statistics(self):
        """
        Test basic statistics calculation
        测试基本统计计算
        """
        stats = self.analyzer.get_basic_statistics()
        
        # Check that all expected keys are present
        expected_keys = [
            'total_orders', 'total_revenue', 'average_order_value',
            'unique_customers', 'unique_products', 'unique_categories',
            'date_range_start', 'date_range_end'
        ]
        
        for key in expected_keys:
            self.assertIn(key, stats)
        
        # Check data types and values
        self.assertIsInstance(stats['total_orders'], int)
        self.assertIsInstance(stats['total_revenue'], (int, float))
        self.assertIsInstance(stats['average_order_value'], (int, float))
        self.assertIsInstance(stats['unique_customers'], int)
        self.assertIsInstance(stats['unique_products'], int)
        self.assertIsInstance(stats['unique_categories'], int)
        
        # Check logical constraints
        self.assertEqual(stats['total_orders'], 100)
        self.assertGreater(stats['total_revenue'], 0)
        self.assertGreater(stats['average_order_value'], 0)
        self.assertLessEqual(stats['unique_customers'], stats['total_orders'])
        self.assertLessEqual(stats['unique_products'], stats['total_orders'])
        
        # Check that average order value is calculated correctly
        expected_aov = stats['total_revenue'] / stats['total_orders']
        self.assertAlmostEqual(stats['average_order_value'], expected_aov, places=2)
    
    def test_analyze_time_series(self):
        """
        Test time series analysis
        测试时间序列分析
        """
        time_analysis = self.analyzer.analyze_time_series()
        
        # Check that all expected keys are present
        expected_keys = [
            'daily_sales', 'monthly_sales', 'quarterly_sales',
            'weekly_pattern', 'seasonal_trends'
        ]
        
        for key in expected_keys:
            self.assertIn(key, time_analysis)
        
        # Check daily sales
        daily_sales = time_analysis['daily_sales']
        self.assertIsInstance(daily_sales, pd.DataFrame)
        self.assertIn('total_amount', daily_sales.columns)
        self.assertIn('order_count', daily_sales.columns)
        
        # Check monthly sales
        monthly_sales = time_analysis['monthly_sales']
        self.assertIsInstance(monthly_sales, pd.DataFrame)
        self.assertLessEqual(len(monthly_sales), 12)  # Max 12 months
        
        # Check quarterly sales
        quarterly_sales = time_analysis['quarterly_sales']
        self.assertIsInstance(quarterly_sales, pd.DataFrame)
        self.assertLessEqual(len(quarterly_sales), 4)  # Max 4 quarters
        
        # Check weekly pattern
        weekly_pattern = time_analysis['weekly_pattern']
        self.assertIsInstance(weekly_pattern, pd.DataFrame)
        self.assertLessEqual(len(weekly_pattern), 7)  # Max 7 days
        
        # Check that all amounts are positive
        self.assertTrue((daily_sales['total_amount'] >= 0).all())
        self.assertTrue((daily_sales['order_count'] > 0).all())
    
    def test_analyze_customers(self):
        """
        Test customer analysis
        测试客户分析
        """
        customer_analysis = self.analyzer.analyze_customers()
        
        # Check that all expected keys are present
        expected_keys = [
            'customer_value', 'rfm_analysis', 'demographics'
        ]
        
        for key in expected_keys:
            self.assertIn(key, customer_analysis)
        
        # Check customer value analysis
        customer_value = customer_analysis['customer_value']
        self.assertIsInstance(customer_value, pd.DataFrame)
        
        expected_value_cols = [
            'total_spent', 'avg_order_value', 'order_count', 'days_since_last_order'
        ]
        for col in expected_value_cols:
            self.assertIn(col, customer_value.columns)
        
        # Check RFM analysis
        rfm_analysis = customer_analysis['rfm_analysis']
        self.assertIsInstance(rfm_analysis, pd.DataFrame)
        
        expected_rfm_cols = ['recency', 'frequency', 'monetary', 'rfm_segment']
        for col in expected_rfm_cols:
            self.assertIn(col, rfm_analysis.columns)
        
        # Check demographics
        demographics = customer_analysis['demographics']
        self.assertIsInstance(demographics, dict)
        
        expected_demo_keys = ['age_distribution', 'gender_distribution', 'city_distribution']
        for key in expected_demo_keys:
            self.assertIn(key, demographics)
        
        # Check that RFM segments are valid
        valid_segments = ['Champions', 'Loyal Customers', 'Potential Loyalists', 
                         'New Customers', 'Promising', 'Need Attention', 
                         'About to Sleep', 'At Risk', 'Cannot Lose Them', 'Hibernating']
        
        unique_segments = rfm_analysis['rfm_segment'].unique()
        for segment in unique_segments:
            self.assertIn(segment, valid_segments)
    
    def test_analyze_products(self):
        """
        Test product analysis
        测试产品分析
        """
        product_analysis = self.analyzer.analyze_products()
        
        # Check that all expected keys are present
        expected_keys = ['product_performance', 'category_analysis']
        
        for key in expected_keys:
            self.assertIn(key, product_analysis)
        
        # Check product performance
        product_performance = product_analysis['product_performance']
        self.assertIsInstance(product_performance, pd.DataFrame)
        
        expected_product_cols = [
            'total_revenue', 'total_quantity', 'order_count', 'avg_unit_price'
        ]
        for col in expected_product_cols:
            self.assertIn(col, product_performance.columns)
        
        # Check category analysis
        category_analysis = product_analysis['category_analysis']
        self.assertIsInstance(category_analysis, pd.DataFrame)
        
        expected_category_cols = [
            'total_revenue', 'total_quantity', 'order_count', 'avg_unit_price', 'market_share'
        ]
        for col in expected_category_cols:
            self.assertIn(col, category_analysis.columns)
        
        # Check that market share sums to approximately 100%
        total_market_share = category_analysis['market_share'].sum()
        self.assertAlmostEqual(total_market_share, 100.0, places=1)
        
        # Check that all values are positive
        self.assertTrue((product_performance['total_revenue'] > 0).all())
        self.assertTrue((product_performance['total_quantity'] > 0).all())
        self.assertTrue((category_analysis['total_revenue'] > 0).all())
    
    def test_rfm_segmentation(self):
        """
        Test RFM segmentation logic
        测试RFM细分逻辑
        """
        customer_analysis = self.analyzer.analyze_customers()
        rfm_analysis = customer_analysis['rfm_analysis']
        
        # Check that RFM scores are in valid ranges
        self.assertTrue((rfm_analysis['recency'] >= 1).all())
        self.assertTrue((rfm_analysis['recency'] <= 5).all())
        self.assertTrue((rfm_analysis['frequency'] >= 1).all())
        self.assertTrue((rfm_analysis['frequency'] <= 5).all())
        self.assertTrue((rfm_analysis['monetary'] >= 1).all())
        self.assertTrue((rfm_analysis['monetary'] <= 5).all())
        
        # Check that segments are assigned
        self.assertFalse(rfm_analysis['rfm_segment'].isnull().any())
        
        # Check that high-value customers have appropriate segments
        high_monetary = rfm_analysis[rfm_analysis['monetary'] >= 4]
        if len(high_monetary) > 0:
            high_value_segments = ['Champions', 'Loyal Customers', 'Potential Loyalists', 'Cannot Lose Them']
            # At least some high monetary customers should be in high-value segments
            self.assertTrue(any(segment in high_value_segments for segment in high_monetary['rfm_segment'].unique()))
    
    def test_generate_report(self):
        """
        Test report generation
        测试报告生成
        """
        # Mock the reports directory
        import sys
        sys.path.append(str(project_root))
        from config import REPORTS_DIR
        
        # Temporarily change reports directory to temp directory
        original_reports_dir = REPORTS_DIR
        import config
        config.REPORTS_DIR = self.temp_dir
        
        try:
            report = self.analyzer.generate_report()
            
            # Check report structure
            self.assertIsInstance(report, dict)
            
            expected_keys = [
                'metadata', 'executive_summary', 'detailed_analysis', 'recommendations'
            ]
            
            for key in expected_keys:
                self.assertIn(key, report)
            
            # Check metadata
            metadata = report['metadata']
            self.assertIn('analysis_date', metadata)
            self.assertIn('data_period', metadata)
            self.assertIn('total_records', metadata)
            
            # Check executive summary
            exec_summary = report['executive_summary']
            self.assertIsInstance(exec_summary, dict)
            self.assertIn('total_revenue', exec_summary)
            self.assertIn('total_orders', exec_summary)
            
            # Check detailed analysis
            detailed_analysis = report['detailed_analysis']
            self.assertIsInstance(detailed_analysis, dict)
            
            expected_analysis_keys = ['basic_stats', 'time_analysis', 'customer_analysis', 'product_analysis']
            for key in expected_analysis_keys:
                self.assertIn(key, detailed_analysis)
            
            # Check recommendations
            recommendations = report['recommendations']
            self.assertIsInstance(recommendations, list)
            self.assertGreater(len(recommendations), 0)
            
            # Check that files were created
            json_report_path = self.temp_dir / 'analysis_report.json'
            md_report_path = self.temp_dir / 'analysis_report.md'
            
            self.assertTrue(json_report_path.exists())
            self.assertTrue(md_report_path.exists())
            
            # Validate JSON file
            with open(json_report_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                self.assertEqual(json_data, report)
            
            # Validate Markdown file
            with open(md_report_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
                self.assertIn('# E-commerce Order Analysis Report', md_content)
                self.assertIn('## Executive Summary', md_content)
                self.assertIn('## Key Metrics', md_content)
        
        finally:
            # Restore original reports directory
            config.REPORTS_DIR = original_reports_dir
    
    def test_edge_cases(self):
        """
        Test edge cases and error handling
        测试边界情况和错误处理
        """
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        
        with self.assertRaises((ValueError, KeyError)):
            OrderAnalyzer(empty_df)
        
        # Test with minimal data
        minimal_data = pd.DataFrame({
            'order_id': ['ORD001'],
            'customer_id': ['CUST001'],
            'product_id': ['PROD001'],
            'total_amount': [100.0],
            'order_date': [datetime.now()],
            'customer_age': [25],
            'customer_gender': ['Male'],
            'customer_city': ['New York'],
            'product_category': ['Electronics'],
            'quantity': [1],
            'unit_price': [100.0]
        })
        
        # Add required derived columns
        minimal_data['order_year'] = minimal_data['order_date'].dt.year
        minimal_data['order_month'] = minimal_data['order_date'].dt.month
        minimal_data['order_quarter'] = minimal_data['order_date'].dt.quarter
        minimal_data['order_weekday'] = minimal_data['order_date'].dt.day_name()
        minimal_data['age_group'] = '18-25'
        
        minimal_analyzer = OrderAnalyzer(minimal_data)
        
        # Should not raise errors
        basic_stats = minimal_analyzer.get_basic_statistics()
        self.assertEqual(basic_stats['total_orders'], 1)
        self.assertEqual(basic_stats['total_revenue'], 100.0)
        
        time_analysis = minimal_analyzer.analyze_time_series()
        self.assertIsInstance(time_analysis, dict)
        
        customer_analysis = minimal_analyzer.analyze_customers()
        self.assertIsInstance(customer_analysis, dict)
        
        product_analysis = minimal_analyzer.analyze_products()
        self.assertIsInstance(product_analysis, dict)
    
    def test_data_validation(self):
        """
        Test data validation in analyzer
        测试分析器中的数据验证
        """
        # Test with missing required columns
        incomplete_data = self.sample_data.drop(columns=['total_amount'])
        
        with self.assertRaises(KeyError):
            OrderAnalyzer(incomplete_data)
        
        # Test with invalid data types
        invalid_data = self.sample_data.copy()
        invalid_data['total_amount'] = 'invalid'  # Should be numeric
        
        # Should handle gracefully or raise appropriate error
        try:
            analyzer = OrderAnalyzer(invalid_data)
            # If it doesn't raise an error, the analysis should still work
            stats = analyzer.get_basic_statistics()
            self.assertIsInstance(stats, dict)
        except (ValueError, TypeError):
            # This is also acceptable behavior
            pass

class TestOrderAnalyzerIntegration(unittest.TestCase):
    """
    Integration tests for OrderAnalyzer
    OrderAnalyzer集成测试
    """
    
    def setUp(self):
        """
        Set up integration test fixtures
        设置集成测试装置
        """
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Generate realistic test data using DataProcessor
        self.processor = DataProcessor()
        self.data_path = self.temp_dir / 'test_orders.csv'
        
        # Generate sample data
        self.processor.generate_sample_data(
            num_orders=200,
            date_range=('2023-01-01', '2023-12-31'),
            output_path=self.data_path
        )
        
        # Load and clean data
        df_raw = self.processor.load_data(self.data_path)
        self.df_clean = self.processor.clean_data(df_raw)
        
        # Initialize analyzer
        self.analyzer = OrderAnalyzer(self.df_clean)
    
    def tearDown(self):
        """
        Clean up after integration tests
        集成测试后清理
        """
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_full_analysis_pipeline(self):
        """
        Test the complete analysis pipeline
        测试完整的分析流水线
        """
        # Run all analysis methods
        basic_stats = self.analyzer.get_basic_statistics()
        time_analysis = self.analyzer.analyze_time_series()
        customer_analysis = self.analyzer.analyze_customers()
        product_analysis = self.analyzer.analyze_products()
        
        # Verify all analyses completed successfully
        self.assertIsInstance(basic_stats, dict)
        self.assertIsInstance(time_analysis, dict)
        self.assertIsInstance(customer_analysis, dict)
        self.assertIsInstance(product_analysis, dict)
        
        # Check data consistency across analyses
        total_revenue_basic = basic_stats['total_revenue']
        total_revenue_time = time_analysis['daily_sales']['total_amount'].sum()
        
        # Should be approximately equal (allowing for floating point differences)
        self.assertAlmostEqual(total_revenue_basic, total_revenue_time, places=2)
        
        # Check customer count consistency
        unique_customers_basic = basic_stats['unique_customers']
        unique_customers_analysis = len(customer_analysis['customer_value'])
        
        self.assertEqual(unique_customers_basic, unique_customers_analysis)
    
    def test_report_generation_integration(self):
        """
        Test report generation with real data
        测试使用真实数据生成报告
        """
        # Mock the reports directory
        import config
        original_reports_dir = config.REPORTS_DIR
        config.REPORTS_DIR = self.temp_dir
        
        try:
            # Generate comprehensive report
            report = self.analyzer.generate_report()
            
            # Verify report completeness
            self.assertIsInstance(report, dict)
            
            # Check that all sections have meaningful content
            exec_summary = report['executive_summary']
            self.assertGreater(exec_summary['total_revenue'], 0)
            self.assertGreater(exec_summary['total_orders'], 0)
            self.assertGreater(exec_summary['unique_customers'], 0)
            
            # Check that recommendations are provided
            recommendations = report['recommendations']
            self.assertIsInstance(recommendations, list)
            self.assertGreater(len(recommendations), 3)  # Should have multiple recommendations
            
            # Verify file outputs
            json_file = self.temp_dir / 'analysis_report.json'
            md_file = self.temp_dir / 'analysis_report.md'
            
            self.assertTrue(json_file.exists())
            self.assertTrue(md_file.exists())
            
            # Check file sizes (should not be empty)
            self.assertGreater(json_file.stat().st_size, 1000)  # At least 1KB
            self.assertGreater(md_file.stat().st_size, 2000)   # At least 2KB
        
        finally:
            # Restore original configuration
            config.REPORTS_DIR = original_reports_dir

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)