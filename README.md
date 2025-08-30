# 📊 SqueezeMetrics Financial Dashboard

A professional financial dashboard for systematic trading with P_NN neural network predictions across 5,400+ securities.

## 🚀 **Live Demo**
**Production Dashboard**: [https://squeezemetrics-dashboard.onrender.com](https://squeezemetrics-dashboard.onrender.com)

## 🎯 **Key Features**

### 💼 **Portfolio Builder**
- **20 Long + 40 Short** systematic position selection
- **$10M volume filter** for conservative liquidity
- **Balance constraints**: Max 4 positions per sector, 2 per industry  
- **Equal-weight sizing** with signal-threshold rebalancing

### 📈 **P_NN Neural Network Analytics**
- **21-day forward alpha predictor** using nearest-neighbor analysis
- **Real-time signals** for long/short position entry/exit
- **SqueezeMetrics indicators**: P, V, G, D, IV scores

### 🔄 **Advanced Trading Tools**
- **Pair Trade Generator**: 530+ pairs within same industries
- **Sector Rankings**: Relative strength analysis
- **Risk Management**: Diversification and liquidity controls
- **Case-insensitive filtering** across all data

## 🛠 **Quick Start**

### **Local Development**
```bash
# Install dependencies
pip install -r requirements.txt

# Fetch latest data
python fetch_squeeze_data.py

# Run full dashboard (all features)
python final_dashboard.py
# Access: http://127.0.0.1:8055/

# Or run production version (simplified)
python app.py  
# Access: http://127.0.0.1:10000/
```

### **Deploy to Render**
1. Fork/clone this repository
2. Sign up at [render.com](https://render.com) 
3. Connect GitHub repository
4. Render auto-detects `render.yaml` configuration
5. Deploy automatically!

## 📁 **Project Structure**

```
Squeeze/
├── app.py                      # 🚀 Production dashboard (Render)
├── final_dashboard.py          # 💻 Full-featured local dashboard  
├── fetch_squeeze_data.py       # 📡 API data fetching
├── render.yaml                 # ⚙️  Render deployment config
├── requirements.txt            # 📦 Python dependencies
├── DASHBOARD_DOCUMENTATION.md  # 📚 Complete user guide (4K+ words)
├── PROJECT_SUMMARY.md          # 📋 Development summary
├── README_DEPLOYMENT.md        # 🚀 Deployment instructions
└── squeeze_data_*.xlsx         # 💾 Historical data (Git ignored)
```

## 🔧 **Technical Specs**

- **Framework**: Plotly Dash + Bootstrap
- **Data Source**: SqueezeMetrics API
- **Securities**: 5,400+ stocks, ETFs, and derivatives
- **Indicators**: 23 columns including P_NN neural predictions
- **Deployment**: Render.com (auto-scaling, HTTPS)

## 💡 **Dashboard Tabs**

### **Local Version (final_dashboard.py)**
1. **📊 Overview** - Data table with advanced filtering
2. **🏆 Rankings** - Sector performance rankings  
3. **🔄 Pair Trades** - 530+ algorithmic pair suggestions
4. **📈 Analysis** - Interactive charts and correlations
5. **🏢 Sectors** - Industry breakdown and heatmaps
6. **💼 Portfolio** - Systematic 20L/40S construction
7. **📋 Export** - Data export functionality

### **Production Version (app.py)**
1. **📊 Overview** - Core data and filtering
2. **💼 Portfolio** - Live portfolio construction  
3. **📈 Analysis** - Key charts and insights

## 📊 **Portfolio Algorithm**

```python
# Universe: $10M+ volume, no ETFs
portfolio_universe = df[
    (df['VOLUME'] >= 10_000_000) & 
    (df['INDUSTRY'] != 'ETF')
]

# Selection: Top 50 longs, Bottom 50 shorts
long_candidates = universe.sort_values('P_NN', ascending=False).head(50)
short_candidates = universe.sort_values('P_NN', ascending=False).tail(50)

# Apply constraints: Max 4/sector, 2/industry
# Equal weight within buckets: 50% long / 50% short
```

## 🔄 **Data Updates**

The production dashboard fetches **live data** from SqueezeMetrics API. For local development:

```bash
python fetch_squeeze_data.py  # Downloads latest data
```

## 🚨 **Performance Notes**

- **Production**: Auto-scales, HTTPS, mobile-responsive
- **Free tier**: 750 hours/month on Render
- **Cold starts**: ~30 seconds (Render wakes up service)
- **Local**: Full feature set, faster response times

## 🎉 **Business Value**

- **Systematic Trading**: Removes emotional bias from position selection
- **Risk Management**: Balanced portfolios with liquidity constraints  
- **Real-time Signals**: P_NN neural network predictions
- **Professional Grade**: Production-ready deployment

## 📞 **Support**

- **Documentation**: See `DASHBOARD_DOCUMENTATION.md` for complete user guide
- **Deployment**: See `README_DEPLOYMENT.md` for hosting setup
- **Summary**: See `PROJECT_SUMMARY.md` for development overview

---
*Built for systematic trading excellence* 🎯