#!/usr/bin/env python3
"""
Copy-Friendly Content Processor
Fixes common clipboard issues in MCP articles by cleaning problematic characters
"""

import re
from typing import Dict, Any

class CopyFixProcessor:
    """Process content to make it copy-friendly for MCP platform"""
    
    def __init__(self):
        self.problematic_chars = {
            # Chinese currency and characters
            '¥': 'CNY ',
            '安琪酵母股份有限公司': 'Angel Yeast Co., Ltd',
            
            # Unicode arrows and symbols
            '↗': '(Improving)',
            '↘': '(Declining)', 
            '→': '->',
            '←': '<-',
            '↔': '<->',
            
            # Checkmarks and status symbols
            '✅': '[PASS]',
            '❌': '[FAIL]',
            '⚠️': '[WARNING]',
            '🔴': '[RED]',
            '🟡': '[YELLOW]',
            '🟢': '[GREEN]',
            '🔵': '[BLUE]',
            
            # Mathematical symbols
            '∛': 'cbrt',
            '÷': '/',
            '×': '*',
            '±': '+/-',
            
            # Special punctuation
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '…': '...',
            '–': '-',
            '—': '--',
            
            # Degree and percentage
            '°': ' degrees',
            '℃': 'C',
            '℉': 'F',
        }
    
    def clean_content_for_copy(self, content: str) -> str:
        """Clean content to make it copy-friendly"""
        
        # Replace problematic characters
        cleaned = content
        for old_char, new_char in self.problematic_chars.items():
            cleaned = cleaned.replace(old_char, new_char)
        
        # Fix spacing issues
        cleaned = self._fix_spacing_issues(cleaned)
        
        # Normalize line endings
        cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove excessive blank lines
        cleaned = re.sub(r'\n{4,}', '\n\n\n', cleaned)
        
        return cleaned
    
    def _fix_spacing_issues(self, content: str) -> str:
        """Fix common spacing issues that cause copy problems"""
        
        # Remove trailing spaces
        lines = content.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        content = '\n'.join(cleaned_lines)
        
        # Fix table spacing
        patterns = [
            # Remove extra spaces in table cells
            (r'\|\s{2,}([^|]+)\s{2,}\|', r'| \1 |'),
            
            # Fix header spacing
            (r'(\*\*[^*]+:\*\*)\s*\n\n{2,}(\|)', r'\1\n\n\2'),
            
            # Fix list spacing
            (r'(\d+\.)\s{2,}', r'\1 '),
            (r'(-)\s{2,}', r'\1 '),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        return content
    
    def chunk_content(self, content: str, max_chars: int = 10000) -> list:
        """Break content into copy-friendly chunks"""
        
        if len(content) <= max_chars:
            return [content]
        
        chunks = []
        current_chunk = ""
        
        # Split by major sections
        sections = re.split(r'\n## ', content)
        
        for i, section in enumerate(sections):
            if i > 0:
                section = "## " + section
            
            if len(current_chunk) + len(section) <= max_chars:
                current_chunk += section
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = section
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def create_copy_friendly_version(self, article_content: str) -> Dict[str, Any]:
        """Create a copy-friendly version of article content"""
        
        # Clean the content
        cleaned_content = self.clean_content_for_copy(article_content)
        
        # Create chunks
        chunks = self.chunk_content(cleaned_content)
        
        # Generate summary
        summary = {
            'original_length': len(article_content),
            'cleaned_length': len(cleaned_content),
            'num_chunks': len(chunks),
            'chunk_sizes': [len(chunk) for chunk in chunks],
            'problematic_chars_found': self._count_problematic_chars(article_content),
            'copy_friendly': True
        }
        
        return {
            'cleaned_content': cleaned_content,
            'chunks': chunks,
            'summary': summary
        }
    
    def _count_problematic_chars(self, content: str) -> Dict[str, int]:
        """Count problematic characters in content"""
        counts = {}
        for char in self.problematic_chars:
            count = content.count(char)
            if count > 0:
                counts[char] = count
        return counts

# Diagnostic function
def diagnose_copy_issues(content: str) -> Dict[str, Any]:
    """Diagnose potential copy issues in content"""
    
    processor = CopyFixProcessor()
    
    issues = {
        'content_length': len(content),
        'character_count': len(content),
        'line_count': len(content.split('\n')),
        'problematic_chars': processor._count_problematic_chars(content),
        'has_unicode': any(ord(char) > 127 for char in content),
        'has_tables': '|' in content,
        'has_chinese': any('\u4e00' <= char <= '\u9fff' for char in content),
        'recommendations': []
    }
    
    # Generate recommendations
    if issues['content_length'] > 20000:
        issues['recommendations'].append("Content too large - consider chunking")
    
    if issues['problematic_chars']:
        issues['recommendations'].append("Contains problematic Unicode characters")
    
    if issues['has_chinese']:
        issues['recommendations'].append("Contains Chinese characters - may cause encoding issues")
    
    if not issues['recommendations']:
        issues['recommendations'].append("Content appears copy-friendly")
    
    return issues

# Example usage
if __name__ == "__main__":
    # Test with sample problematic content
    test_content = """
# Test Article

**Market Metrics:**

| Company | Price | Change |
|---------|-------|--------|
| Apple | $150.25 | ↗ +2.5% |
| Google | ¥1,200 | ✅ Strong |

*Note: Data as of today*
"""
    
    processor = CopyFixProcessor()
    
    # Diagnose issues
    issues = diagnose_copy_issues(test_content)
    print("Diagnostic Results:")
    for key, value in issues.items():
        print(f"  {key}: {value}")
    
    # Create copy-friendly version
    result = processor.create_copy_friendly_version(test_content)
    print(f"\nCleaned Content:\n{result['cleaned_content']}")
