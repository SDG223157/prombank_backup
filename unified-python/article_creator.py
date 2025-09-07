#!/usr/bin/env python3
"""
Enhanced Article Creator with Automatic Table Styling
Integrates with MCP prombank backup to create articles with professional dark tables
"""

import os
import re
from typing import List, Dict, Any, Optional
from table_processor import DarkTableProcessor, process_file_to_article

class EnhancedArticleCreator:
    """Enhanced article creator with automatic table styling support"""
    
    def __init__(self):
        self.table_processor = DarkTableProcessor()
        
    def create_article_from_markdown_file(self, 
                                        file_path: str,
                                        title: Optional[str] = None,
                                        category: Optional[str] = None,
                                        tags: Optional[List[str]] = None,
                                        auto_detect_category: bool = True,
                                        auto_detect_tags: bool = True) -> Dict[str, Any]:
        """
        Create an article from a markdown file with automatic table styling
        
        Args:
            file_path: Path to the markdown file
            title: Article title (auto-detected if None)
            category: Article category (auto-detected if None and auto_detect_category=True)
            tags: Article tags (auto-detected if None and auto_detect_tags=True)
            auto_detect_category: Whether to auto-detect category from content
            auto_detect_tags: Whether to auto-detect tags from content
            
        Returns:
            Dictionary with article data ready for MCP creation
        """
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Markdown file not found: {file_path}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Auto-detect title if not provided
        if not title:
            title = self._extract_title_from_content(content)
        
        # Auto-detect category if not provided
        if not category and auto_detect_category:
            category = self._detect_category_from_content(content, file_path)
        
        # Auto-detect tags if not provided
        if not tags and auto_detect_tags:
            tags = self._detect_tags_from_content(content, title or "")
        
        # Process content with table styling
        article_data = self.table_processor.create_article_with_styled_tables(
            title=title,
            markdown_content=content,
            category=category,
            tags=tags
        )
        
        # Add metadata
        article_data['source_file'] = file_path
        article_data['auto_processed'] = True
        
        return article_data
    
    def create_article_from_content(self,
                                   content: str,
                                   title: str,
                                   category: Optional[str] = None,
                                   tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create an article from markdown content string with automatic table styling
        
        Args:
            content: Markdown content
            title: Article title
            category: Article category
            tags: Article tags
            
        Returns:
            Dictionary with article data ready for MCP creation
        """
        
        # Process content with table styling
        article_data = self.table_processor.create_article_with_styled_tables(
            title=title,
            markdown_content=content,
            category=category,
            tags=tags
        )
        
        article_data['auto_processed'] = True
        
        return article_data
    
    def _extract_title_from_content(self, content: str) -> str:
        """Extract title from markdown content"""
        # Look for first H1 heading
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()
        
        # Look for title in front matter
        frontmatter_match = re.search(r'^---\n.*?title:\s*(.+)\n.*?---', content, re.DOTALL)
        if frontmatter_match:
            return frontmatter_match.group(1).strip().strip('"\'')
        
        return "Untitled Article"
    
    def _detect_category_from_content(self, content: str, file_path: str = "") -> Optional[str]:
        """Auto-detect category based on content and file path"""
        content_lower = content.lower()
        file_lower = file_path.lower()
        
        # Finance/Investment keywords
        finance_keywords = [
            'investment', 'stock', 'trading', 'portfolio', 'financial', 'market',
            'valuation', 'earnings', 'dividend', 'pe ratio', 'peg', 'wealth ratio',
            'apple', 'nvidia', 'microsoft', 'tesla', 'amazon', 'meta', 'alphabet'
        ]
        
        # Technology keywords
        tech_keywords = [
            'programming', 'python', 'javascript', 'react', 'node', 'api',
            'database', 'software', 'development', 'coding', 'algorithm'
        ]
        
        # VPS/Networking keywords
        vps_keywords = [
            'vps', 'server', 'nginx', 'proxy', 'clash', 'v2ray', 'ubuntu',
            'debian', 'ssh', 'firewall', 'networking'
        ]
        
        # Business keywords
        business_keywords = [
            'business', 'strategy', 'management', 'leadership', 'marketing',
            'sales', 'entrepreneurship', 'startup'
        ]
        
        # Count keyword matches
        finance_score = sum(1 for keyword in finance_keywords if keyword in content_lower or keyword in file_lower)
        tech_score = sum(1 for keyword in tech_keywords if keyword in content_lower or keyword in file_lower)
        vps_score = sum(1 for keyword in vps_keywords if keyword in content_lower or keyword in file_lower)
        business_score = sum(1 for keyword in business_keywords if keyword in content_lower or keyword in file_lower)
        
        # Determine category based on highest score
        scores = {
            'Investment Analysis': finance_score,
            'Technology': tech_score,
            'VPS & Networking': vps_score,
            'Business Strategy': business_score
        }
        
        max_score = max(scores.values())
        if max_score >= 2:  # Minimum threshold
            return max(scores, key=scores.get)
        
        return "General"
    
    def _detect_tags_from_content(self, content: str, title: str) -> List[str]:
        """Auto-detect tags based on content analysis"""
        content_text = (content + " " + title).lower()
        
        # Comprehensive tag mapping
        tag_keywords = {
            # Finance & Investment
            'Investment': ['investment', 'investing', 'portfolio', 'asset'],
            'Valuation': ['valuation', 'pe ratio', 'peg', 'wealth ratio', 'pegy'],
            'Stock Analysis': ['stock', 'equity', 'share', 'ticker'],
            'Financial Metrics': ['earnings', 'revenue', 'margin', 'roe', 'roa'],
            'Apple': ['apple', 'aapl', 'iphone', 'ipad', 'mac'],
            'NVIDIA': ['nvidia', 'nvda', 'gpu', 'ai chip', 'cuda'],
            'Microsoft': ['microsoft', 'msft', 'azure', 'office'],
            'Tesla': ['tesla', 'tsla', 'electric vehicle', 'ev'],
            'Amazon': ['amazon', 'amzn', 'aws', 'e-commerce'],
            'Meta': ['meta', 'facebook', 'instagram', 'metaverse'],
            'Alphabet': ['alphabet', 'google', 'googl', 'search'],
            'Magnificent 7': ['magnificent 7', 'mag 7', 'big tech'],
            'Quality Investing': ['quality', 'moat', 'competitive advantage'],
            'Growth Investing': ['growth', 'growth rate', 'expansion'],
            'Peter Lynch': ['peter lynch', 'lynch', 'magellan'],
            'WEALTH Ratio': ['wealth ratio', 'wealth formula'],
            'PEGY': ['pegy', 'peg yield'],
            
            # Technology
            'Python': ['python', 'django', 'flask', 'pandas'],
            'JavaScript': ['javascript', 'js', 'node', 'react', 'vue'],
            'Web Development': ['html', 'css', 'frontend', 'backend'],
            'Database': ['database', 'sql', 'mysql', 'postgresql'],
            'API': ['api', 'rest', 'graphql', 'endpoint'],
            'CSS Styling': ['css', 'styling', 'design', 'ui'],
            'Dark Tables': ['dark table', 'table styling', 'html table'],
            
            # VPS & Networking
            'VPS': ['vps', 'virtual private server', 'cloud server'],
            'V2Ray': ['v2ray', 'vmess', 'proxy server'],
            'Clash': ['clash', 'subscription', 'proxy client'],
            'Nginx': ['nginx', 'web server', 'reverse proxy'],
            'Ubuntu': ['ubuntu', 'linux', 'debian'],
            'Firewall': ['firewall', 'ufw', 'iptables'],
            'SSH': ['ssh', 'secure shell', 'remote access'],
            'Security': ['security', 'encryption', 'ssl', 'tls'],
            'Server Setup': ['server setup', 'configuration', 'installation'],
            'Networking': ['networking', 'network', 'tcp', 'udp'],
            'Tutorial': ['tutorial', 'guide', 'how to', 'step by step'],
            
            # Business
            'Business Strategy': ['strategy', 'strategic', 'planning'],
            'Management': ['management', 'leadership', 'team'],
            'Marketing': ['marketing', 'promotion', 'advertising'],
            'Entrepreneurship': ['entrepreneur', 'startup', 'business']
        }
        
        detected_tags = []
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in content_text for keyword in keywords):
                detected_tags.append(tag)
        
        # Limit to reasonable number of tags
        return detected_tags[:15]
    
    def batch_process_files(self, file_paths: List[str], 
                           default_category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Process multiple markdown files into article data"""
        articles = []
        
        for file_path in file_paths:
            try:
                article_data = self.create_article_from_markdown_file(
                    file_path=file_path,
                    category=default_category
                )
                articles.append(article_data)
                print(f"✅ Processed: {file_path}")
            except Exception as e:
                print(f"❌ Error processing {file_path}: {str(e)}")
        
        return articles
    
    def get_processing_summary(self, article_data: Dict[str, Any]) -> str:
        """Get a summary of the processing results"""
        summary_parts = [
            f"Title: {article_data.get('title', 'N/A')}",
            f"Category: {article_data.get('category', 'N/A')}",
            f"Tags: {len(article_data.get('tags', []))} detected",
            f"Has Tables: {'Yes' if article_data.get('has_styled_tables', False) else 'No'}",
            f"Content Length: {len(article_data.get('content', ''))} characters"
        ]
        
        if article_data.get('tags'):
            summary_parts.append(f"Tags: {', '.join(article_data['tags'][:5])}")
        
        return "\n".join(summary_parts)

# Utility functions for easy integration
def create_article_from_file(file_path: str, **kwargs) -> Dict[str, Any]:
    """Convenience function to create article from file"""
    creator = EnhancedArticleCreator()
    return creator.create_article_from_markdown_file(file_path, **kwargs)

def create_article_from_content(content: str, title: str, **kwargs) -> Dict[str, Any]:
    """Convenience function to create article from content"""
    creator = EnhancedArticleCreator()
    return creator.create_article_from_content(content, title, **kwargs)

# Example usage
if __name__ == "__main__":
    # Test with the wealth ratio article
    wealth_ratio_path = "/Users/sdg223157/Library/CloudStorage/GoogleDrive-isky999@gmail.com/My Drive/wealth_ratio_article.md"
    
    if os.path.exists(wealth_ratio_path):
        creator = EnhancedArticleCreator()
        
        try:
            article_data = creator.create_article_from_markdown_file(wealth_ratio_path)
            print("Article Processing Summary:")
            print("=" * 50)
            print(creator.get_processing_summary(article_data))
            print("=" * 50)
            
            # Show first 500 characters of processed content
            content_preview = article_data['content'][:500] + "..."
            print(f"\nContent Preview:\n{content_preview}")
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Test file not found. Please check the path.")
