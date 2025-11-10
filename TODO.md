# TODO List for Live Graph Implementation

## 1. Update views.py
- [x] Remove matplotlib image generation code
- [x] Collect historical dates, prices, and predictions into lists
- [x] Pass data as JSON to template instead of base64 image
- [x] Add new view `get_live_price` for AJAX calls to fetch current price

## 2. Update URLs
- [x] Add URL pattern for `get_live_price` view

## 3. Update predict.html
- [x] Add Chart.js CDN link
- [x] Replace static image with canvas element
- [x] Add JavaScript to initialize Chart.js chart with historical data
- [x] Add AJAX function to fetch live price every minute and update chart
- [x] Handle prediction data overlay on chart

## 4. Testing
- [x] Run the app and test live graph updates
- [x] Verify chart renders correctly with historical and predicted data
- [x] Check AJAX calls work and update the chart without page reload
