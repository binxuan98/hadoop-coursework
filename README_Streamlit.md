# 电商订单数据分析 Streamlit 网页应用

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements_streamlit.txt
```

### 2. 启动应用
```bash
streamlit run app.py
```

### 3. 访问应用
打开浏览器访问: http://localhost:8501

## 📊 功能特性

### 🔧 数据源选项
- **示例数据**: 使用内置的10,000条示例订单数据
- **文件上传**: 支持上传自定义CSV文件进行分析

### 📈 分析模块
- **基本统计**: 订单总数、销售额、平均订单价值等关键指标
- **时间序列分析**: 日销售趋势、月度趋势分析
- **客户分析**: 客户价值分析、年龄组分布、留存率等
- **产品分析**: 产品类别分布、热销产品排行

### 📊 交互式图表
- 基于 Plotly 的交互式图表
- 支持缩放、悬停、筛选等操作
- 响应式设计，适配不同屏幕尺寸

### 🎛️ 高级功能
- **日期筛选**: 支持自定义时间范围分析
- **图表主题**: 多种图表主题选择
- **数据导出**: 支持下载处理后的数据和分析报告
- **实时分析**: 上传数据后即时生成分析结果

## 📁 项目结构

```
hadoop_coursework/
├── app.py                      # Streamlit 主应用文件
├── requirements_streamlit.txt   # Streamlit 依赖包
├── .streamlit/
│   └── config.toml             # Streamlit 配置文件
├── src/                        # 核心分析模块
│   ├── analysis.py             # 数据分析引擎
│   ├── data_utils.py           # 数据处理工具
│   ├── visualization.py        # 可视化模块
│   └── config.py               # 配置文件
├── data/                       # 数据目录
└── output/                     # 输出目录
    ├── charts/                 # 图表文件
    └── reports/                # 分析报告
```

## 🎯 使用指南

### 数据上传要求
上传的CSV文件应包含以下列（或类似结构）：
- `order_id`: 订单ID
- `customer_id`: 客户ID
- `product_name`: 产品名称
- `product_category`: 产品类别
- `quantity`: 数量
- `unit_price`: 单价
- `total_amount`: 总金额
- `order_date`: 订单日期
- `customer_age`: 客户年龄
- `customer_gender`: 客户性别
- `customer_city`: 客户城市

### 分析流程
1. **选择数据源**: 使用示例数据或上传自定义文件
2. **配置分析选项**: 选择需要的分析模块
3. **设置筛选条件**: 可选择特定时间范围
4. **查看分析结果**: 浏览交互式图表和统计数据
5. **导出结果**: 下载分析报告和处理后的数据

## 🔧 技术栈

- **前端框架**: Streamlit
- **数据处理**: Pandas, NumPy
- **可视化**: Plotly, Matplotlib, Seaborn
- **分析算法**: Scikit-learn
- **配置管理**: TOML

## 📈 性能优化

- 使用 `@st.cache_data` 缓存数据加载
- Plotly 图表支持大数据集渲染
- 分页显示大型数据表
- 异步数据处理

## 🚨 注意事项

1. **数据隐私**: 上传的数据仅在本地处理，不会发送到外部服务器
2. **文件大小**: 建议上传文件不超过100MB以确保良好性能
3. **浏览器兼容**: 推荐使用 Chrome、Firefox 或 Safari 最新版本
4. **端口占用**: 默认使用8501端口，如有冲突可在配置文件中修改

## 🔄 更新日志

### v1.0.0 (2025-05-28)
- ✨ 初始版本发布
- 📊 支持基本统计分析
- 📈 时间序列分析功能
- 👥 客户分析模块
- 🛍️ 产品分析功能
- 📱 响应式界面设计
- 📥 数据导出功能

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📄 许可证

MIT License