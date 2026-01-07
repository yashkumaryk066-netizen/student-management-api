# ChatGPT AI Integration - Quick Setup Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Install OpenAI Package
```bash
pip install openai>=1.3.0
```

### Step 2: Get Your API Key
1. Visit: https://platform.openai.com/api-keys
2. Sign up / Login
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)
5. **IMPORTANT:** Save it securely - you won't see it again!

### Step 3: Configure Environment
Add to your `.env` file:
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**That's it! You're ready to use ChatGPT AI! 🎉**

---

## ✅ Verify Installation

Run the test script:
```bash
python test_chatgpt_ai.py
```

If all tests pass, your ChatGPT integration is working! ✨

---

## 🔍 Check Service Status

Visit: `http://your-domain.com/api/ai/chatgpt/health/`

You should see:
```json
{
    "status": "operational",
    "service": "ChatGPT AI"
}
```

---

## 📚 Available Features

### 1. **AI Tutoring** (`/api/ai/tutor/`)
- Ask questions, get detailed explanations
- Subject-specific tutoring
- Educational context awareness

### 2. **Quiz Generation** (`/api/ai/quiz/generate/`)
- Auto-generate quizzes on any topic
- Multiple choice, true/false, short answer
- Customizable difficulty levels

### 3. **Assignment Grading** (`/api/ai/grade/`)
- AI-powered grading with feedback
- Rubric-based evaluation
- Detailed suggestions for improvement

### 4. **Content Summarization** (`/api/ai/summarize/`)
- Summarize long texts
- Preserve key concepts
- Adjustable summary length

### 5. **Concept Explanation** (`/api/ai/explain/`)
- Explain complex topics simply
- Age-appropriate language
- Uses examples and analogies

### 6. **Translation** (`/api/ai/translate/`)
- Translate to any language
- Educational content focus
- Maintains accuracy

### 7. **Lesson Planning** (`/api/ai/lesson-plan/`)
- Generate complete lesson plans
- Grade-level appropriate
- Includes objectives, activities, assessment

### 8. **Writing Analysis** (`/api/ai/writing/analyze/`)
- Grammar and style checking
- Constructive feedback
- Improvement suggestions

### 9. **Custom Prompts** (`/api/ai/prompt/`)
- Flexible AI interactions
- Custom educational content
- Unlimited possibilities

---

## 💻 Quick Examples

### JavaScript (Frontend)
```javascript
// Ask AI Tutor
const response = await fetch('/api/ai/tutor/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        question: "What is gravity?",
        subject: "Physics"
    })
});
const data = await response.json();
console.log(data.answer);
```

### Python (Backend)
```python
from ai.chatgpt import get_chatgpt_service

service = get_chatgpt_service()
answer = service.ask_tutor("What is DNA?", "Biology")
print(answer)
```

### cURL (Terminal)
```bash
curl -X POST http://localhost:8000/api/ai/tutor/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain photosynthesis", "subject": "Biology"}'
```

---

## 🎯 Configuration Options

### Model Selection
Choose between different GPT models in `.env`:

```bash
# Best quality, higher cost
OPENAI_MODEL=gpt-4-turbo-preview

# Balanced (recommended)
OPENAI_MODEL=gpt-4-turbo-preview

# Fast & economical
OPENAI_MODEL=gpt-3.5-turbo
```

### Creativity Control
```bash
# More creative (0.0 - 1.0)
OPENAI_TEMPERATURE=0.9

# Balanced
OPENAI_TEMPERATURE=0.7

# More focused/deterministic
OPENAI_TEMPERATURE=0.3
```

### Response Length
```bash
# Shorter responses
OPENAI_MAX_TOKENS=1000

# Default
OPENAI_MAX_TOKENS=2000

# Longer responses
OPENAI_MAX_TOKENS=4000
```

---

## 💰 Cost Management

### Pricing (Approximate)
- **GPT-4 Turbo:** $0.01-0.05 per request
- **GPT-3.5 Turbo:** $0.001-0.01 per request

### Tips to Reduce Costs:
1. Use GPT-3.5 for simple tasks
2. Set appropriate max_tokens
3. Cache frequently asked questions
4. Implement user quotas
5. Monitor usage on OpenAI dashboard

---

## 🔒 Security Checklist

- ✅ Never commit `.env` file to Git
- ✅ Use environment variables for API keys
- ✅ Rotate API keys every 90 days
- ✅ Set up billing alerts on OpenAI
- ✅ Implement rate limiting
- ✅ Validate all user inputs
- ✅ Log API usage for monitoring

---

## 🐛 Troubleshooting

### "OPENAI_API_KEY not found"
**Solution:** Add your API key to `.env` file

### "Authentication failed"
**Solution:** Check if your API key is valid, not expired

### "Rate limit exceeded"
**Solution:** Wait a few minutes or upgrade your OpenAI plan

### "Model not found"
**Solution:** Check model name in `.env`, use supported models

### Test script fails
**Solution:** 
1. Check internet connection
2. Verify API key is correct
3. Ensure OpenAI account has credits
4. Check OpenAI service status

---

## 📖 Full Documentation

For complete API documentation, see:
- `CHATGPT_AI_DOCUMENTATION.md` - Complete API reference
- OpenAI Docs: https://platform.openai.com/docs

---

## 🆘 Support

### Common Issues
1. **Import errors:** Run `pip install -r requirements.txt`
2. **Connection errors:** Check internet & OpenAI status
3. **Slow responses:** Try GPT-3.5 or reduce max_tokens
4. **Empty responses:** Increase max_tokens limit

### Get Help
- Check health endpoint: `/api/ai/chatgpt/health/`
- Review error messages in Django logs
- Test with: `python test_chatgpt_ai.py`
- Contact system administrator

---

## 🎓 Best Practices

### For Developers
- Handle errors gracefully
- Show loading states to users
- Cache common responses
- Log important interactions
- Monitor API costs

### For Content
- Write clear, specific prompts
- Provide context when needed
- Use appropriate models
- Verify AI responses
- Combine with human review

---

## 🌟 What's Next?

Your ChatGPT AI is now fully integrated! Start using it to:
- ✨ Provide instant tutoring to students
- 📝 Generate educational content automatically
- ✅ Grade assignments faster
- 🌍 Translate materials for multilingual students
- 📚 Create comprehensive lesson plans
- ✍️ Analyze and improve student writing

**Enjoy the power of AI in your education system! 🚀**

---

**Need help? Check `CHATGPT_AI_DOCUMENTATION.md` for detailed examples!**
