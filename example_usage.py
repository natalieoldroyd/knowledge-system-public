#!/usr/bin/env python3
"""
Example usage of the Knowledge System with multiple categories
"""

from knowledge import KnowledgeDB

def add_example_knowledge():
    """Add some example knowledge entries with multiple categories."""
    db = KnowledgeDB()
    
    # Example 1: Issue that spans multiple APIs
    db.add_knowledge(
        title="Webhook delivery failing for bulk operation completions",
        problem="Customer complaining that webhook notifications for bulk_operations/complete aren't being received after bulk product updates",
        solution="""1. Check webhook subscription exists for bulk_operations/finish topic
2. Verify webhook endpoint URL is publicly accessible (test with curl)
3. Check webhook endpoint returns 200 status within 5 seconds
4. Validate webhook payload signature using HMAC-SHA256
5. If still failing, check if bulk operation actually completed successfully via GraphQL query""",
        categories=["webhooks", "bulk-operations", "products-api"],
        shopify_product="Admin API",
        api_version="2025-07",
        code_examples="""# Check bulk operation status
query = '''
query getBulkOperation($id: ID!) {
  node(id: $id) {
    ... on BulkOperation {
      id
      status
      errorCode
      createdAt
      completedAt
      url
    }
  }
}
'''

# Verify webhook signature
import hmac
import hashlib
import base64

def verify_webhook(data, signature, secret):
    computed_hmac = base64.b64encode(
        hmac.new(secret.encode(), data.encode(), hashlib.sha256).digest()
    )
    return hmac.compare_digest(computed_hmac, signature.encode())""",
        tags=["webhook-delivery", "bulk-operations", "signature-verification", "troubleshooting"],
        notes="This issue often occurs when customers use bulk operations but don't properly handle the async nature of the process."
    )
    
    # Example 2: Orders API with fulfillments
    db.add_knowledge(
        title="Cannot create fulfillment - Location not found error",
        problem="Getting 'Location not found' error when trying to create fulfillment via Orders API, even though location exists in admin",
        solution="""1. Verify the location ID being used in the fulfillment request
2. Check that the location is enabled and active
3. Ensure the location has inventory for the line items being fulfilled
4. Verify app has fulfillment_orders access scope
5. Use fulfillment_orders endpoint instead of legacy fulfillments endpoint for better reliability""",
        categories=["orders-api", "fulfillments-api"],
        shopify_product="Admin API",
        api_version="2025-07",
        code_examples="""# Correct way to create fulfillment
mutation fulfillmentCreateV2($fulfillment: FulfillmentV2Input!) {
  fulfillmentCreateV2(fulfillment: $fulfillment) {
    fulfillment {
      id
      status
      trackingInfo {
        number
        url
      }
    }
    userErrors {
      field
      message
    }
  }
}

# Check location status first
query getLocations {
  locations(first: 50) {
    edges {
      node {
        id
        name
        isActive
        fulfillsOnlineOrders
      }
    }
  }
}""",
        tags=["fulfillment-errors", "location-validation", "orders", "scope-issues"],
        notes="Migration from legacy fulfillments to fulfillment_orders is ongoing - recommend new approach."
    )
    
    # Example 3: App configuration with billing
    db.add_knowledge(
        title="App subscription upgrade failing silently",
        problem="Customer trying to upgrade app subscription but charge isn't being created and no error returned",
        solution="""1. Check if existing subscription is properly cancelled first
2. Verify shop is eligible for the subscription plan (some plans have restrictions)
3. Ensure app is using correct AppSubscriptionCreate mutation format
4. Check if shop has payment method configured
5. Verify app has correct billing scopes (write_payment_terms)""",
        categories=["app-billing", "app-configuration"],
        shopify_product="Partner API",
        api_version="2025-07",
        code_examples="""# Proper subscription upgrade flow
# 1. Cancel existing subscription
mutation appSubscriptionCancel($id: ID!) {
  appSubscriptionCancel(id: $id) {
    appSubscription {
      id
      status
    }
    userErrors {
      field
      message
    }
  }
}

# 2. Create new subscription
mutation appSubscriptionCreate($subscription: AppSubscriptionInput!) {
  appSubscriptionCreate(subscription: $subscription) {
    appSubscription {
      id
      status
    }
    confirmationUrl
    userErrors {
      field
      message
    }
  }
}""",
        tags=["billing-issues", "subscription-upgrade", "partner-api", "payment-methods"],
        notes="Always cancel existing subscription before creating new one to avoid conflicts."
    )
    
    print("✅ Added 3 example knowledge entries with multiple categories!")

def demonstrate_search():
    """Show different ways to search across categories."""
    db = KnowledgeDB()
    
    print("\n🔍 Search Examples:")
    
    # Search by single category
    print("\n1. All webhook-related knowledge:")
    results = db.search_knowledge(categories=["webhooks"])
    for r in results:
        print(f"   - {r['title']}")
    
    # Search by multiple categories
    print("\n2. Knowledge related to both orders and fulfillments:")
    results = db.search_knowledge(categories=["orders-api", "fulfillments-api"])
    for r in results:
        print(f"   - {r['title']}")
    
    # Text search across all categories
    print("\n3. Search for 'subscription' across all categories:")
    results = db.search_knowledge(query="subscription")
    for r in results:
        print(f"   - {r['title']}")
    
    # Combined search
    print("\n4. Search for 'error' in webhook category:")
    results = db.search_knowledge(query="error", categories=["webhooks"])
    for r in results:
        print(f"   - {r['title']}")

def show_stats():
    """Show category statistics."""
    db = KnowledgeDB()
    stats = db.get_stats()
    
    print("\n📊 Knowledge Base Statistics:")
    print(f"Total entries: {stats['total_count']}")
    print(f"Recent additions: {stats['recent_additions']}")
    
    print("\nKnowledge by category:")
    for category, count in stats['categories'].items():
        print(f"   {category}: {count}")

if __name__ == '__main__':
    add_example_knowledge()
    demonstrate_search()
    show_stats()


