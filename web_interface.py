#!/usr/bin/env python3
"""
Web Interface for Knowledge System
A simple Flask web app for managing knowledge.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from knowledge import KnowledgeDB
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Add custom filter for JSON parsing
@app.template_filter('from_json')
def from_json_filter(value):
    """Parse JSON string in templates."""
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return [value] if value else []

# Initialize database
db = KnowledgeDB()

# Load config
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except:
    config = {
        "categories": ["general"],
        "shopify_products": [""]
    }

@app.route('/')
def index():
    """Main dashboard."""
    stats = db.get_stats()
    recent_knowledge = db.search_knowledge(limit=10)
    all_tags = db.get_all_tags()
    return render_template('index.html', stats=stats, recent_knowledge=recent_knowledge, all_tags=all_tags, config=config)

@app.route('/add', methods=['GET', 'POST'])
def add_knowledge():
    """Add new knowledge."""
    if request.method == 'POST':
        try:
            title = request.form['title']
            problem = request.form['problem']
            solution = request.form['solution']
            categories_str = request.form.get('categories', '')
            categories = [c.strip() for c in categories_str.split(',') if c.strip()] if categories_str else ['general']
            product = request.form.get('shopify_product') or None
            api_version = request.form.get('api_version') or None
            code = request.form.get('code_examples') or None
            tags_str = request.form.get('tags', '')
            tags = [t.strip() for t in tags_str.split(',') if t.strip()] if tags_str else None
            notes = request.form.get('notes') or None
            
            knowledge_uuid = db.add_knowledge(
                title=title,
                problem=problem,
                solution=solution,
                categories=categories,
                shopify_product=product,
                api_version=api_version,
                code_examples=code,
                tags=tags,
                notes=notes,
                source="web"
            )
            
            flash(f'Knowledge added successfully! UUID: {knowledge_uuid}', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Error adding knowledge: {str(e)}', 'error')
    
    return render_template('add.html', config=config)

@app.route('/search')
def search():
    """Search knowledge."""
    query = request.args.get('q', '')
    categories_str = request.args.get('categories', '')
    categories = [c.strip() for c in categories_str.split(',') if c.strip()] if categories_str else None
    product = request.args.get('product', '')
    
    if query or categories or product:
        results = db.search_knowledge(
            query=query if query else None,
            categories=categories,
            shopify_product=product if product else None
        )
    else:
        results = []
    
    return render_template('search.html', 
                         results=results, 
                         query=query, 
                         categories=categories_str, 
                         product=product,
                         config=config)

@app.route('/knowledge/<int:knowledge_id>')
def view_knowledge(knowledge_id):
    """View specific knowledge."""
    knowledge = db.get_knowledge(knowledge_id=knowledge_id)
    if not knowledge:
        flash('Knowledge not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('view.html', knowledge=knowledge)

@app.route('/knowledge/<int:knowledge_id>/edit', methods=['GET', 'POST'])
def edit_knowledge(knowledge_id):
    """Edit existing knowledge."""
    knowledge = db.get_knowledge(knowledge_id=knowledge_id)
    if not knowledge:
        flash('Knowledge not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            title = request.form['title']
            problem = request.form['problem']
            solution = request.form['solution']
            categories_str = request.form.get('categories', '')
            categories = [c.strip() for c in categories_str.split(',') if c.strip()] if categories_str else ['general']
            product = request.form.get('shopify_product') or None
            api_version = request.form.get('api_version') or None
            code = request.form.get('code_examples') or None
            tags_str = request.form.get('tags', '')
            tags = [t.strip() for t in tags_str.split(',') if t.strip()] if tags_str else None
            notes = request.form.get('notes') or None
            
            # Update the knowledge entry
            db.update_knowledge(
                knowledge_id=knowledge_id,
                title=title,
                problem=problem,
                solution=solution,
                categories=categories,
                shopify_product=product,
                api_version=api_version,
                code_examples=code,
                tags=tags,
                notes=notes
            )
            
            flash('Knowledge updated successfully!', 'success')
            return redirect(url_for('view_knowledge', knowledge_id=knowledge_id))
            
        except Exception as e:
            flash(f'Error updating knowledge: {str(e)}', 'error')
    
    return render_template('edit.html', knowledge=knowledge, config=config)

@app.route('/api/search')
def api_search():
    """API endpoint for search."""
    query = request.args.get('q', '')
    categories_str = request.args.get('categories', '')
    categories = [c.strip() for c in categories_str.split(',') if c.strip()] if categories_str else None
    limit = int(request.args.get('limit', 10))
    
    results = db.search_knowledge(
        query=query if query else None,
        categories=categories,
        limit=limit
    )
    
    return jsonify(results)

@app.route('/api/stats')
def api_stats():
    """API endpoint for stats."""
    return jsonify(db.get_stats())

@app.route('/use/<int:knowledge_id>', methods=['POST'])
def use_knowledge(knowledge_id):
    """Record knowledge usage."""
    helpful = request.form.get('helpful') == 'true'
    notes = request.form.get('notes', '')
    
    db.record_usage(knowledge_id, context="web", helpful=helpful, notes=notes)
    flash('Usage recorded!', 'success')
    
    return redirect(url_for('view_knowledge', knowledge_id=knowledge_id))

# Create templates directory and basic templates
def create_templates():
    """Create basic HTML templates."""
    os.makedirs('templates', exist_ok=True)
    
    # Base template
    base_template = '''<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Knowledge System{% endblock %}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .code-block { background: #f8f9fa; padding: 1rem; border-radius: 0.375rem; font-family: monospace; }
        .tag { background: #e9ecef; padding: 0.25rem 0.5rem; border-radius: 0.25rem; margin: 0.125rem; display: inline-block; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">📚 Knowledge System</a>
            <div class="navbar-nav">
                <a class="nav-link" href="{{ url_for('index') }}">Dashboard</a>
                <a class="nav-link" href="{{ url_for('add_knowledge') }}">Add Knowledge</a>
                <a class="nav-link" href="{{ url_for('search') }}">Search</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    # Index template
    index_template = '''{% extends "base.html" %}
{% block title %}Dashboard - Knowledge System{% endblock %}
{% block content %}
<div class="row">
    <div class="col-md-4">
        <div class="card">
            <div class="card-header"><h5>📊 Statistics</h5></div>
            <div class="card-body">
                <p><strong>Total Knowledge:</strong> {{ stats.total_count }}</p>
                <p><strong>Recent (7 days):</strong> {{ stats.recent_additions }}</p>
                <h6>Categories:</h6>
                {% for category, count in stats.categories.items() %}
                    <span class="tag">{{ category }}: {{ count }}</span>
                {% endfor %}
            </div>
        </div>
    </div>
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5>🕒 Recent Knowledge</h5>
                <a href="{{ url_for('add_knowledge') }}" class="btn btn-primary btn-sm float-end">Add New</a>
            </div>
            <div class="card-body">
                {% for knowledge in recent_knowledge %}
                    <div class="border-bottom pb-2 mb-2">
                        <h6><a href="{{ url_for('view_knowledge', knowledge_id=knowledge.id) }}">{{ knowledge.title }}</a></h6>
                        <small class="text-muted">{{ knowledge.category }} • {{ knowledge.created_at }}</small>
                    </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Add template
    add_template = '''{% extends "base.html" %}
{% block title %}Add Knowledge{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header"><h5>📝 Add New Knowledge</h5></div>
    <div class="card-body">
        <form method="POST">
            <div class="mb-3">
                <label class="form-label">Issue Title *</label>
                <input type="text" class="form-control" name="title" required>
            </div>
            
            <div class="mb-3">
                <label class="form-label">Problem Description *</label>
                <textarea class="form-control" name="problem" rows="4" required></textarea>
            </div>
            
            <div class="mb-3">
                <label class="form-label">Solution Steps *</label>
                <textarea class="form-control" name="solution" rows="6" required></textarea>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Category</label>
                        <select class="form-control" name="category">
                            {% for category in config.categories %}
                                <option value="{{ category }}">{{ category.replace('_', ' ').title() }}</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Shopify Product</label>
                        <select class="form-control" name="shopify_product">
                            <option value="">Select product...</option>
                            {% for product in config.shopify_products %}
                                <option value="{{ product }}">{{ product }}</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="mb-3">
                <label class="form-label">Code Examples</label>
                <textarea class="form-control font-monospace" name="code_examples" rows="4"></textarea>
            </div>
            
            <div class="mb-3">
                <label class="form-label">Tags</label>
                <input type="text" class="form-control" name="tags" placeholder="comma, separated, tags">
            </div>
            
            <div class="mb-3">
                <label class="form-label">Notes</label>
                <textarea class="form-control" name="notes" rows="3"></textarea>
            </div>
            
            <button type="submit" class="btn btn-primary">💾 Save Knowledge</button>
            <a href="{{ url_for('index') }}" class="btn btn-secondary">Cancel</a>
        </form>
    </div>
</div>
{% endblock %}'''
    
    # Search template
    search_template = '''{% extends "base.html" %}
{% block title %}Search Knowledge{% endblock %}
{% block content %}
<div class="card mb-4">
    <div class="card-header"><h5>🔍 Search Knowledge</h5></div>
    <div class="card-body">
        <form method="GET">
            <div class="row">
                <div class="col-md-6">
                    <input type="text" class="form-control" name="q" value="{{ query }}" placeholder="Search terms...">
                </div>
                <div class="col-md-3">
                    <select class="form-control" name="category">
                        <option value="">All categories</option>
                        {% for category in config.categories %}
                            <option value="{{ category }}" {{ 'selected' if category == category }}>
                                {{ category.replace('_', ' ').title() }}
                            </option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-3">
                    <button type="submit" class="btn btn-primary">Search</button>
                </div>
            </div>
        </form>
    </div>
</div>

{% if results %}
<div class="card">
    <div class="card-header"><h5>Results ({{ results|length }})</h5></div>
    <div class="card-body">
        {% for knowledge in results %}
            <div class="border-bottom pb-3 mb-3">
                <h6><a href="{{ url_for('view_knowledge', knowledge_id=knowledge.id) }}">{{ knowledge.title }}</a></h6>
                <p class="text-muted">{{ knowledge.problem[:200] }}...</p>
                <small>
                    <span class="tag">{{ knowledge.category }}</span>
                    {% if knowledge.shopify_product %}
                        <span class="tag">{{ knowledge.shopify_product }}</span>
                    {% endif %}
                    • Used {{ knowledge.usage_count }} times
                </small>
            </div>
        {% endfor %}
    </div>
</div>
{% endif %}
{% endblock %}'''
    
    # View template
    view_template = '''{% extends "base.html" %}
{% block title %}{{ knowledge.title }}{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header">
        <h5>📝 {{ knowledge.title }}</h5>
        <small class="text-muted">
            {{ knowledge.category }} • {{ knowledge.created_at }}
            {% if knowledge.shopify_product %} • {{ knowledge.shopify_product }}{% endif %}
        </small>
    </div>
    <div class="card-body">
        <h6>❗ Problem:</h6>
        <p>{{ knowledge.problem }}</p>
        
        <h6>✅ Solution:</h6>
        <div>{{ knowledge.solution | replace('\n', '<br>') | safe }}</div>
        
        {% if knowledge.code_examples %}
            <h6>💻 Code Examples:</h6>
            <div class="code-block">{{ knowledge.code_examples }}</div>
        {% endif %}
        
        {% if knowledge.tags %}
            <h6>🏷️ Tags:</h6>
            {% for tag in knowledge.tags.split(',') %}
                <span class="tag">{{ tag.strip() }}</span>
            {% endfor %}
        {% endif %}
        
        {% if knowledge.notes %}
            <h6>📋 Notes:</h6>
            <p>{{ knowledge.notes }}</p>
        {% endif %}
        
        <hr>
        <p><small>📊 Used {{ knowledge.usage_count }} times • Source: {{ knowledge.source }}</small></p>
        
        <form method="POST" action="{{ url_for('use_knowledge', knowledge_id=knowledge.id) }}" class="d-inline">
            <button type="submit" name="helpful" value="true" class="btn btn-success btn-sm">👍 Helpful</button>
            <button type="submit" name="helpful" value="false" class="btn btn-outline-secondary btn-sm">👎 Not Helpful</button>
        </form>
    </div>
</div>
{% endblock %}'''
    
    # Write templates
    with open('templates/base.html', 'w') as f:
        f.write(base_template)
    with open('templates/index.html', 'w') as f:
        f.write(index_template)
    with open('templates/add.html', 'w') as f:
        f.write(add_template)
    with open('templates/search.html', 'w') as f:
        f.write(search_template)
    with open('templates/view.html', 'w') as f:
        f.write(view_template)

if __name__ == '__main__':
    create_templates()
    print("🌐 Starting web interface at http://localhost:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
