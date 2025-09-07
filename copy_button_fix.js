/**
 * Copy Button Fix for MCP Platform
 * Addresses common clipboard API failures and browser compatibility issues
 */

// Enhanced copy function with multiple fallbacks
async function enhancedCopyToClipboard(text, elementId = null) {
    // Method 1: Modern Clipboard API (most reliable)
    if (navigator.clipboard && window.isSecureContext) {
        try {
            await navigator.clipboard.writeText(text);
            showCopySuccess();
            return true;
        } catch (err) {
            console.warn('Clipboard API failed:', err);
            // Fall through to next method
        }
    }
    
    // Method 2: Legacy execCommand (fallback for older browsers)
    try {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        if (successful) {
            showCopySuccess();
            return true;
        }
    } catch (err) {
        console.warn('execCommand failed:', err);
    }
    
    // Method 3: Manual selection prompt (last resort)
    try {
        if (elementId) {
            const element = document.getElementById(elementId);
            if (element) {
                // Select the content for manual copy
                const range = document.createRange();
                range.selectNodeContents(element);
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                
                showCopyInstructions();
                return true;
            }
        }
    } catch (err) {
        console.warn('Manual selection failed:', err);
    }
    
    // Method 4: Show copy instructions
    showCopyInstructions();
    return false;
}

// Success feedback
function showCopySuccess() {
    // Remove any existing notifications
    removeExistingNotifications();
    
    const notification = document.createElement('div');
    notification.className = 'copy-success-notification';
    notification.innerHTML = '✅ Content copied to clipboard successfully!';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #2ecc71;
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        font-weight: bold;
        z-index: 10000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// Manual copy instructions
function showCopyInstructions() {
    removeExistingNotifications();
    
    const notification = document.createElement('div');
    notification.className = 'copy-instruction-notification';
    notification.innerHTML = `
        <strong>📋 Manual Copy Required</strong><br>
        Please select the content and use:<br>
        • Ctrl+C (Windows/Linux)<br>
        • Cmd+C (Mac)
    `;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #f39c12;
        color: white;
        padding: 15px 20px;
        border-radius: 6px;
        font-weight: bold;
        z-index: 10000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        max-width: 250px;
        line-height: 1.4;
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Remove existing notifications
function removeExistingNotifications() {
    const existing = document.querySelectorAll('.copy-success-notification, .copy-instruction-notification');
    existing.forEach(el => el.remove());
}

// Content size optimization for large articles
function optimizeContentForCopy(content) {
    // Remove excessive whitespace
    content = content.replace(/\n{3,}/g, '\n\n');
    
    // Replace problematic Unicode characters
    const replacements = {
        '¥': 'CNY ',
        '€': 'EUR ',
        '£': 'GBP ',
        '↗': '(Improving)',
        '↘': '(Declining)',
        '→': '->',
        '←': '<-',
        '✅': '[PASS]',
        '❌': '[FAIL]',
        '🟢': '[GREEN]',
        '🔴': '[RED]',
        '🟡': '[YELLOW]',
        '∛': 'cbrt',
        '÷': '/',
        '×': '*',
        '±': '+/-',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '…': '...',
        '–': '-',
        '—': '--'
    };
    
    for (const [original, replacement] of Object.entries(replacements)) {
        content = content.replace(new RegExp(original, 'g'), replacement);
    }
    
    return content;
}

// Chunked copy for large content
async function copyInChunks(content, chunkSize = 10000) {
    const chunks = [];
    for (let i = 0; i < content.length; i += chunkSize) {
        chunks.push(content.substring(i, i + chunkSize));
    }
    
    if (chunks.length === 1) {
        return enhancedCopyToClipboard(content);
    }
    
    // For multiple chunks, copy first chunk and show instructions
    const success = await enhancedCopyToClipboard(chunks[0]);
    
    if (success) {
        const notification = document.createElement('div');
        notification.innerHTML = `
            <strong>📄 Large Content Detected</strong><br>
            Copied chunk 1 of ${chunks.length}<br>
            <button onclick="copyRemainingChunks(${JSON.stringify(chunks.slice(1))})">
                Copy Remaining Chunks
            </button>
        `;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #3498db;
            color: white;
            padding: 15px 20px;
            border-radius: 6px;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        document.body.appendChild(notification);
    }
    
    return success;
}

// Copy remaining chunks function
window.copyRemainingChunks = async function(chunks) {
    for (let i = 0; i < chunks.length; i++) {
        try {
            await navigator.clipboard.writeText(chunks[i]);
            console.log(`Copied chunk ${i + 2}`);
        } catch (err) {
            console.error(`Failed to copy chunk ${i + 2}:`, err);
            break;
        }
    }
    
    removeExistingNotifications();
    showCopySuccess();
};

// Enhanced copy button event handler
function setupEnhancedCopyButton() {
    // Find all copy buttons
    const copyButtons = document.querySelectorAll('[data-copy], .copy-button, button[onclick*="copy"]');
    
    copyButtons.forEach(button => {
        // Remove existing event listeners
        button.onclick = null;
        
        // Add enhanced copy functionality
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Find content to copy
            let content = '';
            
            // Method 1: Look for data-copy-target attribute
            const target = this.getAttribute('data-copy-target');
            if (target) {
                const targetElement = document.getElementById(target);
                if (targetElement) {
                    content = targetElement.innerText || targetElement.textContent;
                }
            }
            
            // Method 2: Look for nearby content
            if (!content) {
                const contentContainer = document.querySelector('.content, .article-content, #content, .markdown-content');
                if (contentContainer) {
                    content = contentContainer.innerText || contentContainer.textContent;
                }
            }
            
            // Method 3: Look for pre-formatted content
            if (!content) {
                const preElement = document.querySelector('pre, code, .code-block');
                if (preElement) {
                    content = preElement.innerText || preElement.textContent;
                }
            }
            
            if (!content) {
                alert('No content found to copy. Please select the text manually and use Ctrl+C (Cmd+C on Mac).');
                return;
            }
            
            // Optimize content for copying
            const optimizedContent = optimizeContentForCopy(content);
            
            // Attempt to copy
            if (optimizedContent.length > 20000) {
                await copyInChunks(optimizedContent);
            } else {
                await enhancedCopyToClipboard(optimizedContent);
            }
        });
    });
}

// Auto-setup when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupEnhancedCopyButton);
} else {
    setupEnhancedCopyButton();
}

// Also setup when content changes (for dynamic content)
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'childList') {
            setupEnhancedCopyButton();
        }
    });
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

// Export for manual use
window.enhancedCopyToClipboard = enhancedCopyToClipboard;
window.optimizeContentForCopy = optimizeContentForCopy;
window.setupEnhancedCopyButton = setupEnhancedCopyButton;

console.log('Enhanced copy functionality loaded successfully!');
