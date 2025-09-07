# Yahoo Finance MCP Server Setup Guide

## 🎯 **Goal:** 
Set up direct connection to Yahoo Finance for accurate, real-time stock data (including Chinese stocks like 600298.SS)

## 📦 **Available Yahoo Finance MCP Servers:**

### **Option 1: yfinance-mcp-server (Recommended)**
- **Features:** Price history, financial statements, analyst data, real-time quotes
- **Supports:** Global stocks including Chinese markets (600298.SS)
- **Installation:** `pip install yfinance-mcp-server`

### **Option 2: mcp-yfinance-server**
- **Features:** Real-time data, watchlists, technical indicators, full analysis
- **Supports:** Comprehensive stock analysis tools
- **Installation:** `pip install mcp-yfinance-server`

### **Option 3: yahoo-finance-mcp**
- **Features:** Historical prices, company info, financial statements, options, news
- **Supports:** Complete Yahoo Finance API access
- **Installation:** `pip install yahoo-finance-mcp`

## 🛠️ **Step-by-Step Setup:**

### **Step 1: Install the MCP Server**

Choose one of the servers above. For this guide, we'll use `yfinance-mcp-server`:

```bash
# Using pip (in virtual environment)
cd unified-python
source venv/bin/activate
pip install yfinance-mcp-server

# Or install from source for latest version
git clone https://github.com/itsmejay80/yfinance-mcp-server.git
cd yfinance-mcp-server
pip install -r requirements.txt
```

### **Step 2: Configure MCP Client**

Add Yahoo Finance server to your MCP configuration:

**For Claude Desktop (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "yfinance": {
      "command": "uvx",
      "args": ["yfinance-mcp-server"]
    }
  }
}
```

**For Custom MCP Client:**
```json
{
  "servers": {
    "yahoo_finance": {
      "command": "python",
      "args": ["-m", "yfinance_mcp_server"],
      "env": {}
    }
  }
}
```

### **Step 3: Start the Server**

```bash
# Start the Yahoo Finance MCP server
yfinance-mcp-server

# Or if installed from source
python -m yfinance_mcp_server
```

### **Step 4: Test Connection**

Test with both US and Chinese stocks:

```python
# Test with AAPL (US stock)
response = mcp_client.call("yfinance", "get_ticker_info", {"symbol": "AAPL"})

# Test with Angel Yeast (Chinese stock)
response = mcp_client.call("yfinance", "get_ticker_info", {"symbol": "600298.SS"})
```

## 🔧 **Integration with Our Article System:**

### **Update Article Creator**

Add Yahoo Finance MCP integration to our article creator:

```python
# In article_creator.py
class EnhancedArticleCreator:
    def __init__(self):
        self.table_processor = DarkTableProcessor()
        self.yahoo_finance_mcp = YahooFinanceMCPClient()  # New addition
    
    def get_real_time_stock_data(self, ticker):
        """Get accurate stock data from Yahoo Finance MCP"""
        try:
            data = self.yahoo_finance_mcp.get_ticker_info(ticker)
            return {
                'current_price': data.get('currentPrice'),
                'market_cap': data.get('marketCap'),
                'pe_ratio': data.get('trailingPE'),
                'beta': data.get('beta'),
                'dividend_yield': data.get('dividendYield'),
                '52_week_high': data.get('fiftyTwoWeekHigh'),
                '52_week_low': data.get('fiftyTwoWeekLow'),
                'volume': data.get('volume')
            }
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None
```

### **Usage Example**

```python
# Create article with real-time data
creator = EnhancedArticleCreator()

# Get current Angel Yeast data
angel_data = creator.get_real_time_stock_data("600298.SS")
if angel_data:
    print(f"Current Price: CNY {angel_data['current_price']}")
    print(f"Market Cap: CNY {angel_data['market_cap']:,}")
    print(f"PE Ratio: {angel_data['pe_ratio']}")

# Use this data in article creation
article_data = creator.create_stock_analysis_article(
    ticker="600298.SS",
    real_time_data=angel_data
)
```

## 🚀 **Expected Benefits:**

### **Accurate Data Access:**
- ✅ **Real-time prices** for both US and Chinese stocks
- ✅ **Consistent data source** (Yahoo Finance)
- ✅ **No more stale/cached data** issues
- ✅ **Automatic updates** when creating articles

### **Enhanced Analysis:**
- ✅ **Current valuation metrics** always up-to-date
- ✅ **Accurate buy/sell thresholds** based on real prices
- ✅ **Reliable investment recommendations**
- ✅ **Professional-grade data quality**

## 📋 **Next Steps:**

1. **Choose MCP server** (recommend yfinance-mcp-server)
2. **Install in virtual environment**
3. **Configure MCP client** with server details
4. **Test connection** with both AAPL and 600298.SS
5. **Integrate with article creator** for automatic data updates

**Would you like me to help you install and configure one of these Yahoo Finance MCP servers?** This would give us direct, reliable access to accurate stock data for both US and Chinese stocks.
