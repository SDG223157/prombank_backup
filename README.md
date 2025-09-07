# PromBank Backup - Enhanced Article Creation System

A comprehensive system for creating and managing articles with automatic table styling and MCP integration.

## 🚀 Features

### ✨ Automatic Table Styling
- **Dark Professional Tables**: Automatically converts markdown tables to beautifully styled HTML tables
- **Multiple Table Types**: Support for comparison tables, financial data tables, and sensitivity analysis matrices
- **Responsive Design**: Tables adapt to different screen sizes
- **Print-Friendly**: Optimized styles for printing
- **Hover Effects**: Interactive table rows with smooth transitions

### 🔧 Enhanced Article Creation
- **Auto-Detection**: Automatically detects titles, categories, and tags from content
- **Real-Time Data**: Yahoo Finance integration for accurate stock prices and metrics
- **Automatic Dating**: Always uses current date for analysis date and calculates review dates
- **Batch Processing**: Process multiple markdown files at once
- **File Validation**: Validate markdown files before processing
- **MCP Integration**: Seamless integration with MCP prombank backup system

### 📊 Supported Table Styles
- **Dark Tables**: Professional dark theme with teal accents
- **Comparison Tables**: Orange-accented tables for comparisons
- **Financial Tables**: Green-accented tables for financial data
- **Sensitivity Analysis**: Special containers for analysis matrices

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd prombank_backup
   ```

2. **Install dependencies**:
   ```bash
   cd unified-python
   pip install -r requirements.txt
   ```

3. **Set up environment**:
   ```bash
   # Create .env file with your configuration
   cp .env.example .env
   ```

## 📖 Usage

### Basic Article Creation

```python
from article_creator import EnhancedArticleCreator

creator = EnhancedArticleCreator()

# Create article from markdown file
article_data = creator.create_article_from_markdown_file(
    file_path="path/to/your/article.md",
    category="Investment Analysis",  # Optional - auto-detected
    tags=["Investment", "Analysis"]   # Optional - auto-detected
)

print(creator.get_processing_summary(article_data))
```

### MCP Integration

```python
from mcp_article_integration import MCPArticleIntegration

integration = MCPArticleIntegration()

# Create MCP article with automatic table styling
result = integration.create_mcp_article_from_file(
    file_path="path/to/your/article.md",
    dry_run=True  # Test without creating
)

print(f"Success: {result['success']}")
```

### Command Line Interface

```bash
# Single file processing
python mcp_article_integration.py article.md --dry-run

# Batch processing
python mcp_article_integration.py --batch file1.md file2.md --category="Technology"

# File validation
python mcp_article_integration.py --validate article.md
```

## 🎨 Table Styling Examples

### Basic Dark Table
```markdown
| Company | Ticker | PE Ratio |
|---------|--------|----------|
| **Apple** | AAPL | 35 |
| **Microsoft** | MSFT | 36 |
```

Automatically converts to a professional dark table with:
- Dark background (#2c3e50)
- Light text (#ecf0f1)
- Hover effects
- Professional spacing
- Bold row headers

### Sensitivity Analysis Matrix
```markdown
### Two-Factor Sensitivity Analysis

| Growth/Quality | 15.0 | 16.0 | 17.0 |
|----------------|------|------|------|
| **8.0%** | 6.2 | 6.7 | 7.2 |
| **10.0%** | 6.8 | 7.4 | 8.0 |

*Assumes: PE ratio of 30, dividend yield of 1%*
```

Creates a containerized table with title and notes.

## 📁 File Structure

```
unified-python/
├── table_processor.py                    # Core table processing logic
├── article_creator.py                    # Enhanced article creation
├── enhanced_stock_article_creator.py     # Stock analysis with real-time data
├── yahoo_finance_integration.py          # Yahoo Finance API integration
├── date_utils.py                         # Automatic date handling utilities
├── mcp_article_integration.py            # MCP integration layer
├── copy_fix_processor.py                 # Copy functionality fixes
├── templates/
│   ├── dark_table_styles.css             # CSS template for tables
│   └── view_article.html                 # Article view template (copy button removed)
├── main.py                               # Flask web application
├── database.py                           # Database models
└── requirements.txt                      # Python dependencies
```

## 🔧 Configuration

### Auto-Detection Settings

The system automatically detects:

- **Categories**: Based on content keywords
  - Investment Analysis
  - Technology  
  - VPS & Networking
  - Business Strategy
  - General

- **Tags**: Comprehensive tag detection including:
  - Financial terms (Investment, Valuation, Stock Analysis)
  - Technology terms (Python, JavaScript, CSS Styling)
  - Company names (Apple, NVIDIA, Microsoft, etc.)
  - Technical terms (VPS, Nginx, Security, etc.)

### CSS Customization

Modify `templates/dark_table_styles.css` to customize:
- Color schemes
- Spacing and padding
- Hover effects
- Responsive breakpoints
- Print styles

## 🎯 Supported Content Types

### Financial Articles
- Stock analysis with valuation tables
- Company comparisons
- Financial metrics tables
- Sensitivity analysis matrices

### Technical Articles
- Code examples with data tables
- Configuration comparisons
- Performance metrics
- Feature comparison matrices

### Tutorial Articles
- Step-by-step guides with data tables
- Configuration examples
- Troubleshooting matrices

## 🚀 Advanced Features

### Batch Processing
Process multiple files with consistent styling:

```python
creator = EnhancedArticleCreator()
articles = creator.batch_process_files([
    "article1.md",
    "article2.md", 
    "article3.md"
])
```

### File Validation
Validate markdown files before processing:

```python
integration = MCPArticleIntegration()
result = integration.validate_markdown_file("article.md")

if result['valid']:
    print("✅ File is ready for processing")
else:
    print("❌ Issues found:", result['issues'])
```

### Custom Table Types
Extend with custom table styles:

```python
# Add custom CSS classes
custom_css = """
.custom-table {
    background-color: #1a1a1a;
    border: 2px solid #ff6b35;
}
"""

processor = DarkTableProcessor()
processor.css_template += custom_css
```

## 🔍 Examples

See the `examples/` directory for:
- Sample markdown files
- Generated HTML output
- CSS customization examples
- Integration examples

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

## 🔄 Version History

### v1.0.0 (Current)
- ✅ Automatic table styling with dark theme
- ✅ Enhanced article creation with auto-detection
- ✅ MCP integration layer
- ✅ Command-line interface
- ✅ Batch processing support
- ✅ File validation
- ✅ Responsive and print-friendly styles

---

**Built with ❤️ for creating beautiful, professional articles with stunning table presentations.**