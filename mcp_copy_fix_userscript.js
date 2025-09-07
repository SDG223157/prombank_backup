// ==UserScript==
// @name         MCP Platform Copy Button Fix
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Fix copy button functionality on prombank-mcp.com
// @author       Assistant
// @match        https://prombank-mcp.com/*
// @match        https://*.prombank-mcp.com/*
// @grant        none
// @run-at       document-ready
// ==/UserScript==

(function() {
    'use strict';
    
    console.log('MCP Copy Fix: Loading...');
    
    // Enhanced copy function with multiple fallbacks
    async function fixedCopyToClipboard(text) {
        console.log('MCP Copy Fix: Attempting to copy', text.length, 'characters');
        
        // Clean the text first
        const cleanedText = cleanContentForCopy(text);
        
        // Method 1: Modern Clipboard API
        if (navigator.clipboard && window.isSecureContext) {
            try {
                await navigator.clipboard.writeText(cleanedText);
                showSuccessMessage('Content copied successfully!');
                return true;
            } catch (err) {
                console.warn('MCP Copy Fix: Clipboard API failed:', err);
            }
        }
        
        // Method 2: Legacy execCommand
        try {
            const textArea = document.createElement('textarea');
            textArea.value = cleanedText;
            textArea.style.cssText = 'position:fixed;left:-9999px;top:-9999px;opacity:0;';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            
            if (successful) {
                showSuccessMessage('Content copied successfully!');
                return true;
            }
        } catch (err) {
            console.warn('MCP Copy Fix: execCommand failed:', err);
        }
        
        // Method 3: Show manual copy instructions
        showManualCopyInstructions();
        return false;
    }
    
    // Clean content for copy compatibility
    function cleanContentForCopy(content) {
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
            '⚠️': '[WARNING]',
            '🟢': '[GREEN]',
            '🔴': '[RED]',
            '🟡': '[YELLOW]',
            '🔵': '[BLUE]',
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
        
        let cleaned = content;
        for (const [original, replacement] of Object.entries(replacements)) {
            cleaned = cleaned.replace(new RegExp(original, 'g'), replacement);
        }
        
        // Clean up excessive whitespace
        cleaned = cleaned.replace(/\n{4,}/g, '\n\n\n');
        cleaned = cleaned.replace(/[ \t]+$/gm, ''); // Remove trailing spaces
        
        return cleaned;
    }
    
    // Show success message
    function showSuccessMessage(message) {
        removeExistingNotifications();
        
        const notification = document.createElement('div');
        notification.className = 'mcp-copy-success';
        notification.innerHTML = message;
        notification.style.cssText = `
            position: fixed !important;
            top: 20px !important;
            right: 20px !important;
            background: #2ecc71 !important;
            color: white !important;
            padding: 12px 20px !important;
            border-radius: 6px !important;
            font-weight: bold !important;
            z-index: 999999 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
    
    // Show manual copy instructions
    function showManualCopyInstructions() {
        removeExistingNotifications();
        
        const notification = document.createElement('div');
        notification.className = 'mcp-copy-instructions';
        notification.innerHTML = `
            <strong>📋 Copy Button Fixed</strong><br>
            Content is now selected.<br>
            Use: <strong>Ctrl+C</strong> (Windows) or <strong>Cmd+C</strong> (Mac)
        `;
        notification.style.cssText = `
            position: fixed !important;
            top: 20px !important;
            right: 20px !important;
            background: #f39c12 !important;
            color: white !important;
            padding: 15px 20px !important;
            border-radius: 6px !important;
            font-weight: bold !important;
            z-index: 999999 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
            line-height: 1.4 !important;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    // Remove existing notifications
    function removeExistingNotifications() {
        const existing = document.querySelectorAll('.mcp-copy-success, .mcp-copy-instructions');
        existing.forEach(el => el.remove());
    }
    
    // Find and fix copy buttons
    function fixCopyButtons() {
        console.log('MCP Copy Fix: Looking for copy buttons...');
        
        // Look for copy buttons by various selectors
        const selectors = [
            'button[onclick*="copy"]',
            '.copy-button',
            '[data-copy]',
            'button:contains("Copy")',
            'button[title*="copy" i]',
            'button[aria-label*="copy" i]'
        ];
        
        let buttonsFound = 0;
        
        selectors.forEach(selector => {
            const buttons = document.querySelectorAll(selector);
            buttons.forEach(button => {
                if (!button.dataset.mcpFixed) {
                    console.log('MCP Copy Fix: Fixing button:', button);
                    
                    // Mark as fixed
                    button.dataset.mcpFixed = 'true';
                    
                    // Remove existing onclick
                    button.onclick = null;
                    
                    // Add enhanced copy functionality
                    button.addEventListener('click', async function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        console.log('MCP Copy Fix: Copy button clicked');
                        
                        // Find content to copy
                        let content = findContentToCopy();
                        
                        if (content) {
                            await fixedCopyToClipboard(content);
                        } else {
                            showManualCopyInstructions();
                        }
                    });
                    
                    buttonsFound++;
                }
            });
        });
        
        console.log(`MCP Copy Fix: Fixed ${buttonsFound} copy buttons`);
        
        // Also look for buttons by text content
        const allButtons = document.querySelectorAll('button');
        allButtons.forEach(button => {
            if (!button.dataset.mcpFixed && 
                (button.textContent.toLowerCase().includes('copy') || 
                 button.innerHTML.toLowerCase().includes('copy'))) {
                
                console.log('MCP Copy Fix: Fixing text-based copy button:', button);
                button.dataset.mcpFixed = 'true';
                
                button.onclick = null;
                button.addEventListener('click', async function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const content = findContentToCopy();
                    if (content) {
                        await fixedCopyToClipboard(content);
                    } else {
                        showManualCopyInstructions();
                    }
                });
                
                buttonsFound++;
            }
        });
        
        return buttonsFound;
    }
    
    // Find content to copy
    function findContentToCopy() {
        // Look for content in various containers
        const selectors = [
            '.content',
            '.article-content', 
            '#content',
            '.markdown-content',
            '.article-body',
            '.post-content',
            'main',
            '.main-content'
        ];
        
        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element && element.innerText && element.innerText.trim().length > 100) {
                console.log('MCP Copy Fix: Found content in', selector);
                return element.innerText;
            }
        }
        
        // Fallback: look for the largest text content
        const allDivs = document.querySelectorAll('div, article, section');
        let largestContent = '';
        
        allDivs.forEach(div => {
            const text = div.innerText || div.textContent || '';
            if (text.length > largestContent.length && text.length > 1000) {
                largestContent = text;
            }
        });
        
        if (largestContent) {
            console.log('MCP Copy Fix: Found largest content:', largestContent.length, 'characters');
            return largestContent;
        }
        
        console.warn('MCP Copy Fix: No suitable content found');
        return null;
    }
    
    // Initialize the fix
    function initializeCopyFix() {
        console.log('MCP Copy Fix: Initializing...');
        
        // Fix existing buttons
        const buttonsFixed = fixCopyButtons();
        
        // Watch for new buttons (dynamic content)
        const observer = new MutationObserver(function(mutations) {
            let shouldRecheck = false;
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1 && (
                            node.tagName === 'BUTTON' || 
                            node.querySelector && node.querySelector('button')
                        )) {
                            shouldRecheck = true;
                        }
                    });
                }
            });
            
            if (shouldRecheck) {
                setTimeout(fixCopyButtons, 100);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        console.log(`MCP Copy Fix: Initialized successfully! Fixed ${buttonsFixed} buttons.`);
        
        // Show initialization message
        if (buttonsFixed > 0) {
            setTimeout(() => {
                showSuccessMessage(`Copy functionality enhanced! Fixed ${buttonsFixed} button(s).`);
            }, 1000);
        }
    }
    
    // Start the fix
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeCopyFix);
    } else {
        initializeCopyFix();
    }
    
    // Add CSS for better button visibility
    const style = document.createElement('style');
    style.textContent = `
        button[data-mcp-fixed="true"] {
            position: relative;
        }
        
        button[data-mcp-fixed="true"]:after {
            content: "✨";
            position: absolute;
            top: -5px;
            right: -5px;
            font-size: 10px;
        }
    `;
    document.head.appendChild(style);
    
})();
