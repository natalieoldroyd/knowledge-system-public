# Team Support Knowledge System

A collaborative knowledge management system for capturing and organizing support solutions across teams.

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

## Installation

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Or manually install Flask:
   ```bash
   pip install flask
   ```
   
2. **Verify Installation:**
   ```bash
   python --version  # Should show Python 3.6+
   ```

## Quick Start

1. **Navigate to Directory:**
   ```bash
   cd knowledge-system
   ```

2. **Start Web Interface:**
   ```bash
   python web_interface.py
   ```
   Then open http://localhost:5000 in your browser

3. **Add Knowledge (CLI):**
   ```bash
   python knowledge.py add "Webhook 403 errors" "CORS headers missing" "Add Access-Control-Allow-Origin header"
   ```

4. **Search Knowledge (CLI):**
   ```bash
   python knowledge.py search "webhook"
   ```

5. **List All (CLI):**
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
- ✅ **Clickable categories and tags** for easy filtering
- ✅ Export/import capabilities
- ✅ Edit existing knowledge entries

## Files

- `web_interface.py` - Web interface (Flask app)
- `knowledge.py` - Main CLI tool
- `knowledge.db` - SQLite database (auto-created)
- `config.json` - Configuration file (categories and Shopify products)
- `requirements.txt` - Python dependencies
- `templates/` - HTML templates for web interface
- `README.md` - This file

## Configuration

The system uses `config.json` to define available categories and Shopify products:

```json
{
  "categories": [
    "admin-api",
    "storefront-api", 
    "partners",
    "oxygen-api",
    "general"
  ],
  "shopify_products": [
    "shopify-cli",
    "webhooks",
    "orders-api",
    "payments-api",
    "..."
  ]
}
```

### Customizing Categories and Products

1. **Edit `config.json`** to add/remove categories or Shopify products
2. **Restart the web server** for changes to take effect:
   ```bash
   # Stop the server (Ctrl+C), then restart:
   python web_interface.py
   ```

### Navigation Features

- **Clickable Categories**: Click any category in the Statistics section to view all entries in that category
- **Clickable Tags**: Click any tag in the All Tags section to view all entries with that tag  
- **Cross-linking**: Categories and tags in search results are also clickable for easy navigation

### Port Configuration

The web interface runs on **port 5000** by default. To change the port:

1. **Edit `web_interface.py`** - Find line 511:
   ```python
   app.run(debug=True, host='127.0.0.1', port=5000)
   ```

2. **Change the port number**:
   ```python
   app.run(debug=True, host='127.0.0.1', port=8080)  # Example: port 8080
   ```

3. **Access via new port**: http://localhost:8080

**Note**: If you change the port, remember to update any bookmarks or documentation that reference the URL.

## System Requirements

- Operating System: Windows, macOS, or Linux
- Python 3.6 or higher
- ~10MB disk space
- Web browser (Chrome, Firefox, Safari, Edge)

## Generated Files

When you first run the application, these files are automatically created:
- `knowledge.db` - SQLite database (stores all your knowledge entries)
- No additional setup required!

## Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'flask'"**
- Solution: Install Flask using `pip install flask`

**"Permission denied" errors**
- Solution: Ensure you have write permissions in the directory

**Database issues**
- The SQLite database (`knowledge.db`) is created automatically on first run
- No manual database setup required

**Port already in use**
- Solution: Change the port in `web_interface.py` (see Port Configuration section above)

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


