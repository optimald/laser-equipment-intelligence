#!/usr/bin/env python3
"""
LLM Provider Demo Script
Demonstrates multi-provider LLM configuration and usage
"""

import os
import sys
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from laser_intelligence.ai.llm_providers import (
    LLMProvider, LLMConfig, LLMProviderManager,
    get_llm_config, get_available_providers, get_provider_stats
)


def demo_provider_configuration():
    """Demonstrate provider configuration"""
    print("🤖 LLM Provider Configuration Demo")
    print("=" * 50)
    
    # Show current configuration
    stats = get_provider_stats()
    print(f"Total providers: {stats['total_providers']}")
    print(f"Available: {', '.join(stats['available_providers']) if stats['available_providers'] else 'None (no API keys set)'}")
    print(f"Primary: {stats['primary_provider']}")
    print(f"Fallbacks: {', '.join(stats['fallback_providers']) if stats['fallback_providers'] else 'None'}")
    
    print("\n📋 Provider Details:")
    if stats['provider_details']:
        for provider, details in stats['provider_details'].items():
            print(f"  {provider}: {details['model']} (max_tokens: {details['max_tokens']})")
    else:
        print("  No providers configured (set API keys to enable)")
    
    print("\n🎯 Task-Specific Recommendations:")
    tasks = ['source_discovery', 'data_extraction', 'content_analysis', 'general']
    for task in tasks:
        config = get_llm_config(task_type=task)
        if config:
            print(f"  {task}: {config.provider.value} ({config.model})")
        else:
            print(f"  {task}: No provider available")
    
    return stats


def demo_provider_setup():
    """Demonstrate how to set up providers"""
    print("\n🔧 Provider Setup Instructions")
    print("=" * 40)
    
    providers = [
        {
            'name': 'Groq',
            'env_var': 'GROQ_API_KEY',
            'model': 'llama-3.1-70b-versatile',
            'speed': '⚡⚡⚡',
            'cost': '💰',
            'quality': '🧠🧠🧠',
            'best_for': 'General hunting, source discovery'
        },
        {
            'name': 'OpenAI',
            'env_var': 'OPENAI_API_KEY',
            'model': 'gpt-4o-mini',
            'speed': '⚡⚡',
            'cost': '💰💰',
            'quality': '🧠🧠🧠🧠',
            'best_for': 'Data extraction, structured output'
        },
        {
            'name': 'Anthropic',
            'env_var': 'ANTHROPIC_API_KEY',
            'model': 'claude-3-haiku-20240307',
            'speed': '⚡⚡',
            'cost': '💰💰',
            'quality': '🧠🧠🧠🧠',
            'best_for': 'Content analysis, complex reasoning'
        },
        {
            'name': 'Cohere',
            'env_var': 'COHERE_API_KEY',
            'model': 'command-r-plus',
            'speed': '⚡⚡',
            'cost': '💰💰',
            'quality': '🧠🧠🧠',
            'best_for': 'Alternative option'
        },
        {
            'name': 'Together AI',
            'env_var': 'TOGETHER_API_KEY',
            'model': 'meta-llama/Llama-3.1-70B-Instruct-Turbo',
            'speed': '⚡⚡⚡',
            'cost': '💰',
            'quality': '🧠🧠🧠',
            'best_for': 'Cost-effective alternative'
        }
    ]
    
    print("To enable providers, set these environment variables:")
    print()
    
    for provider in providers:
        print(f"🔹 {provider['name']}")
        print(f"   Model: {provider['model']}")
        print(f"   Speed: {provider['speed']} | Cost: {provider['cost']} | Quality: {provider['quality']}")
        print(f"   Best for: {provider['best_for']}")
        print(f"   Set: export {provider['env_var']}='your_api_key_here'")
        print()
    
    print("Example setup:")
    print("export GROQ_API_KEY='gsk_...'")
    print("export OPENAI_API_KEY='sk-...'")
    print("export ANTHROPIC_API_KEY='sk-ant-...'")
    print()


def demo_usage_examples():
    """Demonstrate usage examples"""
    print("🚀 Usage Examples")
    print("=" * 30)
    
    examples = [
        {
            'title': 'Default Configuration (Groq)',
            'code': '''
from laser_intelligence.ai.hunting_orchestrator import HuntingOrchestrator

# Uses Groq by default (fastest, most cost-effective)
orchestrator = HuntingOrchestrator()
session = orchestrator.hunt_laser_equipment(strategy='comprehensive')
'''
        },
        {
            'title': 'Specific Provider Selection',
            'code': '''
# Use OpenAI for high-accuracy extraction
orchestrator = HuntingOrchestrator(provider='openai')
session = orchestrator.hunt_laser_equipment(strategy='targeted')

# Use Anthropic for complex analysis
orchestrator = HuntingOrchestrator(provider='anthropic')
session = orchestrator.hunt_laser_equipment(strategy='high_value')
'''
        },
        {
            'title': 'Task-Specific Provider Selection',
            'code': '''
from laser_intelligence.ai.llm_providers import get_llm_config

# Automatically selects best provider for each task
discovery_config = get_llm_config(task_type='source_discovery')  # → Groq
extraction_config = get_llm_config(task_type='data_extraction')  # → OpenAI
analysis_config = get_llm_config(task_type='content_analysis')   # → Anthropic
'''
        },
        {
            'title': 'Provider Statistics',
            'code': '''
from laser_intelligence.ai.llm_providers import get_provider_stats

stats = get_provider_stats()
print(f"Available providers: {stats['available_providers']}")
print(f"Primary: {stats['primary_provider']}")
print(f"Fallbacks: {stats['fallback_providers']}")
'''
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['title']}")
        print(example['code'])
        print()


def demo_performance_comparison():
    """Demonstrate performance comparison"""
    print("📊 Performance Comparison")
    print("=" * 35)
    
    comparison = {
        'Groq Llama-3.1-70b': {
            'speed': '⚡⚡⚡ (0.5-1.0s)',
            'cost': '💰 ($1.38/1M tokens)',
            'quality': '🧠🧠🧠 (Good)',
            'throughput': '2000+ tokens/sec',
            'concurrent': '100+ requests',
            'best_for': 'High-volume hunting, source discovery'
        },
        'OpenAI GPT-4o-mini': {
            'speed': '⚡⚡ (2-4s)',
            'cost': '💰💰 ($0.75/1M tokens)',
            'quality': '🧠🧠🧠🧠 (Excellent)',
            'throughput': '500-800 tokens/sec',
            'concurrent': '20-50 requests',
            'best_for': 'Data extraction, structured output'
        },
        'Anthropic Claude-3-haiku': {
            'speed': '⚡⚡ (3-5s)',
            'cost': '💰💰 ($1.50/1M tokens)',
            'quality': '🧠🧠🧠🧠 (Excellent)',
            'throughput': '400-600 tokens/sec',
            'concurrent': '10-30 requests',
            'best_for': 'Content analysis, complex reasoning'
        }
    }
    
    for provider, metrics in comparison.items():
        print(f"🔹 {provider}")
        for metric, value in metrics.items():
            print(f"   {metric.replace('_', ' ').title()}: {value}")
        print()


def demo_recommendations():
    """Provide recommendations for different use cases"""
    print("🎯 Recommendations by Use Case")
    print("=" * 40)
    
    recommendations = [
        {
            'use_case': 'High-Volume Production',
            'provider': 'Groq',
            'reason': 'Fastest and most cost-effective for large-scale operations',
            'config': 'provider="groq"'
        },
        {
            'use_case': 'High-Accuracy Extraction',
            'provider': 'OpenAI',
            'reason': 'Best structured data extraction and JSON output',
            'config': 'provider="openai"'
        },
        {
            'use_case': 'Complex Analysis',
            'provider': 'Anthropic',
            'reason': 'Superior reasoning and content analysis capabilities',
            'config': 'provider="anthropic"'
        },
        {
            'use_case': 'Development/Testing',
            'provider': 'Groq',
            'reason': 'Fast iteration and low cost for development',
            'config': 'provider="groq"'
        },
        {
            'use_case': 'Balanced Production',
            'provider': 'OpenAI',
            'reason': 'Good balance of speed, cost, and quality',
            'config': 'provider="openai"'
        }
    ]
    
    for rec in recommendations:
        print(f"🔹 {rec['use_case']}")
        print(f"   Provider: {rec['provider']}")
        print(f"   Reason: {rec['reason']}")
        print(f"   Config: {rec['config']}")
        print()


def main():
    """Main demo function"""
    print("🤖 LLM Multi-Provider System Demo")
    print("=" * 50)
    
    # Run all demos
    demo_provider_configuration()
    demo_provider_setup()
    demo_usage_examples()
    demo_performance_comparison()
    demo_recommendations()
    
    print("🎉 Demo Complete!")
    print("\nNext Steps:")
    print("1. Set up API keys for your preferred providers")
    print("2. Run the hunting demo: python scripts/llm_hunting_demo.py")
    print("3. Experiment with different providers for your use case")
    print("4. Monitor performance and costs in production")


if __name__ == "__main__":
    main()
