"""
Seed script to populate the plans collection with pricing tiers
Run this script once to initialize the pricing plans in MongoDB
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017").strip("'\" ")
DB_NAME = os.getenv("DB_NAME", "visual_engine").strip("'\" ")

def seed_plans():
    """Seed the plans collection with pricing data"""
    try:
        client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client[DB_NAME]
        plans_collection = db["plans"]
        
        # Clear existing plans
        plans_collection.delete_many({})
        
        # Pricing plans based on the provided image
        plans = [
            {
                "name": "Starter",
                "price": 159.0,
                "includedUnits": 1000,
                "costPerUnit": 0.795,
                "bestFor": "Startups & Initial Testing",
                "features": [
                    "50 Image Units",
                    "ADA Compliance Layer",
                    "Visual Accessibility Scan",
                    "Standard AI Resizing",
                    "Backend Integration Support",
                    "Real-time Usage Monitoring"
                ],
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "name": "Growth",
                "price": 429.0,
                "includedUnits": 3000,
                "costPerUnit": 0.143,
                "bestFor": "Active Marketing Agencies",
                "features": [
                    "3,000 Image Units",
                    "All Starter Features",
                    "Priority API Access",
                    "Intelligent Element Spacing",
                    "Advanced AI Resizing",
                    "Dedicated Support"
                ],
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "name": "Scale",
                "price": 649.0,
                "includedUnits": 5000,
                "costPerUnit": 0.130,
                "bestFor": "Global Signage Networks",
                "features": [
                    "5,000 Image Units",
                    "All Growth Features",
                    "Dedicated Infrastructure",
                    "Custom AI Model Tuning",
                    "Compliance Analysis Reports",
                    "24/7 Premium Support"
                ],
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
        ]
        
        # Insert plans
        result = plans_collection.insert_many(plans)
        print(f"✅ Successfully seeded {len(result.inserted_ids)} pricing plans")
        
        # Display seeded plans
        for plan in plans:
            print(f"\n📦 {plan['name']} Plan:")
            print(f"   Price: ${plan['price']}/month")
            print(f"   Units: {plan['includedUnits']:,}")
            print(f"   Cost per unit: ${plan['costPerUnit']}")
            print(f"   Best for: {plan['bestFor']}")
        
        print("\n✨ Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding plans: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    seed_plans()
