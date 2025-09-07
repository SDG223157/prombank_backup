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
        """Return the dark table CSS template"""
        return """
<style>
.dark-table {
    background-color: #2c3e50;
    color: #ecf0f1;
    border-collapse: collapse;
    width: 100%;
    margin: 8px 0;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.dark-table th {
    background-color: #34495e;
    color: #ecf0f1;
    padding: 12px 15px;
    text-align: center;
    font-weight: bold;
    border-bottom: 2px solid #1abc9c;
}

.dark-table td {
    padding: 10px 15px;
    text-align: center;
    border-bottom: 1px solid #34495e;
}

.dark-table tr:nth-child(even) {
    background-color: #34495e;
}

.dark-table tr:hover {
    background-color: #3498db;
    transition: background-color 0.3s ease;
}

.dark-table .row-header {
    background-color: #34495e;
    font-weight: bold;
    text-align: left;
}

.table-container {
    background-color: #2c3e50;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
}

.table-title {
    color: #ecf0f1;
    font-weight: bold;
    margin-bottom: 8px;
    text-align: center;
}

.table-note {
    color: #bdc3c7;
    font-style: italic;
    text-align: center;
    margin-top: 8px;
    font-size: 0.9em;
}
</style>
"""
    
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
    
    def convert_table_to_html(self, table: Dict[str, Any], table_id: str = None) -> str:
        """Convert a single table to dark-styled HTML"""
        html_parts = []
        
        # Add container if there's a title or note
        if table['title'] or table['note']:
            html_parts.append('<div class="table-container">')
            
            if table['title']:
                html_parts.append(f'<div class="table-title">{table["title"]}</div>')
        
        # Start table
        table_class = f'class="dark-table"'
        if table_id:
            table_class = f'class="dark-table" id="{table_id}"'
        
        html_parts.append(f'<table {table_class}>')
        
        # Add header
        if table['headers']:
            html_parts.append('<thead>')
            html_parts.append('<tr>')
            for header in table['headers']:
                html_parts.append(f'<th>{header}</th>')
            html_parts.append('</tr>')
            html_parts.append('</thead>')
        
        # Add body
        if table['rows']:
            html_parts.append('<tbody>')
            for i, row in enumerate(table['rows']):
                html_parts.append('<tr>')
                for j, cell in enumerate(row):
                    # Check if first column should be a row header (contains **text**)
                    if j == 0 and cell.startswith('**') and cell.endswith('**'):
                        cell_content = cell.replace('**', '')
                        html_parts.append(f'<td class="row-header"><strong>{cell_content}</strong></td>')
                    else:
                        # Handle bold text within cells
                        cell_content = cell.replace('**', '<strong>').replace('**', '</strong>')
                        html_parts.append(f'<td>{cell_content}</td>')
                html_parts.append('</tr>')
            html_parts.append('</tbody>')
        
        html_parts.append('</table>')
        
        # Add note if exists
        if table['note']:
            html_parts.append(f'<div class="table-note">{table["note"]}</div>')
        
        # Close container if opened
        if table['title'] or table['note']:
            html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def process_markdown_content(self, markdown_content: str) -> str:
        """Process entire markdown content and convert tables to styled HTML"""
        # Extract tables
        tables = self.extract_tables_from_markdown(markdown_content)
        
        if not tables:
            return markdown_content
        
        # Start with CSS
        processed_content = markdown_content
        
        # Replace each table with styled HTML
        for i, table in enumerate(tables):
            table_html = self.convert_table_to_html(table, f"table-{i}")
            processed_content = processed_content.replace(table['original'], table_html)
        
        # Add CSS at the beginning if we have tables
        if tables:
            processed_content = self.css_template + '\n\n' + processed_content
        
        return processed_content
    
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
