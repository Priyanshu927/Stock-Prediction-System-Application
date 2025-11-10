from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing
import os
import matplotlib.pyplot as plt
import io
import base64
import qrcode
from PIL import Image
import yfinance as yf
import json
import re
from .models import UserProfile
def index(request):
    return render(request, 'predictor/index.html')
@login_required
def predict(request):
    error = None
    prediction_data = None
    stock_col = request.GET.get('ticker')  # Type e.g. AAPL, GOOGL, etc.
    days = request.GET.get('days')
    if stock_col and days:
        try:
            # Load data from CSV dataset
            csv_path = os.path.join(os.path.dirname(__file__), 'datasets', 'stock_data.csv')
            df = pd.read_csv(csv_path, skiprows=1, names=['Date', 'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'])
            if stock_col not in df.columns:
                error = f"No data found for ticker: {stock_col}. Please check the ticker symbol."
            else:
                # Filter data for the selected ticker
                df_ticker = df[['Date', stock_col]].copy()
                df_ticker['Date'] = pd.to_datetime(df_ticker['Date'])
                df_ticker = df_ticker.sort_values('Date')
                df_ticker = df_ticker.dropna()  # Remove any NaN values
                if df_ticker.empty:
                    error = f"No valid data found for ticker: {stock_col}."
                else:
                    price_col = stock_col  # The column name is the ticker
                    df_ml = df_ticker[[price_col]].copy()
                    forecast_out = int(days)
                    df_ml['Prediction'] = df_ml[price_col].shift(-forecast_out)
                    df_ml = df_ml.dropna()
                    if len(df_ml) < forecast_out:
                        error = f"Not enough data for prediction. Need at least {forecast_out} data points."
                    else:
                        X = np.array(df_ml.drop(['Prediction'], axis=1))
                        y = np.array(df_ml['Prediction'])
                        X = preprocessing.scale(X)
                        model = LinearRegression()
                        model.fit(X, y)
                        last_data = np.array(df_ticker[[price_col]].tail(int(days)))
                        last_data = preprocessing.scale(last_data)
                        prediction = model.predict(last_data)
                        # Prepare data for live graph (future predictions only)
                        predicted_dates = pd.date_range(start=pd.Timestamp.today(), periods=int(days)+1, freq='D')[1:].strftime('%Y-%m-%d').tolist()
                        predicted_prices = prediction.round(2).tolist()
                        # Extend predictions for longer periods if needed (up to 2 years)
                        if int(days) > 365:
                            extended_days = int(days) - 365  # Additional days beyond 1 year
                            predicted_dates += pd.date_range(start=pd.Timestamp.today() + pd.Timedelta(days=365), periods=extended_days, freq='D').strftime('%Y-%m-%d').tolist()
                            extended_prices = [prediction[-1]] * extended_days  # Constant price for extension
                            predicted_prices += extended_prices

                        # Generate QR code with URL to the prediction page (using network IP for mobile access)
                        import socket
                        hostname = socket.gethostname()
                        local_ip = socket.gethostbyname(hostname)
                        qr_data = f"http://{local_ip}:8001/predict/?ticker={stock_col}&days={days}"
                        qr = qrcode.QRCode(version=None, box_size=10, border=5, error_correction=qrcode.constants.ERROR_CORRECT_L)
                        qr.add_data(qr_data)
                        qr.make(fit=True)
                        qr_img = qr.make_image(fill='black', back_color='white')
                        qr_buf = io.BytesIO()
                        qr_img.save(qr_buf, format='PNG')
                        qr_buf.seek(0)
                        qr_base64 = base64.b64encode(qr_buf.read()).decode('utf-8')
                        qr_buf.close()

                        prediction_data = {
                            'ticker': stock_col,
                            'days': days,
                            'current_price': round(df_ticker[price_col].iloc[-1], 2),
                            'predicted_price': round(prediction[-1], 2),
                            'predicted_dates': predicted_dates,
                            'predicted_prices': predicted_prices,
                            'qr_code': qr_base64
                        }
        except Exception as e:
            error = str(e)
    return render(request, 'predictor/predict.html', {'error': error, 'prediction': prediction_data})

@login_required
def get_live_price(request):
    ticker = request.GET.get('ticker')
    if ticker:
        try:
            # Load data from CSV dataset
            csv_path = os.path.join(os.path.dirname(__file__), 'datasets', 'stock_data.csv')
            df = pd.read_csv(csv_path, skiprows=1, names=['Date', 'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'])
            if ticker in df.columns:
                # Get the latest price from the dataset
                latest_price = df[ticker].dropna().iloc[-1]
                return JsonResponse({'price': round(latest_price, 2)})
            else:
                return JsonResponse({'error': 'Ticker not found in dataset'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Ticker not provided'}, status=400)

@login_required
def ticker_info(request):
    ticker_symbol = request.GET.get('ticker')
    if ticker_symbol:
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            return render(request, 'predictor/ticker.html', {'ticker': ticker_symbol, 'info': info})
        except Exception as e:
            return render(request, 'predictor/ticker.html', {'error': str(e)})
    return render(request, 'predictor/ticker.html')

def send_otp(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        mobile = data.get('mobile')
        pan = data.get('pan')
        # For demo purposes, always return success and print OTP to console
        # In production, integrate with SMS service
        print(f"OTP for mobile {mobile} and PAN {pan}: 123456")
        return JsonResponse({'success': True, 'message': 'OTP sent successfully'})

def verify_otp(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        mobile = data.get('mobile')
        otp = data.get('otp')
        print(f"Verifying OTP for mobile {mobile}: received '{otp}'")
        # For demo purposes, accept OTP 123456
        if otp == '123456':
            return JsonResponse({'success': True, 'message': 'OTP verified successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid OTP'})

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        pan_card = request.POST.get('pan_card')
        full_name = request.POST.get('full_name')
        dob = request.POST.get('date_of_birth')
        mobile = request.POST.get('mobile_number')
        address = request.POST.get('address')
        pan_image = request.FILES.get('pan_card_image')
        mobile_verified = request.POST.get('mobile_verified')

        # Validate PAN card format (Indian PAN card: 5 letters, 4 digits, 1 letter)
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan_card.upper()):
            messages.error(request, 'Invalid PAN card format. Please enter a valid PAN card number.')
            return render(request, 'predictor/register.html')

        # Check if PAN card already exists
        if UserProfile.objects.filter(pan_card_number=pan_card.upper()).exists():
            messages.error(request, 'This PAN card is already registered.')
            return render(request, 'predictor/register.html')

        # Validate mobile verification
        if mobile_verified != 'true':
            messages.error(request, 'Please verify your mobile number before registering.')
            return render(request, 'predictor/register.html')

        # Validate passwords
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'predictor/register.html')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'predictor/register.html')

        # Create user
        user = User.objects.create_user(username=username, password=password1)
        user.save()

        # Create user profile
        profile = UserProfile.objects.create(
            user=user,
            pan_card_number=pan_card.upper(),
            full_name=full_name,
            date_of_birth=dob,
            address=address,
            pan_card_image=pan_image
        )
        # For now, auto-verify PAN card (in production, this would require manual verification)
        profile.pan_card_verified = True
        profile.save()

        login(request, user)
        messages.success(request, 'Account created successfully! Your PAN card has been verified.')
        return redirect('index')
    return render(request, 'predictor/register.html')
