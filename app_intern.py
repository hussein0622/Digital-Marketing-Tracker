from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, make_response
import os
import csv
import re
import pickle
import uuid
import numpy as np
import io
import datetime
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

app = Flask(__name__)
app.secret_key = "digital_marketing_intern_app"  # Secret key for flash messages

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# File paths
CAMPAIGNS_CSV = 'data/campaigns_intern.csv'
LEADS_CSV = 'data/leads_intern.csv'
MODEL_PATH = 'data/conversion_model_intern.pkl'

# Load the machine learning model
def load_model():
    try:
        with open(MODEL_PATH, 'rb') as file:
            model = pickle.load(file)
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

# Create initial CSV files if they don't exist
def create_initial_files():
    # Create campaigns CSV if it doesn't exist
    if not os.path.exists(CAMPAIGNS_CSV):
        with open(CAMPAIGNS_CSV, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['campaign_name', 'clicks', 'impressions', 'ctr', 'date'])
            # Sample data
            writer.writerow(['Summer Sale 2025', '1200', '15000', '8.0', '2025-06-01'])
            writer.writerow(['Email Newsletter', '800', '10000', '8.0', '2025-06-15'])
            writer.writerow(['Social Media Ads', '1500', '20000', '7.5', '2025-06-20'])
            writer.writerow(['Google PPC', '2000', '30000', '6.7', '2025-06-25'])
            writer.writerow(['Influencer Campaign', '1800', '22000', '8.2', '2025-07-01'])

    # Create leads CSV if it doesn't exist
    if not os.path.exists(LEADS_CSV):
        with open(LEADS_CSV, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['name', 'email', 'interest_level'])
            # Sample data
            writer.writerow(['John Doe', 'john@example.com', '4'])
            writer.writerow(['Jane Smith', 'jane@example.com', '3'])
            writer.writerow(['Robert Johnson', 'robert@example.com', '5'])

# Helper function to read campaigns data
def read_campaigns_data():
    campaigns = []
    try:
        with open(CAMPAIGNS_CSV, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                campaigns.append(row)
        return campaigns
    except Exception as e:
        print(f"Error reading campaigns data: {e}")
        return []

# Helper function to read leads data
def read_leads_data():
    leads = []
    try:
        with open(LEADS_CSV, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                leads.append(row)
        return leads
    except Exception as e:
        print(f"Error reading leads data: {e}")
        return []

# Helper function to write leads data back to CSV
def write_leads_data(leads):
    try:
        with open(LEADS_CSV, 'w', newline='') as file:
            # Get the field names from the first lead or use default if no leads
            fieldnames = list(leads[0].keys()) if leads else ['name', 'email', 'interest_level']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for lead in leads:
                writer.writerow(lead)
        return True
    except Exception as e:
        print(f"Error writing leads data: {e}")
        return False

# Dashboard route
@app.route('/')
def dashboard():
    campaigns = read_campaigns_data()
    
    # Calculate metrics for dashboard cards
    total_campaigns = len(campaigns)
    
    # Calculate average CTR
    if total_campaigns > 0:
        avg_ctr = sum(float(campaign['ctr']) for campaign in campaigns) / total_campaigns
    else:
        avg_ctr = 0
    
    # Find top campaign by CTR and most impressions
    top_ctr_campaign = None
    most_impressions_campaign = None
    
    if campaigns:
        top_ctr_campaign = max(campaigns, key=lambda x: float(x['ctr']))
        most_impressions_campaign = max(campaigns, key=lambda x: int(x['impressions']))
    
    return render_template('dashboard_intern.html', 
                          total_campaigns=total_campaigns,
                          avg_ctr=avg_ctr,
                          top_ctr_campaign=top_ctr_campaign,
                          most_impressions_campaign=most_impressions_campaign,
                          campaigns=campaigns)

# Upload route
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if user submitted an empty form
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        # Check if the file has a CSV extension
        if not file.filename.endswith('.csv'):
            flash('File must be a CSV', 'danger')
            return redirect(request.url)
        
        try:
            # Secure the filename and save the file
            filename = secure_filename(file.filename)
            file_path = os.path.join('data', 'campaigns_intern.csv')
            file.save(file_path)
            
            # Validate file content
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                
                # Check headers
                required_headers = ['campaign_name', 'clicks', 'impressions', 'ctr', 'date']
                if not all(h in header for h in required_headers):
                    flash('CSV must contain the following headers: campaign_name, clicks, impressions, ctr, date', 'danger')
                    return redirect(request.url)
            
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('dashboard'))
        
        except Exception as e:
            flash(f'Error uploading file: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('upload_intern.html')

# Leads route
@app.route('/leads', methods=['GET', 'POST'])
def leads():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        interest_level = request.form.get('interest_level')
        
        # Form validation
        errors = []
        
        if not name or not name.strip():
            errors.append("Name is required")
        
        if not email or not email.strip():
            errors.append("Email is required")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("Invalid email format")
        
        if not interest_level:
            errors.append("Interest level is required")
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('leads'))
        
        # Save new lead to CSV
        try:
            with open(LEADS_CSV, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([name, email, interest_level])
            
            flash('Lead added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding lead: {str(e)}', 'danger')
        
        return redirect(url_for('leads'))
    
    # Get all leads for display
    leads_data = read_leads_data()
    return render_template('leads_intern.html', leads=leads_data)

# Delete lead route
@app.route('/delete-lead', methods=['POST'])
def delete_lead():
    name = request.form.get('name')
    email = request.form.get('email')
    
    if not name or not email:
        flash('Missing information to delete lead', 'danger')
        return redirect(url_for('leads'))
    
    try:
        # Get all leads
        all_leads = read_leads_data()
        
        # Filter out the lead to delete
        filtered_leads = [lead for lead in all_leads if not (lead['name'] == name and lead['email'] == email)]
        
        # Check if any lead was removed
        if len(filtered_leads) < len(all_leads):
            # Write back the filtered leads
            if write_leads_data(filtered_leads):
                flash('Lead deleted successfully!', 'success')
            else:
                flash('Error deleting lead', 'danger')
        else:
            flash('Lead not found', 'warning')
    
    except Exception as e:
        flash(f'Error deleting lead: {str(e)}', 'danger')
    
    return redirect(url_for('leads'))

# API endpoint for chart data
@app.route('/api/chart-data')
def chart_data():
    campaigns = read_campaigns_data()
    
    # Prepare data for CTR bar chart
    ctr_data = {
        'labels': [campaign['campaign_name'] for campaign in campaigns],
        'values': [float(campaign['ctr']) for campaign in campaigns]
    }
    
    # Prepare data for impressions line chart
    # Sort campaigns by date
    sorted_campaigns = sorted(campaigns, key=lambda x: x['date'])
    impressions_data = {
        'labels': [campaign['date'] for campaign in sorted_campaigns],
        'values': [int(campaign['impressions']) for campaign in sorted_campaigns]
    }
    
    return jsonify({
        'ctr': ctr_data,
        'impressions': impressions_data
    })

# Prediction route
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            # Get form data
            traffic_entry_point = request.form.get('traffic_entry_point')
            ad_source = request.form.get('ad_source')
            email_opt_out = request.form.get('email_opt_out')
            phone_opt_out = request.form.get('phone_opt_out')
            website_visits = float(request.form.get('website_visits'))
            time_on_site = float(request.form.get('time_on_site'))
            pages_per_session = float(request.form.get('pages_per_session'))
            last_engagement_type = request.form.get('last_engagement_type')
            last_conversion_signal = request.form.get('last_conversion_signal')
            
            # Boolean fields (checkboxes)
            came_from_paid_ads = 'Yes' if request.form.get('came_from_paid_ads') else 'No'
            referred_by_client = 'Yes' if request.form.get('referred_by_client') else 'No'
            subscribed_to_newsletter = 'Yes' if request.form.get('subscribed_to_newsletter') else 'No'
            requested_business_content = 'Yes' if request.form.get('requested_business_content') else 'No'
            requested_marketing_content = 'Yes' if request.form.get('requested_marketing_content') else 'No'
            
            # Prepare data for model (convert categorical variables to one-hot encoding)
            # This is a simplified version - in a real app, you'd need to match the exact preprocessing used during training
            
            # Load model
            model = load_model()
            if model is None:
                flash('Error: Could not load prediction model', 'danger')
                return redirect(url_for('predict'))
            
            # Create feature vector to match the expected 15 features
            # Based on the example provided and model requirements
            features = [
                # Traffic Entry Point - Split into multiple binary features
                1 if traffic_entry_point == 'Landing Page Submission' else 0,  # Landing Page
                1 if traffic_entry_point == 'API' else 0,  # API
                
                # Ad Source
                1 if ad_source == 'Google' else 0,
                
                # Opt-Outs
                1 if email_opt_out == 'Yes' else 0,
                1 if phone_opt_out == 'Yes' else 0,
                
                # Numeric features
                website_visits,
                time_on_site,
                pages_per_session,
                
                # Engagement and Conversion features
                1 if 'Email' in last_engagement_type else 0,
                1 if 'Form' in last_conversion_signal else 0,
                
                # Boolean features
                1 if came_from_paid_ads == 'Yes' else 0,
                1 if referred_by_client == 'Yes' else 0,
                1 if subscribed_to_newsletter == 'Yes' else 0,
                1 if requested_business_content == 'Yes' else 0,
                1 if requested_marketing_content == 'Yes' else 0
            ]
            
            # Reshape for prediction
            features_array = np.array(features).reshape(1, -1)
            
            # Make prediction
            prediction = int(model.predict(features_array)[0])
            
            # Get probability if model supports it
            probability = 0.5  # Default value
            try:
                probability_scores = model.predict_proba(features_array)[0]
                probability = probability_scores[1]  # Probability of class 1 (convert)
            except:
                # Model may not support predict_proba
                pass
            
            # Store form data for the template
            form_data = {
                'traffic_entry_point': traffic_entry_point,
                'ad_source': ad_source,
                'email_opt_out': email_opt_out,
                'phone_opt_out': phone_opt_out,
                'website_visits': website_visits,
                'time_on_site': time_on_site,
                'pages_per_session': pages_per_session,
                'last_engagement_type': last_engagement_type,
                'came_from_paid_ads': came_from_paid_ads,
                'referred_by_client': referred_by_client,
                'subscribed_to_newsletter': subscribed_to_newsletter,
                'requested_business_content': requested_business_content,
                'requested_marketing_content': requested_marketing_content,
                'last_conversion_signal': last_conversion_signal
            }
            
            return render_template('predict_intern.html', 
                                   prediction=prediction, 
                                   probability=probability, 
                                   form_data=form_data)
                                   
        except Exception as e:
            flash(f'Error making prediction: {str(e)}', 'danger')
            return redirect(url_for('predict'))
    
    return render_template('predict_intern.html')

# Generate PDF Report route
@app.route('/generate-report', methods=['POST'])
def generate_report():
    try:
        # Get form data
        prediction = int(request.form.get('prediction'))
        probability = float(request.form.get('probability'))
        probability_pct = round(probability * 100)
        
        # Collect form data
        form_data = {}
        for key in request.form:
            if key not in ['prediction', 'probability']:
                form_data[key] = request.form.get(key)
        
        # Generate a unique report ID
        report_id = str(uuid.uuid4())[:8]
        report_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Render the report template
        rendered_html = render_template('report_intern.html', 
                                        prediction=prediction,
                                        probability_pct=probability_pct,
                                        form_data=form_data,
                                        report_id=report_id,
                                        report_date=report_date)
        
        # Generate PDF using ReportLab
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        title_style = styles['Heading1']
        title = Paragraph("Lead Conversion Prediction Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Date and ID
        date_style = styles['Normal']
        date_text = Paragraph(f"Report Generated: {report_date} | ID: {report_id}", date_style)
        elements.append(date_text)
        elements.append(Spacer(1, 20))
        
        # Prediction Result
        result_style = ParagraphStyle(
            'ResultStyle',
            parent=styles['Heading2'],
            backColor=colors.lightgreen if prediction == 1 else colors.lightgrey,
            borderPadding=10
        )
        
        if prediction == 1:
            result_text = Paragraph(f"✅ This lead is likely to convert ({probability_pct}% probability)", result_style)
        else:
            result_text = Paragraph(f"❌ This lead is not likely to convert ({probability_pct}% probability)", result_style)
        
        elements.append(result_text)
        elements.append(Spacer(1, 20))
        
        # Lead Information Table
        lead_info_heading = Paragraph("Lead Information", styles['Heading2'])
        elements.append(lead_info_heading)
        elements.append(Spacer(1, 10))
        
        # Create table data
        table_data = [['Field', 'Value']]
        for key, value in form_data.items():
            # Convert key from snake_case to Title Case for display
            display_key = ' '.join(word.capitalize() for word in key.split('_'))
            table_data.append([display_key, str(value)])
        
        # Create the table
        table = Table(table_data, colWidths=[200, 300])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Recommendations
        recommendations_heading = Paragraph("Recommended Actions", styles['Heading2'])
        elements.append(recommendations_heading)
        elements.append(Spacer(1, 10))
        
        if prediction == 1:
            recommendations = [
                "Prioritize follow-up: This lead should receive immediate attention from the sales team.",
                "Schedule a personalized demo: Prepare a tailored demonstration focusing on the lead's specific needs.",
                "Prepare a custom pricing proposal: Create a customized offer that highlights value propositions.",
                "Offer premium content: Share high-value content that addresses the lead's specific interests."
            ]
        else:
            recommendations = [
                "Nurture with targeted emails: Implement a strategic email nurturing sequence.",
                "Educational content: Share resources that address common pain points.",
                "Special promotions: Consider time-limited offers to incentivize engagement.",
                "Re-engagement strategy: Try new messaging or value propositions."
            ]
        
        for recommendation in recommendations:
            p = Paragraph(f"• {recommendation}", styles['Normal'])
            elements.append(p)
            elements.append(Spacer(1, 5))
        
        # Build the PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Create a response with the PDF
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=lead_prediction_{report_id}.pdf'
        
        return response
        
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'danger')
        return redirect(url_for('predict'))

# Custom error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('base_intern.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('base_intern.html', error="Internal server error"), 500

if __name__ == '__main__':
    # Create initial files if they don't exist
    create_initial_files()
    
if __name__ == '__main__':
    # Create initial files if they don't exist
    create_initial_files()
    
    # Run the app on all network interfaces
    app.run(debug=True, host='0.0.0.0', port=5000)
    
    # Run instructions:
    # python app_intern.py
 
