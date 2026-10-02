# E-Commerce Customer Analytics

## Project Overview
This project analyzes e-commerce transactions to understand sales performance, customer purchasing behavior, product categories, and delivery performance using Python, SQL, and data visualization.

## Objectives
- Analyze monthly order and sales trends.
- Identify popular product categories.
- Understand repeat customer behavior.
- Evaluate delivery time and late deliveries.
- Explore relationships between delivery performance and customer reviews.

## Tools and Technologies
- **Python:** Pandas, NumPy, Matplotlib, Seaborn
- **SQL:** Data analysis and aggregation queries
- **Data Visualization:** Charts and summary reports
- **GitHub:** Version control and project documentation

## Dataset
The project uses the Brazilian E-Commerce Public Dataset by Olist.

Dataset link: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Download the dataset separately and place the required CSV files inside the `data/` directory. Raw dataset files are excluded from Git tracking.

## Project Structure
```text
ecommerce-customer-analytics/
├── data/
│   └── README.md
├── reports/
│   └── README.md
├── sql/
│   └── analysis_queries.sql
├── src/
│   └── analyze.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup and Usage

1. Clone or download this repository.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Download the dataset and place the required CSV files inside `data/`.
4. Run the analysis script:

   ```bash
   python src/analyze.py
   ```

5. Review the generated summaries and visualization outputs.

## Key Business Questions
- How do order volumes change over time?
- Which product categories contribute most to sales?
- How many customers make repeat purchases?
- How long does delivery typically take?
- Are late deliveries associated with lower customer review scores?

## Limitations
The findings depend on the available dataset, data quality, and selected metrics. Observed relationships do not necessarily imply causation.

## Author
Anisha Dey
