# Team Support Knowledge System

A collaborative knowledge management system for capturing and organizing support solutions across teams.

## 🎥 Demo Video

See the knowledge system in action:

https://github.com/natalieoldroyd/knowledge-system-public/raw/main/assets/videos/15-20-ju3e6-xipqr.mp4

*Video shows the clickable categories, tag filtering, and navigation features.*

## Quick Setup

1. **Clone Repository:**
   ```bash
   git clone https://github.com/natalieoldroyd/knowledge-system-public.git
   cd knowledge-system-public
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application:**
   ```bash
   python web_interface.py
   ```
   Then open http://localhost:5000 in your browser

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## CLI Usage Examples

```bash
# Add knowledge entry
python knowledge.py add "Webhook 403 errors" "CORS headers missing" "Add Access-Control-Allow-Origin header"

# Search knowledge
python knowledge.py search "webhook"

# List all entries
python knowledge.py list

# Get statistics
python knowledge.py stats
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
- Solution: Run `pip install -r requirements.txt` from the project directory

**"Permission denied" errors**
- Solution: Ensure you have write permissions in the directory

**Database issues**
- The SQLite database (`knowledge.db`) is created automatically on first run
- No manual database setup required

**Port already in use**
- Solution: Change the port in `web_interface.py` (see Port Configuration section above)

## Advanced Usage

```bash
# Add knowledge with specific category and tags
python knowledge.py add "API Rate Limiting" "Too many requests" "Implement exponential backoff" --category admin-api --tags "api,rate-limit,429"

# Search by category
python knowledge.py search --category webhooks

# Export knowledge backup
python knowledge.py export knowledge_backup.json
```

## Team Collaboration

This knowledge system is designed for team use:
- Share common solutions across support agents
- Maintain consistency in troubleshooting approaches  
- Build institutional knowledge over time
- Quick reference for escalated API support


