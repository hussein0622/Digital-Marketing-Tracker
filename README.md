# Digital-Marketing-Tracker

A professional web application for marketing teams and sales analysts to predict the likelihood of lead conversion using machine learning. The app provides actionable insights, campaign analytics, and downloadable PDF reports to optimize marketing strategies.

## Features

- **Lead Conversion Prediction**: Predicts the probability that a lead will convert using a trained ML model.
- **Interactive Dashboard**: Visualizes campaign performance (CTR, impressions) with modern charts.
- **Leads Management**: Add, view, and delete leads with interest-level analysis.
- **PDF Report Generation**: Download custom reports with prediction results and recommendations.
- **Custom Recommendations**: Actionable next steps based on prediction outcome.
- **Data Upload**: Update campaign data via CSV upload.
- **User-Friendly Interface**: Responsive design with clear navigation.
- **Error Handling**: User-friendly error messages and robust backend validation.

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, Bootstrap, Chart.js
- **Machine Learning**: Scikit-learn (pretrained model in `conversion_model_intern.pkl`)
- **PDF Generation**: ReportLab
- **Data Storage**: CSV files (for campaigns and leads)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd heart_failure_prediction
   ```
2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**
   ```bash
   python app_intern.py
   ```
5. **Access the app**
   Open your browser at [http://localhost:5000](http://localhost:5000)

## Usage

- **Predict Conversion**: Fill out the lead form and get a probability of conversion, with a pie chart visualization.
- **Download PDF Report**: After prediction, click "Generate PDF Report" for a downloadable summary and recommendations.
- **Manage Leads**: View, add, or delete leads. Analyze interest level distribution.
- **Campaign Dashboard**: Monitor campaign metrics (CTR, impressions) with interactive charts.
- **Upload Campaign Data**: Replace campaign data by uploading a properly formatted CSV file.

## File Structure

- `app_intern.py` – Main Flask application
- `data/` – Contains `campaigns_intern.csv`, `leads_intern.csv`, and ML model
- `templates/` – HTML templates (predict_intern.html, report_intern.html, leads_intern.html, etc.)
- `static/` – Custom CSS and JS (Chart.js integration)
- `requirements.txt` – Python dependencies

## Dependencies

- Flask
- numpy
- scikit-learn
- reportlab

Install all dependencies with `pip install -r requirements.txt`.

## Example CSV Format

**Campaigns CSV** (`data/campaigns_intern.csv`):
```
campaign_name,clicks,impressions,ctr,date
Summer Sale 2025,1200,15000,8.0,2025-06-01
```

**Leads CSV** (`data/leads_intern.csv`):
```
name,email,interest_level
John Doe,john@example.com,4
```

## License

This project is for educational and internal marketing analytics use only.

---
For questions or support, contact the project maintainer.
