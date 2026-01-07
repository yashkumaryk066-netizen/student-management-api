# ChatGPT AI Integration - API Documentation

## 🚀 Overview

The **ChatGPT AI Integration** adds powerful AI capabilities to the Y.S.M Advanced Education System, providing intelligent tutoring, content generation, automated grading, and more using OpenAI's GPT models.

---

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
pip install openai>=1.3.0
```

### 2. Get OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Click **Create new secret key**
5. Copy the API key (starts with `sk-...`)

### 3. Configure Environment Variables

Add to your `.env` file:

```bash
# ChatGPT / OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here

# Optional: Model Configuration
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000
```

**Available Models:**
- `gpt-4-turbo-preview` (Recommended - Advanced reasoning)
- `gpt-4` (Most capable, slower)
- `gpt-3.5-turbo` (Fast, cost-effective)

---

## 📡 API Endpoints

### Base URL
```
/api/ai/
```

### Authentication
All endpoints (except health check) require JWT authentication:
```
Authorization: Bearer <your-jwt-token>
```

---

## 🔍 1. Health Check

**Endpoint:** `GET /api/ai/chatgpt/health/`

**Description:** Check if ChatGPT service is available

**Authentication:** ❌ Not required

**Response:**
```json
{
    "status": "operational",
    "service": "ChatGPT AI",
    "model": "gpt-4-turbo-preview",
    "features": [
        "AI Tutoring",
        "Quiz Generation",
        "Assignment Grading",
        "Content Summarization",
        "Concept Explanation",
        "Translation",
        "Lesson Planning",
        "Writing Analysis"
    ]
}
```

---

## 🎓 2. AI Tutoring

**Endpoint:** `POST /api/ai/tutor/`

**Description:** Ask the AI tutor a question and get detailed educational explanations

**Request Body:**
```json
{
    "question": "What is photosynthesis?",
    "subject": "Biology",
    "context": "I'm studying for my biology exam"
}
```

**Response:**
```json
{
    "success": true,
    "question": "What is photosynthesis?",
    "subject": "Biology",
    "answer": "Photosynthesis is the process by which green plants...",
    "model": "gpt-4-turbo-preview"
}
```

---

## 📝 3. Quiz Generation

**Endpoint:** `POST /api/ai/quiz/generate/`

**Description:** Automatically generate quiz questions on any topic

**Request Body:**
```json
{
    "topic": "World War II",
    "num_questions": 5,
    "difficulty": "medium",
    "question_type": "multiple_choice"
}
```

**Parameters:**
- `topic` (required): Quiz topic
- `num_questions` (optional): Number of questions (default: 5)
- `difficulty` (optional): `easy`, `medium`, `hard` (default: medium)
- `question_type` (optional): `multiple_choice`, `true_false`, `short_answer`

**Response:**
```json
{
    "success": true,
    "topic": "World War II",
    "quiz": "[{\"question\": \"...\", \"options\": [...], \"correct_answer\": \"...\"}]",
    "num_questions": 5,
    "difficulty": "medium"
}
```

---

## 📄 4. Content Summarization

**Endpoint:** `POST /api/ai/summarize/`

**Description:** Summarize long educational content into concise summaries

**Request Body:**
```json
{
    "text": "Long educational content to summarize...",
    "max_length": 200
}
```

**Response:**
```json
{
    "success": true,
    "original_length": 1500,
    "summary": "Concise summary of the content...",
    "summary_length": 180
}
```

---

## ✅ 5. Assignment Grading

**Endpoint:** `POST /api/ai/grade/`

**Description:** AI-powered assignment grading with detailed feedback

**Request Body:**
```json
{
    "assignment_text": "Student's assignment submission...",
    "rubric": "Grading criteria: 1. Content accuracy (40%), 2. Organization (30%)...",
    "max_score": 100
}
```

**Response:**
```json
{
    "success": true,
    "grading": {
        "score": 85,
        "overall_feedback": "Strong analysis with good examples...",
        "strengths": ["Clear arguments", "Good use of evidence"],
        "areas_for_improvement": ["Add more transitions", "Conclusion could be stronger"],
        "detailed_comments": "Detailed grading explanation..."
    }
}
```

---

## 💡 6. Concept Explanation

**Endpoint:** `POST /api/ai/explain/`

**Description:** Explain complex concepts in age-appropriate language

**Request Body:**
```json
{
    "concept": "Quantum entanglement",
    "grade_level": "high school"
}
```

**Grade Levels:**
- `elementary school`
- `middle school`
- `high school`
- `college`
- `graduate`

**Response:**
```json
{
    "success": true,
    "concept": "Quantum entanglement",
    "grade_level": "high school",
    "explanation": "Think of quantum entanglement like this..."
}
```

---

## 🌍 7. Content Translation

**Endpoint:** `POST /api/ai/translate/`

**Description:** Translate educational content to different languages

**Request Body:**
```json
{
    "text": "The mitochondria is the powerhouse of the cell",
    "target_language": "Hindi"
}
```

**Supported Languages:** Any language (Hindi, Spanish, French, German, etc.)

**Response:**
```json
{
    "success": true,
    "original": "The mitochondria is the powerhouse of the cell",
    "target_language": "Hindi",
    "translated": "माइटोकॉन्ड्रिया कोशिका का ऊर्जा केंद्र है"
}
```

---

## 📚 8. Lesson Plan Generation

**Endpoint:** `POST /api/ai/lesson-plan/`

**Description:** Generate comprehensive lesson plans for any topic

**Request Body:**
```json
{
    "topic": "Introduction to Algebra",
    "duration_minutes": 45,
    "grade_level": "middle school"
}
```

**Response:**
```json
{
    "success": true,
    "topic": "Introduction to Algebra",
    "duration_minutes": 45,
    "grade_level": "middle school",
    "lesson_plan": "Detailed lesson plan with objectives, activities, assessment..."
}
```

---

## ✍️ 9. Writing Analysis

**Endpoint:** `POST /api/ai/writing/analyze/`

**Description:** Analyze student writing for grammar, style, and structure

**Request Body:**
```json
{
    "writing_sample": "Student's essay or writing sample..."
}
```

**Response:**
```json
{
    "success": true,
    "analysis": {
        "grammar_score": 8,
        "structure_score": 7,
        "clarity_score": 9,
        "vocabulary_score": 8,
        "key_issues": ["Some run-on sentences", "Passive voice overuse"],
        "suggestions": ["Break long sentences", "Use more active voice"],
        "positive_points": ["Clear thesis", "Good examples"]
    }
}
```

---

## 🎯 10. Custom AI Prompt

**Endpoint:** `POST /api/ai/prompt/`

**Description:** Send custom prompts for flexible AI interactions

**Request Body:**
```json
{
    "prompt": "Generate 5 creative writing prompts for high school students",
    "system_message": "You are a creative writing instructor"
}
```

**Response:**
```json
{
    "success": true,
    "prompt": "Generate 5 creative writing prompts...",
    "response": "1. Write a story where time flows backwards...\n2. Imagine a world where..."
}
```

---

## 💰 Pricing & Usage

### OpenAI API Costs (as of 2024)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| GPT-4 Turbo | $10 | $30 |
| GPT-4 | $30 | $60 |
| GPT-3.5 Turbo | $0.50 | $1.50 |

### Cost Estimation
- **AI Tutoring:** ~$0.01-0.05 per question
- **Quiz Generation:** ~$0.02-0.10 per quiz
- **Assignment Grading:** ~$0.05-0.20 per assignment

---

## 🔒 Security Best Practices

1. **Never commit API keys** - Always use environment variables
2. **Rotate keys regularly** - Recommended every 90 days
3. **Monitor usage** - Set up billing alerts on OpenAI dashboard
4. **Rate limiting** - Implement user quotas to control costs
5. **Input validation** - Sanitize all user inputs before sending to AI

---

## 🚨 Error Handling

### Common Errors

**Authentication Error (503):**
```json
{
    "status": "unavailable",
    "error": "AI service authentication failed. Please check API credentials."
}
```

**Rate Limit (500):**
```json
{
    "error": "AI service rate limit exceeded. Please try again later."
}
```

**Invalid Request (500):**
```json
{
    "error": "Invalid AI request: ...",
    "details": "Model 'xyz' does not exist"
}
```

---

## 📊 Integration Examples

### Frontend JavaScript Example

```javascript
// AI Tutoring Request
async function askAITutor(question, subject) {
    const response = await fetch('/api/ai/tutor/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            question: question,
            subject: subject
        })
    });
    
    const data = await response.json();
    console.log('AI Answer:', data.answer);
}

// Quiz Generation
async function generateQuiz(topic, numQuestions = 5) {
    const response = await fetch('/api/ai/quiz/generate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            topic: topic,
            num_questions: numQuestions,
            difficulty: 'medium'
        })
    });
    
    const data = await response.json();
    const quiz = JSON.parse(data.quiz);
    console.log('Generated Quiz:', quiz);
}
```

### Python Client Example

```python
import requests

API_BASE = "https://your-domain.com/api"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Ask AI Tutor
response = requests.post(
    f"{API_BASE}/ai/tutor/",
    headers=headers,
    json={
        "question": "Explain Newton's laws of motion",
        "subject": "Physics"
    }
)
print(response.json()['answer'])
```

---

## 🎨 Use Cases

### For Students
- Get instant help with homework
- Practice with AI-generated quizzes
- Improve writing with AI feedback
- Learn complex concepts in simple terms

### For Teachers
- Generate lesson plans automatically
- Grade assignments faster with AI assistance
- Create custom quizzes on any topic
- Translate materials for multilingual classrooms

### For Administrators
- Provide 24/7 tutoring support
- Scale educational content creation
- Reduce teacher workload
- Enhance student learning outcomes

---

## 🔄 Updates & Roadmap

### Current Version: 1.0.0

**Features:**
- ✅ AI Tutoring
- ✅ Quiz Generation
- ✅ Assignment Grading
- ✅ Content Summarization
- ✅ Concept Explanation
- ✅ Content Translation
- ✅ Lesson Planning
- ✅ Writing Analysis

**Coming Soon:**
- 🔜 Image-based question answering
- 🔜 Voice-to-text tutoring
- 🔜 Personalized learning paths
- 🔜 Multi-model support (Gemini, Claude)

---

## 📞 Support

For issues or questions:
1. Check health endpoint: `/api/ai/chatgpt/health/`
2. Review error messages in response
3. Check OpenAI dashboard for API status
4. Contact system administrator

---

**Now your Y.S.M Advanced Education System has premium AI capabilities! 🎉**
