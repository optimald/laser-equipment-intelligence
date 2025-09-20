# 🤖 LLM Configuration Guide

**Multi-Provider LLM Support for Laser Equipment Hunting**

This guide explains how to configure and use multiple LLM providers in our hunting system.

## 🎯 Current LLM Setup

### **Primary LLM: Groq Llama-3.1-70b-versatile**

**Why Groq?**
- ⚡ **Speed**: 3-5x faster than OpenAI/Anthropic
- 💰 **Cost**: ~90% cheaper than GPT-4
- 🧠 **Quality**: Excellent for structured data extraction
- 🔄 **Throughput**: High concurrent request support

**Configuration:**
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

### **Supported Providers**

| Provider | Model | Speed | Cost | Quality | Best For |
|----------|-------|-------|------|---------|----------|
| **Groq** | Llama-3.1-70b | ⚡⚡⚡ | 💰 | 🧠🧠🧠 | General hunting |
| **OpenAI** | GPT-4o-mini | ⚡⚡ | 💰💰 | 🧠🧠🧠🧠 | Data extraction |
| **Anthropic** | Claude-3-haiku | ⚡⚡ | 💰💰 | 🧠🧠🧠🧠 | Content analysis |
| **Cohere** | Command-r-plus | ⚡⚡ | 💰💰 | 🧠🧠🧠 | Alternative option |
| **Together** | Llama-3.1-70b | ⚡⚡⚡ | 💰 | 🧠🧠🧠 | Cost-effective |

## 🔧 Configuration Options

### **Environment Variables**

```bash
# Primary provider (Groq)
export GROQ_API_KEY="your_groq_api_key"

# Fallback providers
export OPENAI_API_KEY="your_openai_api_key"
export ANTHROPIC_API_KEY="your_anthropic_api_key"
export COHERE_API_KEY="your_cohere_api_key"
export TOGETHER_API_KEY="your_together_api_key"
```

### **Provider Selection**

```python
from laser_intelligence.ai.hunting_orchestrator import HuntingOrchestrator

# Use default provider (Groq)
orchestrator = HuntingOrchestrator()

# Use specific provider
orchestrator = HuntingOrchestrator(provider='openai')

# Use provider for specific task
orchestrator = HuntingOrchestrator(provider='anthropic')  # Better for analysis
```

### **Task-Specific Provider Selection**

The system automatically selects the best provider for each task:

```python
# Source discovery - Uses Groq (fastest)
discovery_config = get_llm_config(task_type='source_discovery')

# Data extraction - Uses OpenAI (most accurate)
extraction_config = get_llm_config(task_type='data_extraction')

# Content analysis - Uses Anthropic (best analysis)
analysis_config = get_llm_config(task_type='content_analysis')
```

## 🚀 Usage Examples

### **Basic Configuration**

```python
from laser_intelligence.ai.hunting_orchestrator import HuntingOrchestrator

# Default: Uses Groq Llama-3.1-70b
orchestrator = HuntingOrchestrator()

# Run hunt with default provider
session = orchestrator.hunt_laser_equipment(strategy='comprehensive')
```

### **Provider-Specific Configuration**

```python
# Use OpenAI for high-accuracy extraction
orchestrator = HuntingOrchestrator(provider='openai')
session = orchestrator.hunt_laser_equipment(strategy='targeted')

# Use Anthropic for complex analysis
orchestrator = HuntingOrchestrator(provider='anthropic')
session = orchestrator.hunt_laser_equipment(strategy='high_value')
```

### **Multi-Provider with Fallback**

```python
from laser_intelligence.ai.llm_providers import provider_manager

# Check available providers
available = provider_manager.get_available_providers()
print(f"Available providers: {available}")

# Get provider statistics
stats = provider_manager.get_provider_stats()
print(f"Primary: {stats['primary_provider']}")
print(f"Fallbacks: {stats['fallback_providers']}")
```

## 📊 Performance Comparison

### **Speed Benchmarks**

| Provider | Avg Response Time | Tokens/Second | Concurrent Requests |
|----------|------------------|---------------|-------------------|
| Groq | 0.5-1.0s | 2000+ | 100+ |
| OpenAI | 2-4s | 500-800 | 20-50 |
| Anthropic | 3-5s | 400-600 | 10-30 |
| Cohere | 2-3s | 600-900 | 30-60 |
| Together | 1-2s | 1000-1500 | 50-80 |

### **Cost Comparison (per 1M tokens)**

| Provider | Input Cost | Output Cost | Total Cost |
|----------|------------|-------------|------------|
| Groq | $0.59 | $0.79 | $1.38 |
| OpenAI GPT-4o-mini | $0.15 | $0.60 | $0.75 |
| Anthropic Claude-3-haiku | $0.25 | $1.25 | $1.50 |
| Cohere Command-r-plus | $3.00 | $15.00 | $18.00 |
| Together Llama-3.1-70b | $0.90 | $0.90 | $1.80 |

### **Quality Comparison**

| Provider | Structured Data | Web Search | Analysis | Creativity |
|----------|----------------|------------|----------|------------|
| Groq Llama-3.1-70b | 🧠🧠🧠 | 🧠🧠🧠🧠 | 🧠🧠 | 🧠🧠🧠 |
| OpenAI GPT-4o-mini | 🧠🧠🧠🧠 | 🧠🧠🧠 | 🧠🧠🧠 | 🧠🧠🧠 |
| Anthropic Claude-3-haiku | 🧠🧠🧠 | 🧠🧠🧠 | 🧠🧠🧠🧠 | 🧠🧠🧠 |
| Cohere Command-r-plus | 🧠🧠 | 🧠🧠🧠 | 🧠🧠 | 🧠🧠 |
| Together Llama-3.1-70b | 🧠🧠🧠 | 🧠🧠🧠🧠 | 🧠🧠 | 🧠🧠🧠 |

## 🎯 Recommended Configurations

### **For Production Use**

```python
# High-volume production (cost-optimized)
orchestrator = HuntingOrchestrator(provider='groq')

# High-accuracy production (quality-optimized)
orchestrator = HuntingOrchestrator(provider='openai')

# Balanced production (speed + quality)
orchestrator = HuntingOrchestrator(provider='anthropic')
```

### **For Development/Testing**

```python
# Fast development (Groq)
orchestrator = HuntingOrchestrator(provider='groq')

# Thorough testing (OpenAI)
orchestrator = HuntingOrchestrator(provider='openai')
```

### **For Specific Use Cases**

```python
# Source discovery (fast web search)
discovery_hunter = LLMHunter(provider='groq')

# Data extraction (high accuracy)
extractor = AdaptiveExtractor(provider='openai')

# Content analysis (best reasoning)
analyzer = LLMHunter(provider='anthropic')
```

## 🔄 Fallback Strategy

The system automatically falls back to alternative providers if the primary fails:

```python
# Automatic fallback order:
# 1. Groq (primary)
# 2. OpenAI (fallback)
# 3. Anthropic (fallback)
# 4. Any other available provider

orchestrator = HuntingOrchestrator()  # Uses automatic fallback
```

## 📈 Monitoring and Optimization

### **Provider Performance Tracking**

```python
import time
from laser_intelligence.ai.llm_providers import provider_manager

def benchmark_provider(provider_name, test_prompt):
    start_time = time.time()
    
    # Run test with provider
    config = provider_manager.get_provider_config(LLMProvider(provider_name))
    # ... run test ...
    
    end_time = time.time()
    response_time = end_time - start_time
    
    print(f"{provider_name}: {response_time:.2f}s")
    return response_time

# Benchmark all providers
providers = ['groq', 'openai', 'anthropic']
for provider in providers:
    benchmark_provider(provider, "Test prompt")
```

### **Cost Monitoring**

```python
def track_usage(provider, tokens_used, cost_per_token):
    usage = {
        'provider': provider,
        'tokens': tokens_used,
        'cost': tokens_used * cost_per_token,
        'timestamp': time.time()
    }
    
    # Log usage for monitoring
    print(f"Usage: {usage}")
    return usage
```

## 🛠️ Advanced Configuration

### **Custom Provider**

```python
from laser_intelligence.ai.llm_providers import LLMConfig, LLMProvider

# Add custom provider
custom_config = LLMConfig(
    provider=LLMProvider.GROQ,  # or create new enum value
    api_url="https://custom-api.com/v1/chat/completions",
    model="custom-model",
    api_key="custom_key",
    max_tokens=8000,
    temperature=0.05,
    timeout=120
)

# Use custom configuration
orchestrator = HuntingOrchestrator(
    api_key=custom_config.api_key,
    api_url=custom_config.api_url
)
```

### **Provider-Specific Optimizations**

```python
# Groq optimizations (speed-focused)
groq_config = {
    'temperature': 0.1,  # Lower for consistency
    'max_tokens': 4000,  # Standard size
    'timeout': 30,       # Fast timeout
}

# OpenAI optimizations (quality-focused)
openai_config = {
    'temperature': 0.05,  # Very low for accuracy
    'max_tokens': 6000,   # Larger context
    'timeout': 60,        # Longer timeout
}

# Anthropic optimizations (analysis-focused)
anthropic_config = {
    'temperature': 0.2,   # Slightly higher for creativity
    'max_tokens': 8000,   # Large context
    'timeout': 90,        # Long timeout for complex analysis
}
```

## 🚨 Troubleshooting

### **Common Issues**

1. **API Key Not Found**
   ```bash
   # Check environment variables
   echo $GROQ_API_KEY
   echo $OPENAI_API_KEY
   ```

2. **Provider Not Available**
   ```python
   # Check available providers
   from laser_intelligence.ai.llm_providers import get_available_providers
   print(get_available_providers())
   ```

3. **Rate Limiting**
   ```python
   # Implement retry logic
   import time
   time.sleep(1)  # Wait between requests
   ```

4. **Timeout Issues**
   ```python
   # Increase timeout for complex tasks
   config.timeout = 120  # 2 minutes
   ```

### **Debug Mode**

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging
logger = logging.getLogger('laser_intelligence.ai')
logger.setLevel(logging.DEBUG)
```

## 📋 Best Practices

### **1. Provider Selection**
- Use **Groq** for high-volume, fast operations
- Use **OpenAI** for high-accuracy data extraction
- Use **Anthropic** for complex analysis tasks

### **2. Cost Management**
- Monitor token usage across providers
- Use appropriate model sizes for tasks
- Implement caching for repeated requests

### **3. Performance Optimization**
- Use provider-specific optimizations
- Implement proper retry logic
- Monitor response times and adjust timeouts

### **4. Reliability**
- Always configure fallback providers
- Implement proper error handling
- Monitor provider health and availability

---

**The multi-LLM system provides flexibility, reliability, and optimization for different use cases while maintaining the Clay.com-style intelligent hunting capabilities.**
