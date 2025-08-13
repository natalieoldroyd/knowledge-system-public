#!/usr/bin/env python3
"""
Personal Support Knowledge System
A simple CLI tool for managing support knowledge and solutions.
"""

import sqlite3
import json
import argparse
import datetime
import re
from pathlib import Path
from typing import List, Dict, Optional
import uuid

class KnowledgeDB:
    def __init__(self, db_path: str = "knowledge.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main knowledge table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                problem TEXT NOT NULL,
                solution TEXT NOT NULL,
                categories TEXT DEFAULT 'general',  -- JSON array of categories
                shopify_product TEXT,
                api_version TEXT,
                code_examples TEXT,
                tags TEXT,
                notes TEXT,
                source TEXT DEFAULT 'manual',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                effectiveness_score REAL DEFAULT 0.0
            )
        ''')
        
        # Usage tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                knowledge_id INTEGER,
                used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                context TEXT,
                helpful BOOLEAN,
                notes TEXT,
                FOREIGN KEY (knowledge_id) REFERENCES knowledge (id)
            )
        ''')
        
        # Create full-text search index
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
                title, problem, solution, tags, code_examples,
                content='knowledge',
                content_rowid='id'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_knowledge(self, title: str, problem: str, solution: str, 
                     categories: List[str] = None, shopify_product: str = None,
                     api_version: str = None, code_examples: str = None,
                     tags: List[str] = None, notes: str = None,
                     source: str = "manual") -> str:
        """Add new knowledge entry."""
        knowledge_uuid = str(uuid.uuid4())
        tags_str = ",".join(tags) if tags else ""
        categories_json = json.dumps(categories if categories else ["general"])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO knowledge (
                uuid, title, problem, solution, categories, shopify_product,
                api_version, code_examples, tags, notes, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (knowledge_uuid, title, problem, solution, categories_json, shopify_product,
              api_version, code_examples, tags_str, notes, source))
        
        knowledge_id = cursor.lastrowid
        
        # Update FTS index
        cursor.execute('''
            INSERT INTO knowledge_fts (rowid, title, problem, solution, tags, code_examples)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (knowledge_id, title, problem, solution, tags_str, code_examples or ""))
        
        conn.commit()
        conn.close()
        
        return knowledge_uuid
    
    def update_knowledge(self, knowledge_id: int, title: str, problem: str, solution: str,
                        categories: List[str] = None, shopify_product: str = None,
                        api_version: str = None, code_examples: str = None,
                        tags: List[str] = None, notes: str = None) -> bool:
        """Update existing knowledge entry."""
        tags_str = ",".join(tags) if tags else ""
        categories_json = json.dumps(categories if categories else ["general"])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE knowledge SET
                title = ?, problem = ?, solution = ?, categories = ?,
                shopify_product = ?, api_version = ?, code_examples = ?,
                tags = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title, problem, solution, categories_json, shopify_product,
              api_version, code_examples, tags_str, notes, knowledge_id))
        
        # Update FTS index
        cursor.execute('''
            UPDATE knowledge_fts SET
                title = ?, problem = ?, solution = ?, tags = ?, code_examples = ?
            WHERE rowid = ?
        ''', (title, problem, solution, tags_str, code_examples or "", knowledge_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    def search_knowledge(self, query: str = None, categories: List[str] = None, 
                        shopify_product: str = None, tags: List[str] = None,
                        limit: int = 20) -> List[Dict]:
        """Search knowledge entries."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if query:
            # Use FTS for text search
            sql = '''
                SELECT k.* FROM knowledge k
                JOIN knowledge_fts fts ON k.id = fts.rowid
                WHERE knowledge_fts MATCH ?
            '''
            params = [query]
        else:
            sql = 'SELECT * FROM knowledge WHERE 1=1'
            params = []
        
        # Add filters
        if categories:
            # Check if any of the requested categories are in the JSON array
            category_conditions = []
            for cat in categories:
                category_conditions.append("JSON_EXTRACT(categories, '$') LIKE ?")
                params.append(f'%"{cat}"%')
            if category_conditions:
                sql += f' AND ({" OR ".join(category_conditions)})'
        
        if shopify_product:
            sql += ' AND shopify_product = ?'
            params.append(shopify_product)
        
        if tags:
            for tag in tags:
                sql += ' AND tags LIKE ?'
                params.append(f'%{tag}%')
        
        sql += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(sql, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_knowledge(self, knowledge_id: int = None, knowledge_uuid: str = None) -> Optional[Dict]:
        """Get specific knowledge entry."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if knowledge_uuid:
            cursor.execute('SELECT * FROM knowledge WHERE uuid = ?', (knowledge_uuid,))
        elif knowledge_id:
            cursor.execute('SELECT * FROM knowledge WHERE id = ?', (knowledge_id,))
        else:
            return None
        
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def record_usage(self, knowledge_id: int, context: str = "manual", 
                    helpful: bool = None, notes: str = None):
        """Record knowledge usage for analytics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Record usage
        cursor.execute('''
            INSERT INTO knowledge_usage (knowledge_id, context, helpful, notes)
            VALUES (?, ?, ?, ?)
        ''', (knowledge_id, context, helpful, notes))
        
        # Update usage count
        cursor.execute('''
            UPDATE knowledge 
            SET usage_count = usage_count + 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (knowledge_id,))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total count
        cursor.execute('SELECT COUNT(*) FROM knowledge')
        total_count = cursor.fetchone()[0]
        
        # By category - flatten JSON arrays and count
        cursor.execute('''
            WITH RECURSIVE category_split(category, rest) AS (
                SELECT JSON_EXTRACT(categories, '$[0]'), categories FROM knowledge
                UNION ALL
                SELECT JSON_EXTRACT(rest, '$[1]'), JSON_REMOVE(rest, '$[0]') 
                FROM category_split 
                WHERE JSON_ARRAY_LENGTH(rest) > 1
            )
            SELECT category, COUNT(*) FROM category_split WHERE category IS NOT NULL GROUP BY category
        ''')
        categories = dict(cursor.fetchall())
        
        # Most used
        cursor.execute('''
            SELECT title, usage_count FROM knowledge 
            ORDER BY usage_count DESC LIMIT 5
        ''')
        most_used = cursor.fetchall()
        
        # Recent additions
        cursor.execute('''
            SELECT COUNT(*) FROM knowledge 
            WHERE created_at > date('now', '-7 days')
        ''')
        recent_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_count': total_count,
            'categories': categories,
            'most_used': most_used,
            'recent_additions': recent_count
        }
    
    def get_all_tags(self) -> List[Dict]:
        """Get all unique tags with their usage counts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all tags and split them
        cursor.execute('SELECT tags FROM knowledge WHERE tags IS NOT NULL AND tags != ""')
        tags_rows = cursor.fetchall()
        
        # Count tag usage
        tag_counts = {}
        for row in tags_rows:
            if row[0]:
                tags = [tag.strip() for tag in row[0].split(',')]
                for tag in tags:
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by usage count (descending) then alphabetically
        sorted_tags = sorted(tag_counts.items(), key=lambda x: (-x[1], x[0].lower()))
        
        conn.close()
        return [{'tag': tag, 'count': count} for tag, count in sorted_tags]
    
    def export_knowledge(self, file_path: str):
        """Export all knowledge to JSON file."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM knowledge ORDER BY created_at')
        knowledge = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM knowledge_usage ORDER BY used_at')
        usage = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        export_data = {
            'knowledge': knowledge,
            'usage': usage,
            'exported_at': datetime.datetime.now().isoformat()
        }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

def print_knowledge(knowledge: Dict, detailed: bool = False):
    """Pretty print knowledge entry."""
    print(f"\n📝 {knowledge['title']}")
    
    # Handle categories (JSON array)
    try:
        categories = json.loads(knowledge['categories']) if knowledge['categories'] else ['general']
        categories_str = ", ".join(categories)
        print(f"   Categories: {categories_str}")
    except:
        print(f"   Categories: {knowledge.get('categories', 'general')}")
    
    if knowledge['shopify_product']:
        print(f"   Product: {knowledge['shopify_product']}")
    if knowledge['tags']:
        print(f"   Tags: {knowledge['tags']}")
    
    if detailed:
        print(f"\n❗ Problem:")
        print(f"   {knowledge['problem']}")
        print(f"\n✅ Solution:")
        print(f"   {knowledge['solution']}")
        
        if knowledge['code_examples']:
            print(f"\n💻 Code:")
            print(f"   {knowledge['code_examples']}")
        
        if knowledge['notes']:
            print(f"\n📋 Notes:")
            print(f"   {knowledge['notes']}")
        
        print(f"\n📊 Usage: {knowledge['usage_count']} times")
        print(f"   Created: {knowledge['created_at']}")
    
    print("-" * 50)

def main():
    parser = argparse.ArgumentParser(description="Personal Support Knowledge System")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add new knowledge')
    add_parser.add_argument('title', help='Issue title')
    add_parser.add_argument('problem', help='Problem description')
    add_parser.add_argument('solution', help='Solution steps')
    add_parser.add_argument('--categories', nargs='+', default=['general'],
                           help='Categories (space-separated): app-proxy orders-api returns-api fulfillments-api products-api shopify-cli webhooks payments-api multipass customer-account-api bulk-operations media-api app-billing app-configuration oxygen-api storefront-api admin-api general')
    add_parser.add_argument('--product', help='Shopify product area')
    add_parser.add_argument('--api-version', help='API version (e.g., 2025-07)')
    add_parser.add_argument('--code', help='Code examples')
    add_parser.add_argument('--tags', help='Comma-separated tags')
    add_parser.add_argument('--notes', help='Additional notes')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search knowledge')
    search_parser.add_argument('query', nargs='?', help='Search query')
    search_parser.add_argument('--categories', nargs='+', help='Filter by categories (space-separated)')
    search_parser.add_argument('--product', help='Filter by product')
    search_parser.add_argument('--tags', help='Filter by tags')
    search_parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed results')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all knowledge')
    list_parser.add_argument('--categories', nargs='+', help='Filter by categories (space-separated)')
    list_parser.add_argument('--limit', type=int, default=20, help='Limit results')
    list_parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed results')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show specific knowledge')
    show_parser.add_argument('id', type=int, help='Knowledge ID')
    
    # Use command
    use_parser = subparsers.add_parser('use', help='Mark knowledge as used')
    use_parser.add_argument('id', type=int, help='Knowledge ID')
    use_parser.add_argument('--helpful', type=bool, help='Was it helpful?')
    use_parser.add_argument('--notes', help='Usage notes')
    
    # Stats command
    subparsers.add_parser('stats', help='Show knowledge base statistics')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export knowledge to JSON')
    export_parser.add_argument('file', help='Output file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    db = KnowledgeDB()
    
    if args.command == 'add':
        tags = args.tags.split(',') if args.tags else None
        knowledge_uuid = db.add_knowledge(
            title=args.title,
            problem=args.problem,
            solution=args.solution,
            categories=args.categories,
            shopify_product=args.product,
            api_version=args.api_version,
            code_examples=args.code,
            tags=tags,
            notes=args.notes
        )
        print(f"✅ Knowledge added successfully! UUID: {knowledge_uuid}")
    
    elif args.command == 'search':
        tags = args.tags.split(',') if args.tags else None
        results = db.search_knowledge(
            query=args.query,
            categories=args.categories,
            shopify_product=args.product,
            tags=tags
        )
        
        if not results:
            print("No knowledge found matching your criteria.")
        else:
            print(f"Found {len(results)} knowledge entries:")
            for knowledge in results:
                print_knowledge(knowledge, detailed=args.detailed)
    
    elif args.command == 'list':
        results = db.search_knowledge(
            categories=args.categories,
            limit=args.limit
        )
        
        if not results:
            print("No knowledge entries found.")
        else:
            print(f"Showing {len(results)} knowledge entries:")
            for knowledge in results:
                print_knowledge(knowledge, detailed=args.detailed)
    
    elif args.command == 'show':
        knowledge = db.get_knowledge(knowledge_id=args.id)
        if knowledge:
            print_knowledge(knowledge, detailed=True)
        else:
            print(f"Knowledge with ID {args.id} not found.")
    
    elif args.command == 'use':
        db.record_usage(args.id, helpful=args.helpful, notes=args.notes)
        print(f"✅ Usage recorded for knowledge ID {args.id}")
    
    elif args.command == 'stats':
        stats = db.get_stats()
        print(f"\n📊 Knowledge Base Statistics")
        print(f"   Total entries: {stats['total_count']}")
        print(f"   Recent additions (7 days): {stats['recent_additions']}")
        
        print(f"\n📂 Categories:")
        for category, count in stats['categories'].items():
            print(f"   {category}: {count}")
        
        print(f"\n🔥 Most Used:")
        for title, usage_count in stats['most_used']:
            print(f"   {title}: {usage_count} times")
    
    elif args.command == 'export':
        db.export_knowledge(args.file)
        print(f"✅ Knowledge exported to {args.file}")

if __name__ == '__main__':
    main()
