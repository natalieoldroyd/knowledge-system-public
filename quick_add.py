#!/usr/bin/env python3
"""
Quick and easy way to add knowledge without command line parsing issues
"""

from knowledge import KnowledgeDB

def quick_add():
    """Interactive knowledge entry."""
    db = KnowledgeDB()
    
    print("🚀 Quick Knowledge Entry")
    print("=" * 40)
    
    # Get basic info
    title = input("📝 Issue Title: ")
    problem = input("❗ Problem Description: ")
    solution = input("✅ Solution: ")
    
    # Get categories
    print("\n📂 Available Categories:")
    categories_list = [
        "app-proxy", "orders-api", "returns-api", "fulfillments-api", 
        "products-api", "shopify-cli", "webhooks", "payments-api", 
        "multipass", "customer-account-api", "bulk-operations", 
        "media-api", "app-billing", "app-configuration", 
        "oxygen-api", "storefront-api", "admin-api", "general"
    ]
    
    for i, cat in enumerate(categories_list, 1):
        print(f"{i:2d}. {cat}")
    
    cat_input = input("\n🏷️  Enter category numbers (space-separated, e.g., '1 7 15'): ")
    
    try:
        cat_indices = [int(x) - 1 for x in cat_input.split()]
        selected_categories = [categories_list[i] for i in cat_indices if 0 <= i < len(categories_list)]
    except:
        selected_categories = ["general"]
        print("Invalid category selection, using 'general'")
    
    # Optional fields
    product = input("🛠️  Shopify Product (optional): ") or None
    api_version = input("🔢 API Version (optional, e.g., 2025-07): ") or None
    code = input("💻 Code Examples (optional): ") or None
    tags_input = input("🏷️  Tags (comma-separated, optional): ")
    tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else None
    notes = input("📋 Notes (optional): ") or None
    
    # Add to database
    try:
        uuid = db.add_knowledge(
            title=title,
            problem=problem,
            solution=solution,
            categories=selected_categories,
            shopify_product=product,
            api_version=api_version,
            code_examples=code,
            tags=tags,
            notes=notes,
            source="interactive"
        )
        
        print(f"\n✅ Knowledge added successfully!")
        print(f"   UUID: {uuid}")
        print(f"   Categories: {', '.join(selected_categories)}")
        
    except Exception as e:
        print(f"\n❌ Error adding knowledge: {e}")

if __name__ == '__main__':
    quick_add()


