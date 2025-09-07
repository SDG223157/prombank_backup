#!/usr/bin/env python3
"""
Table Processor for Markdown to HTML with Dark CSS Styling
Automatically converts markdown tables to professionally styled HTML tables
"""

import re
import markdown
from typing import List, Dict, Any

class DarkTableProcessor:
    """Process markdown content and convert tables to dark-styled HTML tables"""
    
    def __init__(self):
        self.css_template = self._get_dark_table_css()
    
    def _get_dark_table_css(self) -> str:
        """Return empty CSS for MCP articles - use clean markdown instead"""
        return ""
    
    def extract_tables_from_markdown(self, markdown_content: str) -> List[Dict[str, Any]]:
        """Extract table information from markdown content"""
        tables = []
        
        # Pattern to match markdown tables with optional titles and notes
        table_pattern = r'((?:### .+\n\n)?)\|(.+)\|\n\|(?:[-:| ]+)\|\n((?:\|.+\|\n?)+)(?:\n\n\*(.+)\*)?'
        
        matches = re.finditer(table_pattern, markdown_content, re.MULTILINE)
        
        for match in matches:
            title = match.group(1).strip().replace('### ', '') if match.group(1) else None
            header = match.group(2)
            rows = match.group(3)
            note = match.group(4) if match.group(4) else None
            
            # Parse header
            headers = [col.strip() for col in header.split('|') if col.strip()]
            
            # Parse rows
            row_data = []
            for row in rows.strip().split('\n'):
                if row.strip() and '|' in row:
                    cols = [col.strip() for col in row.split('|') if col.strip()]
                    if cols:  # Only add non-empty rows
                        row_data.append(cols)
            
            tables.append({
                'title': title,
                'headers': headers,
                'rows': row_data,
                'note': note,
                'original': match.group(0)
            })
        
        return tables
    
    def convert_table_to_markdown(self, table: Dict[str, Any]) -> str:
        """Convert a table back to clean markdown format"""
        markdown_parts = []
        
        # Add title if exists
        if table['title']:
            markdown_parts.append(f"**{table['title']}**")
            markdown_parts.append("")
        
        # Create header row
        if table['headers']:
            header_row = "| " + " | ".join(table['headers']) + " |"
            separator_row = "|" + "|".join(["---" for _ in table['headers']]) + "|"
            markdown_parts.append(header_row)
            markdown_parts.append(separator_row)
        
        # Add data rows
        if table['rows']:
            for row in table['rows']:
                # Clean up cell content
                cleaned_row = []
                for cell in row:
                    # Keep bold formatting but clean up
                    cleaned_cell = cell.strip()
                    cleaned_row.append(cleaned_cell)
                
                row_string = "| " + " | ".join(cleaned_row) + " |"
                markdown_parts.append(row_string)
        
        # Add note if exists
        if table['note']:
            markdown_parts.append("")
            markdown_parts.append(f"*{table['note']}*")
        
        return '\n'.join(markdown_parts)
    
    def process_markdown_content(self, markdown_content: str) -> str:
        """Process entire markdown content - keep clean markdown for MCP articles"""
        # For MCP articles, just return clean markdown without CSS
        # The platform will handle table rendering
        return self._clean_markdown_spacing(markdown_content)
    
    def _clean_markdown_spacing(self, content: str) -> str:
        """Clean up markdown spacing issues"""
        
        # Remove excessive blank lines before tables
        patterns = [
            (r'(\*\*[^*]+:\*\*)\s*\n\n\n+(\|)', r'\1\n\n\2'),  # Bold headers before tables
            (r'(### [^#\n]+)\s*\n\n\n+(\|)', r'\1\n\n\2'),     # H3 headers before tables  
            (r'(#### [^#\n]+)\s*\n\n\n+(\|)', r'\1\n\n\2'),    # H4 headers before tables
            (r'\n\n\n+(\|)', r'\n\n\1'),                        # General excessive spacing before tables
            (r'(\|[^\n]+\|)\n\n\n+(\|)', r'\1\n\2'),            # Between table rows
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        return content
    
    def _fix_header_table_spacing(self, content: str) -> str:
        """Fix spacing between markdown headers/text and tables"""
        
        # Patterns that often precede tables with too much space
        patterns = [
            (r'(\*\*Market Metrics:\*\*)\s*\n\n+(<table)', r'\1\n\n\2'),
            (r'(\*\*Valuation Ratios:\*\*)\s*\n\n+(<table)', r'\1\n\n\2'),
            (r'(\*\*Profitability & Returns:\*\*)\s*\n\n+(<table)', r'\1\n\n\2'),
            (r'(\*\*Financial Health:\*\*)\s*\n\n+(<table)', r'\1\n\n\2'),
            (r'(\*\*[^*]+:\*\*)\s*\n\n+(<table)', r'\1\n\n\2'),  # Generic bold headers
            (r'(### [^#\n]+)\s*\n\n+(<table)', r'\1\n\n\2'),  # H3 headers
            (r'(#### [^#\n]+)\s*\n\n+(<table)', r'\1\n\n\2'),  # H4 headers
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        return content
    
    def create_article_with_styled_tables(self, title: str, markdown_content: str, 
                                        category: str = None, tags: List[str] = None) -> Dict[str, Any]:
        """Create article data with automatically styled tables"""
        
        # Process the markdown content
        styled_content = self.process_markdown_content(markdown_content)
        
        # Prepare article data
        article_data = {
            'title': title,
            'content': styled_content,
            'has_styled_tables': len(self.extract_tables_from_markdown(markdown_content)) > 0
        }
        
        if category:
            article_data['category'] = category
        
        if tags:
            article_data['tags'] = tags
        
        return article_data

def process_file_to_article(file_path: str, title: str = None, 
                           category: str = None, tags: List[str] = None) -> Dict[str, Any]:
    """Process a markdown file and return article data with styled tables"""
    
    processor = DarkTableProcessor()
    
    # Read file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract title from content if not provided
    if not title:
        title_match = re.match(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
        else:
            title = "Untitled Article"
    
    return processor.create_article_with_styled_tables(title, content, category, tags)

# Example usage and testing
if __name__ == "__main__":
    # Test with sample markdown content
    sample_markdown = """
# Test Article

## Sample Table

| Company | Ticker | PE Ratio | Growth Rate |
|---------|--------|----------|-------------|
| **Apple** | AAPL | 35 | 6% |
| **Microsoft** | MSFT | 36 | 18% |
| **NVIDIA** | NVDA | 49 | 30% |

*Sample data for testing purposes*

Another paragraph after the table.
"""
    
    processor = DarkTableProcessor()
    result = processor.process_markdown_content(sample_markdown)
    print("Processed Content:")
    print(result)
