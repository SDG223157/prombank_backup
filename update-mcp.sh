#!/bin/bash
set -e

echo "🔨 Building MCP server..."
cd "$(dirname "$0")/mcp-server"
npm run build

echo "📦 Reinstalling globally..."
npm uninstall -g prompt-house-premium-mcp 2>/dev/null || true
npm install -g .

echo "✅ MCP server updated successfully!"
echo ""
echo "⚠️  IMPORTANT: Please restart Cursor completely (Cmd+Q) to see the new tools"
echo ""
echo "Available tools:"
echo "  - import_articles (NEW!)"
echo "  - create_article"
echo "  - get_article_list"
echo "  - search_articles"
echo "  - and many more..."
