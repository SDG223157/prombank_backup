#!/usr/bin/env python3
"""
Yahoo Finance Integration for Real-Time Stock Data
Provides accurate, real-time stock data for article creation
"""

import yfinance as yf
from typing import Dict, Any, Optional
from datetime import datetime

class YahooFinanceIntegration:
    """Integration with Yahoo Finance for real-time stock data"""
    
    def __init__(self):
        self.exchange_rate_cny_usd = 0.1395  # Approximate CNY to USD rate
    
    def get_stock_data(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive stock data from Yahoo Finance"""
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get current price (try multiple fields)
            current_price = (
                info.get('currentPrice') or 
                info.get('regularMarketPrice') or 
                info.get('previousClose')
            )
            
            # Determine currency
            currency = 'USD'
            if ticker.endswith('.SS') or ticker.endswith('.SZ'):
                currency = 'CNY'
            elif ticker.endswith('.L'):
                currency = 'GBP'
            elif ticker.endswith('.TO'):
                currency = 'CAD'
            
            data = {
                'ticker': ticker,
                'company_name': info.get('longName', info.get('shortName', 'Unknown')),
                'current_price': current_price,
                'currency': currency,
                'previous_close': info.get('previousClose'),
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'pe_ratio_ttm': info.get('trailingPE'),
                'pe_ratio_forward': info.get('forwardPE'),
                'beta': info.get('beta'),
                'dividend_yield': info.get('dividendYield'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                'volume': info.get('volume'),
                'avg_volume': info.get('averageVolume'),
                'shares_outstanding': info.get('sharesOutstanding'),
                'float_shares': info.get('floatShares'),
                'ev_ebitda': info.get('enterpriseToEbitda'),
                'ev_revenue': info.get('enterpriseToRevenue'),
                'price_book': info.get('priceToBook'),
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'debt_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'gross_margin': info.get('grossMargins'),
                'operating_margin': info.get('operatingMargins'),
                'net_margin': info.get('profitMargins'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'timestamp': datetime.now().isoformat(),
                'data_source': 'Yahoo Finance via yfinance'
            }
            
            # Add USD equivalent for non-USD stocks
            if currency == 'CNY' and current_price:
                data['current_price_usd'] = current_price * self.exchange_rate_cny_usd
                if data['market_cap']:
                    data['market_cap_usd'] = data['market_cap'] * self.exchange_rate_cny_usd
            
            return data
            
        except Exception as e:
            return {
                'ticker': ticker,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'data_source': 'Yahoo Finance via yfinance (FAILED)'
            }
    
    def get_multiple_stocks(self, tickers: list) -> Dict[str, Dict[str, Any]]:
        """Get data for multiple stocks"""
        results = {}
        for ticker in tickers:
            results[ticker] = self.get_stock_data(ticker)
        return results
    
    def format_currency(self, value: float, currency: str) -> str:
        """Format currency values appropriately"""
        if not value:
            return "N/A"
        
        if currency == 'USD':
            if value >= 1e12:
                return f"${value/1e12:.2f}T"
            elif value >= 1e9:
                return f"${value/1e9:.2f}B"
            elif value >= 1e6:
                return f"${value/1e6:.2f}M"
            else:
                return f"${value:,.2f}"
        
        elif currency == 'CNY':
            if value >= 1e12:
                return f"CNY {value/1e12:.2f}T"
            elif value >= 1e9:
                return f"CNY {value/1e9:.2f}B"
            elif value >= 1e6:
                return f"CNY {value/1e6:.2f}M"
            else:
                return f"CNY {value:,.2f}"
        
        return f"{value:,.2f} {currency}"
    
    def validate_data_freshness(self, data: Dict[str, Any], max_age_hours: int = 24) -> bool:
        """Validate if data is fresh enough"""
        if 'timestamp' not in data:
            return False
        
        try:
            data_time = datetime.fromisoformat(data['timestamp'])
            age_hours = (datetime.now() - data_time).total_seconds() / 3600
            return age_hours <= max_age_hours
        except:
            return False

# Test the integration
if __name__ == '__main__':
    yf_integration = YahooFinanceIntegration()
    
    # Test both stocks
    test_tickers = ['AAPL', '600298.SS']
    results = yf_integration.get_multiple_stocks(test_tickers)
    
    print('Yahoo Finance Integration Test:')
    print('=' * 50)
    
    for ticker, data in results.items():
        print(f'\n{ticker}:')
        if 'error' in data:
            print(f'  Error: {data["error"]}')
        else:
            print(f'  Company: {data.get("company_name", "N/A")}')
            print(f'  Current Price: {yf_integration.format_currency(data.get("current_price"), data.get("currency"))}')
            print(f'  Market Cap: {yf_integration.format_currency(data.get("market_cap"), data.get("currency"))}')
            print(f'  PE Ratio: {data.get("pe_ratio_ttm", "N/A")}')
            print(f'  Data Fresh: {yf_integration.validate_data_freshness(data)}')
