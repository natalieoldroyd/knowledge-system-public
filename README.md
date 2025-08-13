# Personal Support Knowledge System

A simple knowledge management system for capturing and organizing support solutions.

## Quick Start

1. **Start Web Interface:**
   ```bash
   cd knowledge-system && python web_interface.py
   ```
   Then open http://localhost:5000 in your browser

2. **Add Knowledge (CLI):**
   ```bash
   python knowledge.py add "Webhook 403 errors" "CORS headers missing" "Add Access-Control-Allow-Origin header"
   ```

3. **Search Knowledge (CLI):**
   ```bash
   python knowledge.py search "webhook"
   ```

4. **List All (CLI):**
   ```bash
   python knowledge.py list
   ```

## Features

- ✅ Web interface for easy knowledge entry and browsing
- ✅ Simple command-line interface
- ✅ SQLite database (no setup required)
- ✅ Full-text search
- ✅ Multi-category support
- ✅ Categorization and tagging
- ✅ Export/import capabilities
- ✅ Edit existing knowledge entries

## Files

- `web_interface.py` - Web interface (Flask app)
- `knowledge.py` - Main CLI tool
- `knowledge.db` - SQLite database (auto-created)
- `config.json` - Configuration file
- `templates/` - HTML templates for web interface
- `README.md` - This file

## Usage Examples

```bash
# Add knowledge with category
python knowledge.py add "API Rate Limiting" "Too many requests" "Implement exponential backoff" --category api_issue --tags "api,rate-limit,429"

# Search by category
python knowledge.py search --category webhook_problem

# Export knowledge
python knowledge.py export knowledge_backup.json

# Get stats
python knowledge.py stats
```


