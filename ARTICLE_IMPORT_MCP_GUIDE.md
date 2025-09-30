# Article Import MCP Tool Guide

## Overview

The `import_articles` MCP tool allows you to bulk import articles into prombank_backup using the Model Context Protocol. This tool supports three import methods:
1. **JSON Import**: Direct import from JSON data
2. **URL Import**: Import from a remote JSON URL
3. **Markdown Import**: Import from Markdown file content

## Prerequisites

- MCP server must be configured and running
- Valid API token with authentication
- Articles must be in the correct JSON format

## Tool: `import_articles`

### Description
Import multiple articles from JSON data, URL, or Markdown content

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string (enum: 'json', 'url', 'markdown', 'md') | Yes | Import type: json (direct data), url (from remote source), or markdown/md (markdown content) |
| `articles` | array | Required for json type | Array of article objects to import |
| `url` | string | Required for url type | URL to fetch articles from |
| `markdown_content` | string | Required for markdown/md type | Markdown content containing articles |

### Article Object Format

Each article in the `articles` array must have the following structure:

```json
{
  "title": "Article Title",           // Required: Article title
  "content": "Article content here",  // Required: Full article content (markdown supported)
  "category": "Category Name",        // Optional: Category (default: "Imported")
  "tags": ["tag1", "tag2"],          // Optional: Array of tags
  "prompt_id": "uuid-here",          // Optional: Associated prompt ID
  "metadata": {                       // Optional: Additional metadata
    "author": "Author Name",
    "date": "2025-09-30",
    "source": "Source Name"
  }
}
```

### Markdown Format

For markdown imports, articles should follow this structure:

```markdown
# Article Title

**Category:** Category Name
**Tags:** tag1, tag2, tag3
**Prompt ID:** optional-uuid-here
**Metadata:** author=John Doe, date=2025-09-30

Article content goes here in full markdown format.

You can include:
- Lists
- **Bold** and *italic* text
- Code blocks
- Links and images
- Multiple paragraphs

Everything after the metadata section is treated as article content.

---

# Second Article Title

**Category:** Another Category
**Tags:** tutorial, advanced

Content for the second article...
```

**Metadata Fields:**
- `**Category:**` - Article category (optional, defaults to "Imported")
- `**Tags:**` - Comma-separated list of tags (optional)
- `**Prompt ID:**` or `**Prompt_ID:**` - UUID of associated prompt (optional)
- `**Metadata:**` - Key-value pairs in `key=value, key2=value2` format (optional)

**Separator:**
- Use `---` (three dashes) to separate multiple articles in the same markdown file

## Usage Examples

### Example 1: JSON Import (Direct Data)

```json
{
  "type": "json",
  "articles": [
    {
      "title": "Getting Started with AI",
      "content": "# Introduction\n\nArtificial Intelligence is transforming...",
      "category": "AI Tutorial",
      "tags": ["AI", "Tutorial", "Beginner"],
      "metadata": {
        "author": "AI Expert",
        "difficulty": "Beginner"
      }
    },
    {
      "title": "Advanced Prompt Engineering",
      "content": "# Advanced Techniques\n\nThis article covers...",
      "category": "Prompt Engineering",
      "tags": ["Prompts", "Advanced", "LLM"],
      "prompt_id": "abc-123-def-456",
      "metadata": {
        "author": "Prompt Engineer",
        "difficulty": "Advanced"
      }
    }
  ]
}
```

### Example 2: URL Import

Import articles from a remote JSON file:

```json
{
  "type": "url",
  "url": "https://example.com/articles.json"
}
```

The JSON file at the URL should contain an array of articles or an object with an `articles` key:

**Option A: Direct array**
```json
[
  {
    "title": "Article 1",
    "content": "Content here..."
  },
  {
    "title": "Article 2",
    "content": "More content..."
  }
]
```

**Option B: Object with articles key**
```json
{
  "articles": [
    {
      "title": "Article 1",
      "content": "Content here..."
    }
  ]
}
```

### Example 3: Markdown Import

Import articles from markdown content:

```json
{
  "type": "markdown",
  "markdown_content": "# Getting Started with AI\n\n**Category:** AI Tutorial\n**Tags:** AI, Tutorial, Beginner\n**Metadata:** author=AI Expert, difficulty=Beginner\n\n# Introduction\n\nArtificial Intelligence is transforming how we interact with technology...\n\n## Key Concepts\n\n1. Machine Learning\n2. Neural Networks\n3. Natural Language Processing\n\n---\n\n# Advanced Prompt Engineering\n\n**Category:** Prompt Engineering\n**Tags:** Prompts, Advanced, LLM\n**Prompt ID:** abc-123-def-456\n\n# Advanced Techniques\n\nThis article covers advanced prompt engineering techniques...\n\n## Best Practices\n\n- Use clear instructions\n- Provide examples\n- Iterate and refine"
}
```

Or with a multiline string (if your tool supports it):

```json
{
  "type": "md",
  "markdown_content": "# Article One\n\n**Category:** Tutorial\n**Tags:** guide, beginner\n\nContent for article one...\n\n---\n\n# Article Two\n\n**Category:** Advanced\n**Tags:** guide, advanced\n\nContent for article two..."
}
```

## Response Format

### Success Response

```json
{
  "message": "Successfully imported 2 articles via MCP",
  "imported_articles": [
    {
      "id": "uuid-1",
      "title": "Getting Started with AI",
      "word_count": 1234
    },
    {
      "id": "uuid-2",
      "title": "Advanced Prompt Engineering",
      "word_count": 2345
    }
  ]
}
```

### Error Response

```json
{
  "error": "Article import failed: [error message]"
}
```

## Features

1. **Automatic Word & Character Counting**: The system automatically calculates and stores word and character counts for each article.

2. **Prompt Association**: If you provide a `prompt_id`, the article will be linked to that prompt (if it exists and you have access to it).

3. **Tag Management**: Support for multiple tags per article for better organization.

4. **Metadata Storage**: Store additional metadata with each article for custom use cases.

5. **Category Organization**: Organize articles into categories for easy filtering.

6. **Access Control**: Admin users can associate articles with any prompt, while regular users can only use their own prompts.

## Common Use Cases

### 1. Migrate Articles from Another System

Export articles from your current system as JSON, then use the `import_articles` tool to migrate them to prombank_backup.

### 2. Bulk Content Creation

If you have AI-generated content in JSON format, you can bulk import all articles at once.

### 3. Content Syndication

Set up automated imports from remote URLs to sync content from multiple sources.

### 4. Backup & Restore

Export articles to JSON for backup, then restore them using the import tool.

### 5. Import from Markdown Files

If you have articles written in Markdown files, you can directly import them by reading the file content and passing it to the import tool. This is ideal for:
- Blog posts written in Markdown
- Documentation files
- GitHub README files or wikis
- Any markdown-based content

## Best Practices

1. **Validate JSON**: Ensure your JSON is valid before attempting import
2. **Test with Small Batches**: Start with a few articles to verify format
3. **Use Categories**: Organize articles with meaningful categories
4. **Add Metadata**: Include useful metadata for future reference
5. **Link to Prompts**: Associate articles with prompts for better traceability

## API Endpoint

The MCP tool calls the following backend endpoint:

```
POST /api/mcp/import-articles
```

**Authentication**: Requires API token

**Request Body**:
```json
{
  "type": "json" | "url",
  "articles": [...],  // for json type
  "url": "..."        // for url type
}
```

## Troubleshooting

### Error: "API token required"
- Ensure your MCP server is configured with a valid API token
- Check the `PROMPTHOUSE_ACCESS_TOKEN` environment variable

### Error: "No articles provided for JSON import"
- Verify the `articles` array is not empty
- Check that the JSON structure matches the expected format

### Error: "URL content must be valid JSON"
- Ensure the URL returns valid JSON
- Check that the URL is accessible and returns the correct content type

### Error: "Prompt not found or access denied"
- Verify the `prompt_id` exists
- Check that you have access to the prompt (for non-admin users)

### Error: "Markdown content is required for markdown import"
- Ensure you're passing the `markdown_content` parameter
- Check that the parameter name is correct (use `markdown_content`, not just `content`)

### Error: "Failed to parse markdown"
- Verify your markdown format follows the expected structure
- Ensure article titles start with `#` (header syntax)
- Check that metadata fields use the `**Field:**` format
- Make sure articles are separated by `---` if multiple articles

### Error: "No valid articles found in markdown content"
- Verify that each article has both a title (header) and content
- Check that the markdown structure is correct
- Ensure there's content after the metadata section

## Related Tools

- `create_article`: Create a single article
- `get_article_list`: List all articles
- `search_articles`: Search for articles
- `update_article`: Update an existing article
- `delete_article`: Delete an article

## Support

For issues or questions, please refer to:
- Main documentation: `README.md`
- MCP Installation: `MCP_INSTALLATION_GUIDE.md`
- Article Storage Setup: `ARTICLE_STORAGE_SETUP_GUIDE.md`
