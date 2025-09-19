#!/usr/bin/env python3
"""
Test script for the Laser Equipment Intelligence API
"""
import asyncio
import asyncpg
import os
from api.models.database import init_db

async def test_database_connection():
    """Test database connection and initialization"""
    try:
        print("Testing database connection...")
        await init_db()
        print("✅ Database connection successful")
        
        # Test inserting sample data
        conn = await asyncpg.connect(os.getenv("DATABASE_URL", "postgresql://localhost/laser_intelligence"))
        
        # Insert sample listing
        await conn.execute("""
            INSERT INTO listings (title, brand, model, condition, price, source, location, description, score_overall)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT DO NOTHING
        """, 
        "Test Sciton Joule Laser System",
        "Sciton", 
        "Joule",
        "excellent",
        85000,
        "test_source",
        "Test Location",
        "Test description for API validation",
        85
        )
        
        # Test query
        rows = await conn.fetch("SELECT COUNT(*) FROM listings")
        print(f"✅ Database contains {rows[0]['count']} listings")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing Laser Equipment Intelligence API")
    print("=" * 50)
    
    # Test database
    db_success = await test_database_connection()
    
    print("\n" + "=" * 50)
    if db_success:
        print("🎉 All tests passed! API is ready for deployment.")
    else:
        print("❌ Some tests failed. Please check the configuration.")
    
    return db_success

if __name__ == "__main__":
    asyncio.run(main())
