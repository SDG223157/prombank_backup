# MCP Tool Update Guide

## How to See New Tools in Cursor

When you add new tools to your MCP server, you need to follow these steps to make them available in Cursor:

### Step 1: Build the MCP Server
```bash
cd /Users/sdg223157/prombank_backup/prombank_backup/mcp-server
npm run build
```

### Step 2: Reinstall Globally
```bash
npm uninstall -g prompt-house-premium-mcp
npm install -g .
```

### Step 3: Verify Installation
```bash
which prompt-house-premium-mcp
# Should output: /Users/sdg223157/.nvm/versions/node/v23.4.0/bin/prompt-house-premium-mcp

# Check if your new tool is in the compiled code
grep -i "import_articles" $(npm root -g)/prompt-house-premium-mcp/dist/index.js
```

### Step 4: Restart Cursor
**This is the most important step!**

1. **Quit Cursor completely** (Cmd+Q on Mac, or File → Quit)
2. Wait a few seconds
3. Reopen Cursor

### Step 5: Verify the Tool is Available

After restarting Cursor, the `import_articles` tool should now be available. You can verify by:

1. Opening the MCP tools panel in Cursor
2. Looking for the `import_articles` tool
3. Or simply trying to use it in a conversation

## Common Issues

### Issue: Tool still not showing up after restart

**Solution:**
1. Check if the MCP server is configured correctly:
   ```bash
   cat ~/.config/cursor/mcp.json
   # or
   cat ~/Library/Application\ Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json
   ```

2. Make sure your API token is set correctly in the MCP config

3. Try completely rebuilding and reinstalling:
   ```bash
   cd /Users/sdg223157/prombank_backup/prombank_backup/mcp-server
   rm -rf dist node_modules
   npm install
   npm run build
   npm uninstall -g prompt-house-premium-mcp
   npm install -g .
   ```

4. Restart Cursor again

### Issue: MCP server is not responding

**Solution:**
1. Check MCP server logs in Cursor (if available)
2. Test the MCP server manually:
   ```bash
   prompt-house-premium-mcp
   ```
   (Press Ctrl+C to exit)

3. Verify environment variables are set:
   ```bash
   echo $PROMPTHOUSE_API_URL
   echo $PROMPTHOUSE_ACCESS_TOKEN
   ```

### Issue: "Command not found" error

**Solution:**
1. The global installation might have failed. Reinstall:
   ```bash
   cd /Users/sdg223157/prombank_backup/prombank_backup/mcp-server
   npm install -g .
   ```

2. Check your PATH includes npm global bin:
   ```bash
   echo $PATH | grep npm
   ```

## Current Status

✅ **import_articles tool is now installed** (as of last update)

The following import types are supported:
- `json` - Direct JSON data import
- `url` - Import from remote JSON URL
- `markdown` or `md` - Import from Markdown content

## Testing the Tool

Once Cursor restarts and picks up the tool, you can test it with:

```json
{
  "type": "markdown",
  "markdown_content": "# Test Article\n\n**Category:** Test\n**Tags:** test\n\nThis is a test article."
}
```

## MCP Configuration Locations

Depending on how Cursor is configured, the MCP settings might be in:

1. **Cursor Settings UI**: Settings → Extensions → MCP
2. **Global config**: `~/.config/cursor/mcp.json`
3. **Cline/Roo extension**: `~/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json`

The configuration should look like:
```json
{
  "mcpServers": {
    "prompt-house-premium": {
      "command": "prompt-house-premium-mcp",
      "env": {
        "PROMPTHOUSE_API_URL": "https://prombank.app",
        "PROMPTHOUSE_ACCESS_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

## Quick Fix Script

Save this as `update-mcp.sh` for future updates:

```bash
#!/bin/bash
set -e

echo "🔨 Building MCP server..."
cd /Users/sdg223157/prombank_backup/prombank_backup/mcp-server
npm run build

echo "📦 Reinstalling globally..."
npm uninstall -g prompt-house-premium-mcp 2>/dev/null || true
npm install -g .

echo "✅ MCP server updated!"
echo "⚠️  Please restart Cursor to see the changes"
```

Then run:
```bash
chmod +x update-mcp.sh
./update-mcp.sh
```
