"""
Multi-LLM provider support for the hunting system
Supports Groq, OpenAI, Anthropic, and other providers
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers"""
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    TOGETHER = "together"


@dataclass
class LLMConfig:
    """Configuration for LLM provider"""
    provider: LLMProvider
    api_url: str
    model: str
    api_key: str
    max_tokens: int = 4000
    temperature: float = 0.1
    timeout: int = 60


class LLMProviderManager:
    """Manages multiple LLM providers with fallback support"""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.primary_provider = LLMProvider.GROQ
        self.fallback_providers = [LLMProvider.OPENAI, LLMProvider.ANTHROPIC]
    
    def _initialize_providers(self) -> Dict[LLMProvider, LLMConfig]:
        """Initialize all available LLM providers"""
        providers = {}
        
        # Groq (Primary - Fast & Cost-effective)
        if os.getenv('GROQ_API_KEY'):
            providers[LLMProvider.GROQ] = LLMConfig(
                provider=LLMProvider.GROQ,
                api_url="https://api.groq.com/openai/v1/chat/completions",
                model="llama-3.1-70b-versatile",
                api_key=os.getenv('GROQ_API_KEY'),
                max_tokens=4000,
                temperature=0.1,
                timeout=60
            )
        
        # OpenAI (Fallback - High Quality)
        if os.getenv('OPENAI_API_KEY'):
            providers[LLMProvider.OPENAI] = LLMConfig(
                provider=LLMProvider.OPENAI,
                api_url="https://api.openai.com/v1/chat/completions",
                model="gpt-4o-mini",  # Cost-effective but high quality
                api_key=os.getenv('OPENAI_API_KEY'),
                max_tokens=4000,
                temperature=0.1,
                timeout=60
            )
        
        # Anthropic (Fallback - Excellent for structured data)
        if os.getenv('ANTHROPIC_API_KEY'):
            providers[LLMProvider.ANTHROPIC] = LLMConfig(
                provider=LLMProvider.ANTHROPIC,
                api_url="https://api.anthropic.com/v1/messages",
                model="claude-3-haiku-20240307",  # Fast and cost-effective
                api_key=os.getenv('ANTHROPIC_API_KEY'),
                max_tokens=4000,
                temperature=0.1,
                timeout=60
            )
        
        # Cohere (Alternative)
        if os.getenv('COHERE_API_KEY'):
            providers[LLMProvider.COHERE] = LLMConfig(
                provider=LLMProvider.COHERE,
                api_url="https://api.cohere.ai/v1/chat",
                model="command-r-plus",
                api_key=os.getenv('COHERE_API_KEY'),
                max_tokens=4000,
                temperature=0.1,
                timeout=60
            )
        
        # Together AI (Alternative)
        if os.getenv('TOGETHER_API_KEY'):
            providers[LLMProvider.TOGETHER] = LLMConfig(
                provider=LLMProvider.TOGETHER,
                api_url="https://api.together.xyz/v1/chat/completions",
                model="meta-llama/Llama-3.1-70B-Instruct-Turbo",
                api_key=os.getenv('TOGETHER_API_KEY'),
                max_tokens=4000,
                temperature=0.1,
                timeout=60
            )
        
        return providers
    
    def get_provider_config(self, provider: LLMProvider) -> Optional[LLMConfig]:
        """Get configuration for a specific provider"""
        return self.providers.get(provider)
    
    def get_available_providers(self) -> list[LLMProvider]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def get_primary_config(self) -> Optional[LLMConfig]:
        """Get primary provider configuration"""
        return self.providers.get(self.primary_provider)
    
    def get_fallback_configs(self) -> list[LLMConfig]:
        """Get fallback provider configurations"""
        return [self.providers[provider] for provider in self.fallback_providers if provider in self.providers]
    
    def get_best_provider_for_task(self, task_type: str) -> Optional[LLMConfig]:
        """Get the best provider for a specific task type"""
        
        task_preferences = {
            'source_discovery': LLMProvider.GROQ,  # Fast for web search
            'data_extraction': LLMProvider.OPENAI,  # High accuracy for structured data
            'content_analysis': LLMProvider.ANTHROPIC,  # Excellent for analysis
            'general': LLMProvider.GROQ  # Default to fastest
        }
        
        preferred_provider = task_preferences.get(task_type, LLMProvider.GROQ)
        
        # Return preferred provider if available, otherwise primary
        if preferred_provider in self.providers:
            return self.providers[preferred_provider]
        elif self.primary_provider in self.providers:
            return self.providers[self.primary_provider]
        else:
            # Return any available provider
            return next(iter(self.providers.values())) if self.providers else None
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics about available providers"""
        stats = {
            'total_providers': len(self.providers),
            'available_providers': [p.value for p in self.providers.keys()],
            'primary_provider': self.primary_provider.value,
            'fallback_providers': [p.value for p in self.fallback_providers if p in self.providers],
            'provider_details': {}
        }
        
        for provider, config in self.providers.items():
            stats['provider_details'][provider.value] = {
                'model': config.model,
                'max_tokens': config.max_tokens,
                'temperature': config.temperature,
                'timeout': config.timeout
            }
        
        return stats


# Global provider manager instance
provider_manager = LLMProviderManager()


def get_llm_config(provider: LLMProvider = None, task_type: str = 'general') -> Optional[LLMConfig]:
    """Get LLM configuration for a provider or task type"""
    if provider:
        return provider_manager.get_provider_config(provider)
    else:
        return provider_manager.get_best_provider_for_task(task_type)


def get_available_providers() -> list[str]:
    """Get list of available provider names"""
    return [p.value for p in provider_manager.get_available_providers()]


def get_provider_stats() -> Dict[str, Any]:
    """Get provider statistics"""
    return provider_manager.get_provider_stats()


# Example usage and configuration
if __name__ == "__main__":
    print("🤖 LLM Provider Configuration")
    print("=" * 40)
    
    stats = get_provider_stats()
    print(f"Total providers: {stats['total_providers']}")
    print(f"Available: {', '.join(stats['available_providers'])}")
    print(f"Primary: {stats['primary_provider']}")
    print(f"Fallbacks: {', '.join(stats['fallback_providers'])}")
    
    print("\nProvider Details:")
    for provider, details in stats['provider_details'].items():
        print(f"  {provider}: {details['model']} (max_tokens: {details['max_tokens']})")
    
    print("\nTask-Specific Recommendations:")
    tasks = ['source_discovery', 'data_extraction', 'content_analysis', 'general']
    for task in tasks:
        config = get_llm_config(task_type=task)
        if config:
            print(f"  {task}: {config.provider.value} ({config.model})")
