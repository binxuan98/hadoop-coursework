# E-commerce Order Analysis Project
# 电商订单数据分析项目

## 项目简介 (Project Overview)

这是一个适合大专学生的数据分析项目，通过分析电商订单数据来学习数据处理、可视化和分析技能。项目使用Python开发，包含完整的数据分析流程。

This is a data analysis project suitable for college students to learn data processing, visualization, and analysis skills through e-commerce order data analysis. The project is developed in Python and includes a complete data analysis workflow.

## 项目特点 (Features)

- 📊 **贴近生活**: 使用电商订单数据，学生容易理解
- 💻 **轻量级**: 仅需CPU运行，无需GPU
- 🏗️ **结构清晰**: 模块化设计，易于理解和扩展
- 📈 **可视化丰富**: 使用多种图表展示分析结果
- 🎯 **评分标准**: 包含完整的项目评分体系
- 👥 **团队协作**: 支持多人协作开发

## 项目结构 (Project Structure)

```
ecommerce-order-analysis/
├── README.md                 # 项目说明文档
├── requirements.txt          # 依赖包列表
├── main.py                  # 主程序入口
├── config.py                # 配置文件
├── data/                    # 数据目录
│   ├── raw/                 # 原始数据
│   │   └── sample_orders.csv
│   └── processed/           # 处理后数据
├── src/                     # 源代码目录
│   ├── __init__.py
│   ├── data_utils.py        # 数据处理工具
│   ├── visualization.py     # 可视化模块
│   ├── analysis.py          # 分析模块
│   └── evaluation.py        # 评分模块
├── notebooks/               # Jupyter笔记本
│   └── analysis.ipynb       # 分析笔记本
├── output/                  # 输出目录
│   ├── charts/              # 图表输出
│   └── reports/             # 报告输出
└── tests/                   # 测试文件
    └── test_data_utils.py
```

## 安装和运行 (Installation and Usage)

### 1. 环境要求 (Requirements)

- Python 3.7+
- pip

### 2. 安装依赖 (Install Dependencies)

```bash
# 克隆项目
git clone <your-repo-url>
cd ecommerce-order-analysis

# 安装依赖
pip install -r requirements.txt
```

### 3. 运行项目 (Run Project)

```bash
# 运行主程序
python main.py

# 或者使用Jupyter笔记本
jupyter notebook notebooks/analysis.ipynb
```

## 数据说明 (Data Description)

项目使用模拟的电商订单数据，包含以下字段：

- `order_id`: 订单ID
- `customer_id`: 客户ID
- `product_category`: 产品类别
- `product_name`: 产品名称
- `quantity`: 购买数量
- `unit_price`: 单价
- `total_amount`: 总金额
- `order_date`: 订单日期
- `customer_age`: 客户年龄
- `customer_gender`: 客户性别
- `customer_city`: 客户城市

## 分析内容 (Analysis Content)

1. **数据清洗和预处理**
   - 缺失值处理
   - 异常值检测
   - 数据类型转换

2. **描述性统计分析**
   - 基本统计信息
   - 分布分析
   - 相关性分析

3. **销售趋势分析**
   - 时间序列分析
   - 季节性分析
   - 增长趋势

4. **客户分析**
   - 客户画像
   - 购买行为分析
   - 客户价值分析

5. **产品分析**
   - 产品销量排行
   - 类别分析
   - 价格分析

## 评分标准 (Evaluation Criteria)

| 评分项目 | 权重 | 评分标准 |
|---------|------|----------|
| 数据清洗 | 20% | 缺失值处理、异常值检测、数据质量 |
| 数据分析 | 30% | 分析方法正确性、深度、创新性 |
| 可视化 | 25% | 图表规范性、美观性、信息传达效果 |
| 代码质量 | 15% | 代码规范、注释、可读性 |
| 报告撰写 | 10% | 结论合理性、逻辑性、表达清晰度 |

## 学习目标 (Learning Objectives)

完成本项目后，学生将掌握：

- Python数据分析基础
- Pandas数据处理技能
- Matplotlib/Seaborn可视化技能
- 数据清洗和预处理方法
- 统计分析基础
- 项目管理和团队协作

## 扩展建议 (Extension Suggestions)

- 添加机器学习预测模型
- 实现交互式仪表板
- 集成更多数据源
- 添加实时数据处理
- 部署到云平台

## 贡献指南 (Contributing)

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证 (License)

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式 (Contact)

如有问题，请联系：
- 邮箱：your-email@example.com
- GitHub：[your-github-username](https://github.com/your-github-username)

---

**注意**: 这是一个教学项目，数据为模拟生成，仅用于学习目的。

**Note**: This is an educational project with simulated data for learning purposes only.