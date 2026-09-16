# Interactive Dashboard & KPI Visualizations

## Project Objective

This project is a professional Streamlit and Plotly business intelligence dashboard for exploring retail sales, customer, product, and geographic performance. It detects common equivalent column names at runtime so that a cleaned retail CSV can be used without hard-coding one exact schema.

## Features

- Executive KPI cards for revenue, orders, customers, AOV, units, profit, and profit margin.
- Honest availability handling for CAC and churn: neither metric is invented when required fields are absent.
- Sidebar filters for year, month, category, sub-category, region, state, and date range when available.
- Interactive Plotly trend, category, regional, geographic, customer, and top-item charts.
- Year-to-month, category-to-sub-category, and geographic drill-down controls.
- Safe date parsing, numeric conversion, missing-column handling, empty-data handling, caching, and refresh.

## Dataset

Place `clean_dataset.csv` in the same folder as `app.py`. The application looks for common equivalents such as Sales or Revenue, Order Date or Date, Order ID, Customer ID, Category, Region, State, City, Quantity, Discount, and Profit.

## Technologies

Python, Streamlit, Pandas, NumPy, Plotly, GitHub, and Streamlit Community Cloud.

## Installation and VS Code

1. Open VS Code.
2. Create or open the project folder.
3. Put `clean_dataset.csv` beside `app.py`.
4. Open the VS Code terminal.
5. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

6. Activate it:

   ```powershell
   .\\.venv\\Scripts\\Activate.ps1
   ```

7. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

8. Run the dashboard:

   ```powershell
   streamlit run app.py
   ```

9. Open the local URL shown by Streamlit, normally `http://localhost:8501`.
10. Stop the app with `Ctrl+C` in the terminal.

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` for the current terminal session, then activate again.

## GitHub Upload

Replace the placeholder URL with your own repository URL:

```powershell
git init
git add .
git commit -m "Create interactive retail dashboard"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Do not add secrets to the repository. The CSV is intentionally not ignored because it is needed by the deployed app. For a very large CSV, use Git LFS or move the data to a hosted data source and update the loader.

## Streamlit Community Cloud

1. Push the project to GitHub.
2. Open Streamlit Community Cloud and sign in.
3. Choose **Create app** or **Deploy an app**.
4. Select your GitHub repository.
5. Select the `main` branch.
6. Set the app file to `app.py`.
7. Click **Deploy**.
8. After deployment, Streamlit displays a public app URL that can be shared and submitted.

## PDF Export

Open the deployed or local dashboard in a browser, wait for the charts to load, then use the browser menu **Print** and select **Save as PDF**. For the cleanest submission, expand the required dashboard sections, use landscape orientation if offered, and confirm that background graphics are enabled.

## Project Structure

```text
rebacademy/
|-- app.py
|-- clean_dataset.csv
|-- requirements.txt
|-- README.md
`-- .gitignore
```

## KPI Definitions and Limitations

- Revenue = sum of the detected sales or revenue field.
- Orders = distinct Order ID count; if Order ID is absent, row count is used only as a transparent fallback.
- Customers = distinct Customer ID or customer field count.
- AOV = total revenue divided by total orders.
- Units Sold = sum of Quantity.
- Profit = sum of Profit when available.
- Profit Margin = total profit divided by total revenue times 100 when both are available.
- CAC is not calculated without acquisition spend and newly acquired customer data.
- Churn Rate is not calculated without customer lifecycle activity and a defined churn period.

The dashboard cannot infer business definitions that are not represented in the CSV. Invalid dates are excluded from time charts, and missing optional dimensions produce informative unavailable states.

## Academic Documentation

### Project Description

An interactive retail business intelligence dashboard that converts transaction-level retail data into executive KPIs and interactive performance views.

### Objective

To enable decision-makers to monitor sales performance, order behavior, customer patterns, product/category performance, and regional results through a responsive and defensible dashboard.

### Tools and Technologies

Python, Streamlit, Pandas, NumPy, Plotly, GitHub, and Streamlit Community Cloud.

### Dataset

`clean_dataset.csv`, a cleaned retail transaction dataset supplied by the project owner. The application detects common column-name variants automatically.

### KPI Dictionary

| KPI | Definition | Formula | Business meaning | Required fields |
|---|---|---|---|---|
| Revenue | Total sales value | `SUM(Sales/Revenue)` | Overall commercial scale | Sales or Revenue |
| Orders | Unique orders | `COUNT DISTINCT(Order ID)` | Transaction volume | Order ID |
| Customers | Unique customers | `COUNT DISTINCT(Customer ID)` | Customer reach | Customer ID |
| AOV | Revenue per order | `Revenue / Orders` | Typical basket value | Revenue, Order ID |
| Units Sold | Total item quantity | `SUM(Quantity)` | Volume sold | Quantity |
| Profit | Total profit | `SUM(Profit)` | Absolute earnings | Profit |
| Profit Margin | Profit as a share of revenue | `Profit / Revenue * 100` | Profitability efficiency | Profit, Revenue |
| CAC | Acquisition cost per new customer | `Acquisition spend / New customers` | Cost efficiency of acquisition | Acquisition spend, newly acquired customers |
| Churn Rate | Customers lost during a defined period | `Lost customers / Starting customers * 100` | Retention health | Lifecycle activity, churn period |

CAC and churn are deliberately shown as unavailable unless the required fields and business definition are present.

### Dashboard Features

The app includes responsive KPI cards, interactive filters, hover and zoom-enabled Plotly charts, trend analysis, category and geographic analysis, customer order frequency, top-item ranking, and practical drill-down selectors.

### Data Limitations

Column names and optional fields may vary. Missing values, invalid dates, absent customer identifiers, and absent acquisition or lifecycle data limit which metrics can be calculated. A geographic heatmap is represented as a state/city/region performance view unless latitude and longitude are supplied.

### Key Business Insights

Use the filtered dashboard to identify revenue trends, leading categories, high-performing regions, concentration among top products, order frequency patterns, and periods where profitability diverges from revenue. Interpret all findings in the context of data availability and the selected filters.

### Conclusion

The dashboard provides an executive-ready, interactive view of retail performance while preserving analytical integrity. It calculates only metrics supported by the supplied data and clearly communicates limitations where CAC, churn, or other optional analyses cannot be defended.
