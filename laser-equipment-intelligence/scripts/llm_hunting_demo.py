#!/usr/bin/env python3
"""
LLM Hunting Demo Script
Demonstrates the Clay.com-style LLM-driven hunting capabilities
"""

import os
import sys
import json
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from laser_intelligence.ai.hunting_orchestrator import HuntingOrchestrator


def main():
    """Main demo function"""
    print("🤖 LLM-Driven Laser Equipment Hunting Demo")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ Error: GROQ_API_KEY environment variable not set")
        print("Please set your Groq API key:")
        print("export GROQ_API_KEY='your_api_key_here'")
        return
    
    # Initialize hunting orchestrator
    print("🚀 Initializing LLM Hunting System...")
    orchestrator = HuntingOrchestrator(api_key)
    
    # Show available strategies
    strategies = orchestrator.get_hunting_strategies()
    print(f"📋 Available hunting strategies: {', '.join(strategies)}")
    
    # Demo different hunting strategies
    demo_strategies = [
        ('discovery', 'Source Discovery Hunt'),
        ('targeted', 'Targeted Brand Hunt'),
        ('high_value', 'High-Value Equipment Hunt'),
        ('auction_focused', 'Auction-Focused Hunt')
    ]
    
    for strategy, description in demo_strategies:
        print(f"\n🎯 Running {description}...")
        print("-" * 40)
        
        try:
            # Run hunting session
            session = orchestrator.hunt_laser_equipment(
                strategy=strategy,
                search_terms=['sciton', 'cynosure', 'cutera', 'laser equipment'],
                geographic_scope=['United States'],
                max_sources=10,
                max_listings_per_source=20,
                min_confidence=0.6
            )
            
            # Display results
            print(f"✅ Session completed in {session.total_processing_time:.1f} seconds")
            print(f"📊 Sources discovered: {len(session.discovered_sources)}")
            print(f"📦 Listings extracted: {len(session.extracted_listings)}")
            print(f"🎯 Success rate: {session.success_rate:.1%}")
            print(f"🔍 Confidence score: {session.confidence_score:.2f}")
            
            # Show top discovered sources
            if session.discovered_sources:
                print("\n🔍 Top Discovered Sources:")
                for i, source in enumerate(session.discovered_sources[:5], 1):
                    print(f"  {i}. {source.name} ({source.source_type})")
                    print(f"     URL: {source.url}")
                    print(f"     Confidence: {source.confidence:.2f}")
                    print(f"     Estimated listings: {source.estimated_listings}")
                    print()
            
            # Show top extracted listings
            if session.extracted_listings:
                print("📦 Top Extracted Listings:")
                for i, listing in enumerate(session.extracted_listings[:3], 1):
                    title = listing.get('title_raw', 'No title')[:60]
                    brand = listing.get('brand', 'Unknown')
                    model = listing.get('model', 'Unknown')
                    price = listing.get('asking_price', 0)
                    condition = listing.get('condition', 'Unknown')
                    
                    print(f"  {i}. {title}...")
                    print(f"     Brand: {brand}, Model: {model}")
                    print(f"     Price: ${price:,.0f}, Condition: {condition}")
                    print(f"     Source: {listing.get('source_url', 'Unknown')}")
                    print()
            
            # Generate summary
            summary = orchestrator.get_session_summary(session)
            print("📋 Session Summary:")
            print(summary)
            
        except Exception as e:
            print(f"❌ Error running {strategy} hunt: {e}")
        
        print("\n" + "="*50)
        
        # Pause between strategies
        if strategy != demo_strategies[-1][0]:
            print("⏳ Waiting 5 seconds before next strategy...")
            time.sleep(5)
    
    print("\n🎉 LLM Hunting Demo Complete!")
    print("\nKey Benefits of LLM-Driven Hunting:")
    print("✅ Discovers new sources automatically")
    print("✅ Adapts to any website structure")
    print("✅ No need for pre-built scrapers")
    print("✅ Handles complex JavaScript sites")
    print("✅ Extracts structured data from unstructured content")
    print("✅ Learns and improves over time")


def interactive_demo():
    """Interactive demo mode"""
    print("🤖 Interactive LLM Hunting Demo")
    print("=" * 40)
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ Error: GROQ_API_KEY environment variable not set")
        return
    
    orchestrator = HuntingOrchestrator(api_key)
    
    while True:
        print("\nChoose a hunting strategy:")
        strategies = orchestrator.get_hunting_strategies()
        for i, strategy in enumerate(strategies, 1):
            print(f"  {i}. {strategy}")
        print("  0. Exit")
        
        try:
            choice = int(input("\nEnter choice (0-{}): ".format(len(strategies))))
            if choice == 0:
                break
            elif 1 <= choice <= len(strategies):
                strategy = strategies[choice - 1]
                
                # Get search terms
                search_input = input("Enter search terms (comma-separated): ")
                search_terms = [term.strip() for term in search_input.split(',')] if search_input else None
                
                # Get geographic scope
                geo_input = input("Enter geographic scope (comma-separated): ")
                geographic_scope = [geo.strip() for geo in geo_input.split(',')] if geo_input else None
                
                print(f"\n🎯 Running {strategy} hunt...")
                
                session = orchestrator.hunt_laser_equipment(
                    strategy=strategy,
                    search_terms=search_terms,
                    geographic_scope=geographic_scope,
                    max_sources=20,
                    max_listings_per_source=30,
                    min_confidence=0.6
                )
                
                print(orchestrator.get_session_summary(session))
                
            else:
                print("Invalid choice. Please try again.")
                
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        main()
