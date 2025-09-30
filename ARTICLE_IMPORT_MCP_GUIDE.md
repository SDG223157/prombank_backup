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
| `markdown_content` | string | Required for markdown/md type | Markdown content containing article(s) |
| `split_sections` | boolean | Optional for markdown/md type | Whether to split markdown into multiple articles by headers (default: false - imports as ONE article) |

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

**IMPORTANT: By default, markdown imports the ENTIRE file as ONE article.**

To import the complete markdown document as a single article (default behavior):

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

**Separator (only used when split_sections=true):**
- Use `---` (three dashes) to separate multiple articles in the same markdown file

---

### Splitting Markdown into Multiple Articles

If you want to split a markdown file into multiple articles by sections, set `split_sections: true`:

```markdown
# First Article

**Category:** Category One
**Tags:** tag1, tag2

Content for first article...

---

# Second Article

**Category:** Category Two
**Tags:** tag3, tag4

Content for second article...
```

**When to use `split_sections: true`:**
- When you have a markdown file with multiple independent articles
- When each `---` separator should create a new article
- When each `###` subsection should become its own article

**When to use default (split_sections: false or omitted):**
- When importing a single document/article (most common case)
- When you want the entire markdown file imported as one article
- When the document is a complete work (like a book chapter, research paper, etc.)

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

### Example 3: Markdown Import (Single Article - Default)

Import the ENTIRE markdown file as ONE article (recommended for most cases):

```json
{
  "type": "markdown",
  "markdown_content": "# 解缙草书《唐宋诗文》分篇解读\n\n**总字数：753字（不含标点）**\n\n---\n\n## 第一首：崔珏《有赠》\n\n### 原文\n绿槐夹道集昏鸦，敕使传宣坐赐茶。\n...(full document content)..."
}
```

This will create ONE article with:
- **Title**: "解缙草书《唐宋诗文》分篇解读" (extracted from first # header)
- **Content**: Everything after the title (the entire document)

### Example 4: Markdown Import (Split into Multiple Articles)

If you want to split a markdown file into separate articles, use `split_sections: true`:

```json
{
  "type": "markdown",
  "markdown_content": "# Getting Started with AI\n\n**Category:** AI Tutorial\n**Tags:** AI, Tutorial, Beginner\n\nArtificial Intelligence is transforming...\n\n---\n\n# Advanced Prompt Engineering\n\n**Category:** Prompt Engineering\n**Tags:** Prompts, Advanced, LLM\n\nThis article covers advanced techniques...",
  "split_sections": true
}
```

This will create TWO separate articles (split by `---`)

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
