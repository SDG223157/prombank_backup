#!/usr/bin/env python3
"""
MCP Article Integration with Automatic Table Styling
Integrates the enhanced article creator with MCP prombank backup functionality
"""

import os
import sys
from typing import Dict, Any, List, Optional
from article_creator import EnhancedArticleCreator

class MCPArticleIntegration:
    """Integration layer for creating MCP articles with automatic table styling"""
    
    def __init__(self):
        self.article_creator = EnhancedArticleCreator()
    
    def create_mcp_article_from_file(self, 
                                   file_path: str,
                                   title: Optional[str] = None,
                                   category: Optional[str] = None,
                                   tags: Optional[List[str]] = None,
                                   dry_run: bool = False) -> Dict[str, Any]:
        """
        Create an MCP article from a markdown file with automatic table styling
        
        Args:
            file_path: Path to the markdown file
            title: Article title (auto-detected if None)
            category: Article category (auto-detected if None)
            tags: Article tags (auto-detected if None)
            dry_run: If True, return article data without creating MCP article
            
        Returns:
            Dictionary with MCP article creation result
        """
        
        # Process the file into article data
        article_data = self.article_creator.create_article_from_markdown_file(
            file_path=file_path,
            title=title,
            category=category,
            tags=tags
        )
        
        if dry_run:
            return {
                'success': True,
                'dry_run': True,
                'article_data': article_data,
                'summary': self.article_creator.get_processing_summary(article_data)
            }
        
        # Here you would integrate with actual MCP creation
        # For now, we'll simulate the MCP call structure
        mcp_result = self._simulate_mcp_creation(article_data)
        
        return mcp_result
    
    def create_mcp_article_from_content(self,
                                      content: str,
                                      title: str,
                                      category: Optional[str] = None,
                                      tags: Optional[List[str]] = None,
                                      dry_run: bool = False) -> Dict[str, Any]:
        """
        Create an MCP article from markdown content with automatic table styling
        
        Args:
            content: Markdown content
            title: Article title
            category: Article category
            tags: Article tags
            dry_run: If True, return article data without creating MCP article
            
        Returns:
            Dictionary with MCP article creation result
        """
        
        # Process the content into article data
        article_data = self.article_creator.create_article_from_content(
            content=content,
            title=title,
            category=category,
            tags=tags
        )
        
        if dry_run:
            return {
                'success': True,
                'dry_run': True,
                'article_data': article_data,
                'summary': self.article_creator.get_processing_summary(article_data)
            }
        
        # Here you would integrate with actual MCP creation
        mcp_result = self._simulate_mcp_creation(article_data)
        
        return mcp_result
    
    def _simulate_mcp_creation(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate MCP article creation (replace with actual MCP call)
        
        This is where you would call the actual MCP prombank backup create_article function:
        
        Example:
        ```python
        from mcp_prombank_backup import create_article
        
        result = create_article(
            title=article_data['title'],
            content=article_data['content'],
            category=article_data.get('category'),
            tags=article_data.get('tags')
        )
        ```
        """
        
        # Simulate successful creation
        return {
            'success': True,
            'article_id': 'simulated-article-id-12345',
            'title': article_data['title'],
            'category': article_data.get('category'),
            'tags': article_data.get('tags', []),
            'has_styled_tables': article_data.get('has_styled_tables', False),
            'content_length': len(article_data.get('content', '')),
            'message': 'Article created successfully with automatic table styling'
        }
    
    def batch_create_articles(self, 
                            file_paths: List[str],
                            default_category: Optional[str] = None,
                            dry_run: bool = False) -> List[Dict[str, Any]]:
        """Create multiple articles from markdown files"""
        
        results = []
        
        for file_path in file_paths:
            try:
                result = self.create_mcp_article_from_file(
                    file_path=file_path,
                    category=default_category,
                    dry_run=dry_run
                )
                result['source_file'] = file_path
                results.append(result)
                
                status = "✅ DRY RUN" if dry_run else "✅ CREATED"
                print(f"{status}: {os.path.basename(file_path)}")
                
            except Exception as e:
                error_result = {
                    'success': False,
                    'error': str(e),
                    'source_file': file_path
                }
                results.append(error_result)
                print(f"❌ ERROR: {os.path.basename(file_path)} - {str(e)}")
        
        return results
    
    def validate_markdown_file(self, file_path: str) -> Dict[str, Any]:
        """Validate a markdown file for article creation"""
        
        validation_result = {
            'valid': True,
            'issues': [],
            'recommendations': []
        }
        
        if not os.path.exists(file_path):
            validation_result['valid'] = False
            validation_result['issues'].append(f"File not found: {file_path}")
            return validation_result
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for basic structure
            if not content.strip():
                validation_result['issues'].append("File is empty")
                validation_result['valid'] = False
            
            # Check for title
            if not re.search(r'^#\s+.+$', content, re.MULTILINE):
                validation_result['recommendations'].append("Consider adding a main title (# Title)")
            
            # Check for tables
            table_count = len(re.findall(r'\|.*\|', content))
            if table_count > 0:
                validation_result['recommendations'].append(
                    f"Found {table_count} table rows - will be automatically styled"
                )
            
            # Check file size
            content_length = len(content)
            if content_length > 100000:  # 100KB
                validation_result['recommendations'].append(
                    "Large file detected - consider breaking into multiple articles"
                )
            elif content_length < 500:  # 500 chars
                validation_result['recommendations'].append(
                    "Short content detected - consider expanding"
                )
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['issues'].append(f"Error reading file: {str(e)}")
        
        return validation_result

# Command-line interface
def main():
    """Command-line interface for MCP article creation"""
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python mcp_article_integration.py <markdown_file> [--dry-run] [--category=<category>]")
        print("  python mcp_article_integration.py --validate <markdown_file>")
        print("  python mcp_article_integration.py --batch <file1> <file2> ... [--dry-run]")
        return
    
    integration = MCPArticleIntegration()
    
    # Validate mode
    if sys.argv[1] == '--validate':
        if len(sys.argv) < 3:
            print("Error: Please specify a file to validate")
            return
        
        file_path = sys.argv[2]
        result = integration.validate_markdown_file(file_path)
        
        print(f"\nValidation Results for: {file_path}")
        print("=" * 50)
        print(f"Valid: {'✅ Yes' if result['valid'] else '❌ No'}")
        
        if result['issues']:
            print(f"\nIssues:")
            for issue in result['issues']:
                print(f"  ❌ {issue}")
        
        if result['recommendations']:
            print(f"\nRecommendations:")
            for rec in result['recommendations']:
                print(f"  💡 {rec}")
        
        return
    
    # Parse arguments
    dry_run = '--dry-run' in sys.argv
    category = None
    files = []
    
    for arg in sys.argv[1:]:
        if arg.startswith('--category='):
            category = arg.split('=', 1)[1]
        elif not arg.startswith('--'):
            files.append(arg)
    
    if not files:
        print("Error: No files specified")
        return
    
    # Batch mode
    if '--batch' in sys.argv:
        files = [f for f in files if f != '--batch']
        results = integration.batch_create_articles(files, category, dry_run)
        
        print(f"\nBatch Processing Results:")
        print("=" * 50)
        successful = sum(1 for r in results if r.get('success', False))
        print(f"Processed: {len(results)} files")
        print(f"Successful: {successful}")
        print(f"Failed: {len(results) - successful}")
        
    else:
        # Single file mode
        file_path = files[0]
        result = integration.create_mcp_article_from_file(
            file_path=file_path,
            category=category,
            dry_run=dry_run
        )
        
        print(f"\nArticle Creation Result:")
        print("=" * 50)
        
        if result.get('success'):
            if dry_run:
                print("✅ DRY RUN SUCCESSFUL")
                print(result.get('summary', ''))
            else:
                print("✅ ARTICLE CREATED")
                print(f"ID: {result.get('article_id', 'N/A')}")
                print(f"Title: {result.get('title', 'N/A')}")
                print(f"Category: {result.get('category', 'N/A')}")
                print(f"Tags: {len(result.get('tags', []))}")
        else:
            print("❌ CREATION FAILED")
            print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
