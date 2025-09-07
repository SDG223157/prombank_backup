#!/usr/bin/env python3
"""
Enhanced Stock Article Creator with Real-Time Data Integration
Automatically uses today's date and Yahoo Finance real-time data
"""

import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from yahoo_finance_integration import YahooFinanceIntegration
from article_creator import EnhancedArticleCreator

class EnhancedStockArticleCreator(EnhancedArticleCreator):
    """Enhanced article creator with Yahoo Finance integration and automatic date handling"""
    
    def __init__(self):
        super().__init__()
        self.yahoo_finance = YahooFinanceIntegration()
    
    def create_stock_analysis_article(self, 
                                    ticker: str,
                                    title: Optional[str] = None,
                                    category: str = "Investment Analysis",
                                    use_real_time_data: bool = True,
                                    analysis_framework: str = "unified") -> Dict[str, Any]:
        """
        Create a comprehensive stock analysis article with real-time data
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', '600298.SS')
            title: Article title (auto-generated if None)
            category: Article category
            use_real_time_data: Whether to fetch real-time Yahoo Finance data
            analysis_framework: Framework to use ('unified', 'damodaran', 'wealth')
            
        Returns:
            Dictionary with article data ready for MCP creation
        """
        
        # Get real-time stock data
        if use_real_time_data:
            stock_data = self.yahoo_finance.get_stock_data(ticker)
            if 'error' in stock_data:
                raise ValueError(f"Failed to get stock data for {ticker}: {stock_data['error']}")
        else:
            stock_data = None
        
        # Generate title if not provided
        if not title:
            company_name = stock_data.get('company_name', ticker) if stock_data else ticker
            title = f"{company_name} ({ticker}) - Unified Professional Stock Analysis"
        
        # Generate article content based on framework
        content = self._generate_stock_analysis_content(ticker, stock_data, analysis_framework)
        
        # Auto-detect tags for stock analysis
        tags = self._generate_stock_analysis_tags(ticker, stock_data)
        
        # Create article data
        article_data = {
            'title': title,
            'content': content,
            'category': category,
            'tags': tags,
            'ticker': ticker,
            'real_time_data': stock_data is not None,
            'analysis_framework': analysis_framework,
            'analysis_date': self.yahoo_finance.get_current_analysis_date(),
            'next_review_date': self.yahoo_finance.get_next_review_date(),
            'copy_friendly': True,
            'auto_processed': True
        }
        
        return article_data
    
    def _generate_stock_analysis_content(self, ticker: str, stock_data: Dict[str, Any], framework: str) -> str:
        """Generate stock analysis content based on framework"""
        
        if not stock_data:
            return self._generate_template_content(ticker, framework)
        
        # Extract key data
        company_name = stock_data.get('company_name', ticker)
        current_price = stock_data.get('current_price', 0)
        currency = stock_data.get('currency', 'USD')
        market_cap = stock_data.get('market_cap', 0)
        
        # Format prices
        if currency == 'CNY':
            price_str = f"CNY {current_price:,.2f}"
            price_usd_str = f"USD {stock_data.get('current_price_usd', 0):.2f}"
            market_cap_str = self.yahoo_finance.format_currency(market_cap, 'CNY')
            market_cap_usd_str = self.yahoo_finance.format_currency(stock_data.get('market_cap_usd', 0), 'USD')
        else:
            price_str = f"USD {current_price:,.2f}"
            price_usd_str = price_str
            market_cap_str = self.yahoo_finance.format_currency(market_cap, 'USD')
            market_cap_usd_str = market_cap_str
        
        # Generate content based on framework
        content = f"""# {company_name} ({ticker}) - Unified Professional Stock Analysis

*A comprehensive institutional-grade analysis using the Unified Professional Stock Analysis Framework*

---

## Phase I: Company Foundation & Market Context

### 1. Company Profile & Business Understanding

**Basic Information:**
- **Company:** {ticker} - {company_name}
- **Analysis Date:** {self.yahoo_finance.get_current_analysis_date()}
- **Analyst:** Investment Research Team
- **Current Price:** {price_str} (approx. {price_usd_str})
- **Market Cap:** {market_cap_str} (approx. {market_cap_usd_str})

**Business Model Analysis:**
- **Core Business:** [To be completed based on company research]
- **Industry Classification:** [To be determined]
- **Competitive Advantages:** [To be analyzed]
- **Life Cycle Stage:** [ ] Young Growth [ ] Growth [ ] Mature [ ] Declining
- **Geographic Footprint:** [To be researched]
- **Management Team:** [To be analyzed]

---

## Phase II: Financial Performance & Valuation Metrics

### 3. Current Financial Profile

**Market Metrics:**

| Metric | Value ({currency}) | Value (USD) | Analysis |
|--------|-------------|-------------|----------|
| Current Price | {price_str} | {price_usd_str} | Real-time Yahoo Finance data |
| 52-Week Range | {currency} {stock_data.get('52_week_low', 'N/A')} - {stock_data.get('52_week_high', 'N/A')} | [USD equivalent] | [Analysis needed] |
| Market Cap | {market_cap_str} | {market_cap_usd_str} | [Classification] |
| Beta (5-Year) | {stock_data.get('beta', 'N/A')} | {stock_data.get('beta', 'N/A')} | [Volatility assessment] |
| PE Ratio (TTM) | {stock_data.get('pe_ratio_ttm', 'N/A')} | {stock_data.get('pe_ratio_ttm', 'N/A')} | [Valuation assessment] |
| Dividend Yield | {stock_data.get('dividend_yield', 'N/A')} | {stock_data.get('dividend_yield', 'N/A')} | [Income assessment] |

**Real-Time Data Source:** {stock_data.get('data_source', 'Yahoo Finance')}
**Data Timestamp:** {stock_data.get('timestamp', 'N/A')}

---

## Investment Framework Analysis

**Next Review Date:** {self.yahoo_finance.get_next_review_date()}

*This analysis uses real-time data from Yahoo Finance to ensure accuracy and timeliness. All financial metrics are current as of the analysis date above.*

**Disclaimer:** This analysis is for educational and research purposes. All investment decisions should consider individual circumstances, risk tolerance, and professional advice. Past performance does not guarantee future results.
"""
        
        return content
    
    def _generate_template_content(self, ticker: str, framework: str) -> str:
        """Generate template content when real-time data is not available"""
        
        return f"""# {ticker} - Stock Analysis Template

**Analysis Date:** {self.yahoo_finance.get_current_analysis_date()}
**Next Review Date:** {self.yahoo_finance.get_next_review_date()}

*Template for {framework} analysis framework - please update with current data*

**Note:** Real-time data not available. Please update with current financial information.
"""
    
    def _generate_stock_analysis_tags(self, ticker: str, stock_data: Dict[str, Any]) -> List[str]:
        """Generate relevant tags for stock analysis"""
        
        tags = ["Stock Analysis", "Investment Research", "Financial Analysis"]
        
        # Add ticker-specific tags
        if ticker:
            tags.append(ticker)
            
            # Add exchange-specific tags
            if ticker.endswith('.SS'):
                tags.extend(["Chinese Stocks", "A-Shares", "Shanghai Stock Exchange"])
            elif ticker.endswith('.SZ'):
                tags.extend(["Chinese Stocks", "A-Shares", "Shenzhen Stock Exchange"])
            elif not '.' in ticker:  # US stocks
                tags.extend(["US Stocks", "NYSE", "NASDAQ"])
        
        # Add company name if available
        if stock_data and stock_data.get('company_name'):
            company_name = stock_data['company_name']
            tags.append(company_name)
            
            # Add industry-specific tags based on company name
            if 'yeast' in company_name.lower():
                tags.extend(["Biotechnology", "Food Industry", "Consumer Staples"])
            elif 'moutai' in company_name.lower():
                tags.extend(["Premium Brands", "Baijiu", "Luxury Goods", "Cultural Moat"])
            elif 'apple' in company_name.lower():
                tags.extend(["Technology", "Consumer Electronics", "FAANG"])
            elif 'microsoft' in company_name.lower():
                tags.extend(["Technology", "Cloud Computing", "Software"])
        
        # Add framework tags
        tags.extend([
            "Unified Analysis Framework",
            "Damodaran DCF", 
            "WEALTH Ratio",
            "Monte Carlo Simulation",
            "Quality Assessment",
            "Real-Time Data"
        ])
        
        return tags[:20]  # Limit to 20 tags
    
    def create_multiple_stock_analyses(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """Create multiple stock analysis articles"""
        
        articles = []
        
        for ticker in tickers:
            try:
                article_data = self.create_stock_analysis_article(ticker)
                articles.append(article_data)
                print(f"✅ Created analysis for {ticker}")
            except Exception as e:
                print(f"❌ Failed to create analysis for {ticker}: {e}")
        
        return articles

# Convenience functions
def create_stock_analysis(ticker: str, **kwargs) -> Dict[str, Any]:
    """Convenience function to create stock analysis with real-time data"""
    creator = EnhancedStockArticleCreator()
    return creator.create_stock_analysis_article(ticker, **kwargs)

def get_current_analysis_date() -> str:
    """Get current analysis date"""
    return datetime.now().strftime("%B %d, %Y")

def get_next_review_date(months_ahead: int = 6) -> str:
    """Get next review date"""
    try:
        from dateutil.relativedelta import relativedelta
        next_date = datetime.now() + relativedelta(months=months_ahead)
        return next_date.strftime("%B %d, %Y")
    except ImportError:
        import calendar
        today = datetime.now()
        year = today.year
        month = today.month + months_ahead
        
        while month > 12:
            month -= 12
            year += 1
        
        day = min(today.day, calendar.monthrange(year, month)[1])
        next_date = datetime(year, month, day)
        return next_date.strftime("%B %d, %Y")

# Example usage
if __name__ == "__main__":
    creator = EnhancedStockArticleCreator()
    
    # Test with a stock ticker
    test_ticker = "600519.SS"  # Kweichow Moutai
    
    try:
        print(f"Creating analysis for {test_ticker}...")
        article_data = creator.create_stock_analysis_article(test_ticker)
        
        print("Article Creation Summary:")
        print("=" * 50)
        print(f"Title: {article_data['title']}")
        print(f"Analysis Date: {article_data['analysis_date']}")
        print(f"Next Review: {article_data['next_review_date']}")
        print(f"Real-Time Data: {article_data['real_time_data']}")
        print(f"Tags: {len(article_data['tags'])} tags")
        print(f"Content Length: {len(article_data['content'])} characters")
        
    except Exception as e:
        print(f"Error: {e}")
