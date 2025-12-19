# 💰 Savings Analysis Dashboard

A Streamlit web application for analyzing disputes and identifying savings opportunities. The dashboard visualizes **savings** (positive discrepancy values) vs **underbilled amounts** (negative discrepancy values) from dispute data.

## Features

- 📊 **Key Metrics**: Total savings, underbilled amounts, and net impact
- 📈 **Time Analysis**: Daily and monthly trends of savings vs underbilled
- 🏢 **Category Analysis**: Breakdown by customer, site, item type, and discrepancy type
- 📋 **Top Disputes**: Identify highest savings and underbilled cases
- 🔍 **Advanced Filtering**: Filter by status, type, customer, and date range
- 📥 **Data Export**: Download filtered data as CSV

## Visualizations

- **Green** = Savings (positive values) - money saved/overcharged
- **Red** = Underbilled (negative values) - money that should have been charged

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mladenburic-sketch/savings-analisys.git
cd savings-analisys
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Data Format

The application expects a CSV file (`data/disputes-all-data.csv`) with the following columns:
- `po_number`: Purchase order number
- `disputedAt`: Date of dispute
- `discrepancy_value`: Value of the discrepancy (positive = savings, negative = underbilled)
- `customerName`: Customer name
- `siteName`: Site name
- `item`: Item description
- `discrepancy_type`: Type of discrepancy
- `gallons`: Number of gallons (if applicable)
- And other relevant fields

## Project Structure

```
savings-analisys/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── data/                  # Data folder
│   └── disputes-all-data.csv
└── src/                   # Source modules
    ├── data_loader.py     # Data loading and cleaning
    ├── calculations.py   # Metrics and calculations
    └── visualizations.py # Chart generation
```

## Usage

1. Upload or place your disputes CSV file in the `data/` folder
2. Open the application in your browser
3. Use the sidebar filters to focus on specific categories or time periods
4. Explore different tabs for various analysis views
5. Export filtered data as needed

## Technologies

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations

## License

This project is open source and available for use.

