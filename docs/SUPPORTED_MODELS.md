# Supported LLM Models

The Agent Engineering Playground supports multiple LLM providers, giving you flexibility in choosing the model that best fits your needs.

## Supported Providers

### 1. Anthropic (Claude)

**Models:**
- `claude-3-5-sonnet-20241022` (default, recommended)
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`

**Setup:**
1. Get API key from [Anthropic Console](https://console.anthropic.com/)
2. Add to `.env`: `ANTHROPIC_API_KEY=your_key_here`

**Best for:**
- Complex reasoning tasks
- Multi-step planning
- Natural language understanding
- Long context windows

---

### 2. OpenAI (GPT)

**Models:**
- `gpt-4-turbo-preview`
- `gpt-4`
- `gpt-3.5-turbo`

**Setup:**
1. Get API key from [OpenAI Platform](https://platform.openai.com/)
2. Add to `.env`: `OPENAI_API_KEY=your_key_here`

**Best for:**
- General purpose tasks
- Fast iterations
- Cost-effective experimentation
- Wide model selection

---

### 3. Google (Gemini)

**Models:**
- `gemini-pro`
- `gemini-pro-vision` (for multimodal tasks)

**Setup:**
1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add to `.env`: `GOOGLE_API_KEY=your_key_here`

**Best for:**
- Google Cloud integration
- Multimodal capabilities
- Cost-effective at scale
- Research and experimentation

---

## Choosing a Model

### For Learning (Recommended)
**Claude 3.5 Sonnet** - Best balance of capability and cost
- Default model in the playground
- Excellent reasoning abilities
- Clear explanations of agent thinking

### For Quick Experiments
**GPT-3.5 Turbo** - Fastest and most cost-effective
- Good for rapid prototyping
- Lower latency
- Sufficient for simple tasks

### For Complex Tasks
**GPT-4** or **Claude 3 Opus** - Maximum capability
- Best performance on difficult challenges
- Better at multi-step reasoning
- Higher cost per request

### For Budget-Conscious Users
**Gemini Pro** - Great value
- Competitive performance
- Lower pricing
- Good for extended learning sessions

---

## Configuration

### In Backend Code

When configuring an agent, specify the model:

```python
from src.models.agent import AgentConfig

config = AgentConfig(
    system_prompt="You are a helpful agent...",
    model="claude-3-5-sonnet-20241022",  # or "gpt-4", "gemini-pro"
    temperature=0.7,
    max_steps=50
)
```

### In Environment Variables

Ensure at least one API key is configured:

```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AI...
```

---

## Pricing Comparison (Approximate)

| Provider | Model | Input (per 1M tokens) | Output (per 1M tokens) |
|----------|-------|----------------------|------------------------|
| Anthropic | Claude 3.5 Sonnet | $3 | $15 |
| Anthropic | Claude 3 Haiku | $0.25 | $1.25 |
| OpenAI | GPT-4 Turbo | $10 | $30 |
| OpenAI | GPT-3.5 Turbo | $0.50 | $1.50 |
| Google | Gemini Pro | $0.50 | $1.50 |

*Prices are approximate and subject to change. Check provider websites for current pricing.*

---

## Switching Models

You can switch models at any time:

1. **In the UI**: Select from the model dropdown (coming soon)
2. **In Code**: Update the `model` field in `AgentConfig`
3. **Per Level**: Different levels can use different models

---

## Troubleshooting

### "API key not configured" error
- Verify API key is in `.env` file
- Restart backend server after adding keys
- Check `/health` endpoint: `http://localhost:8000/health`

### Model not responding
- Verify API key has correct permissions
- Check API provider status page
- Ensure sufficient credits/quota

### Rate limiting
- Different providers have different rate limits
- Consider upgrading your API plan
- Implement exponential backoff (handled automatically)

---

## Future Support

We plan to add support for:
- Local models (Ollama, LM Studio)
- Azure OpenAI
- Cohere
- Mistral AI
- Custom model endpoints

Want to add support for a new provider? See [CONTRIBUTING.md](../CONTRIBUTING.md)!
