# 🧠 MindLens Backend API

Backend API for MindLens - An intelligent multimodal analyzer powered by Gemini 3.

## 🚀 Live Demo

- **Frontend**: [https://ton-url-netlify.netlify.app](https://ton-url-netlify.netlify.app)
- **API Health**: [https://ton-url-railway.up.railway.app/health](https://ton-url-railway.up.railway.app/health)
- **API Docs**: [https://ton-url-railway.up.railway.app/docs](https://ton-url-railway.up.railway.app/docs)

## 🎯 What is MindLens?

MindLens transforms images and documents into structured reasoning using **Gemini 3's multimodal capabilities**. Unlike simple chatbots, MindLens:

- 👁️ **Observes** factually what it sees
- 🔍 **Analyzes** implications and patterns
- 🧠 **Reasons** through explicit logical chains
- ✅ **Recommends** prioritized actions

## ⚡ Key Features

### Gemini 3 Integration

- **Model**: `gemini-2.5-flash-lite` for low latency
- **Multimodal Vision**: Analyzes images (infrastructure, charts, documents)
- **Structured Prompting**: Custom prompts enforce reasoning structure
- **Safety**: Content validation and rate limiting

### Use Cases

1. **Infrastructure Analysis**: Roads, buildings, public spaces
2. **Data Interpretation**: Charts, graphs, statistics
3. **Document Processing**: Reports, articles, strategic documents

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.115.0
- **AI**: Google Gemini 3 API
- **Validation**: Pydantic 2.10.3
- **Security**: Rate limiting, file validation, CORS
- **Deployment**: Railway.app

## 📁 Project Structure

    ```
mindlens-backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration management
│   ├── services/
│   │   ├── gemini_service.py    # Gemini 3 integration
│   │   └── file_handler.py      # Secure file handling
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   ├── routes/
│   │   └── analysis.py          # API endpoints
│   ├── utils/
│   │   ├── validators.py        # File validation
│   │   └── security.py          # Security utilities
│   └── prompts/
│       └── analysis_prompts.py  # Structured prompts
├── uploads/                 # Temporary file storage
├── requirements.txt
├── Procfile                 # Railway deployment
└── README.md
    ```

## 🚀 Local Setup

### Prerequisites

- Python 3.12+
- Gemini API Key

### Installation

    ```bash
    # Clone repository
`git clone https://github.com/ton-username/mindlens-backend.git`
cd mindlens-backend

    # Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

    # Install dependencies
pip install -r requirements.txt

    # Configure environment
cp .env.example .env
    # Edit .env and add your GEMINI_API_KEY
    ```

### Run Locally

    ```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

Access at: `http://localhost:8000`

## 🔐 Environment Variables

    ```env
GEMINI_API_KEY=your_api_key_here
DEBUG=False
ALLOWED_ORIGINS=https://your-frontend-url.netlify.app
MAX_FILE_SIZE=10485760
RATE_LIMIT_PER_MINUTE=5
    ```

## 📡 API Endpoints

### Health Check

    ```
GET /health
    ```

### Analyze File

    ```
POST /api/analyze
    ```

**Request:**

- `file`: File (image or text, max 10MB)
- `analysis_type`: "infrastructure" | "data" | "document"

**Response:**

    ```json
{
  "observations": "Factual observations...",
  "analysis": "Deep analysis...",
  "reasoning": "Logical chain...",
  "actions": ["Action 1", "Action 2", ...]
}
    ```

## 🔒 Security Features

- ✅ File type validation (MIME + magic bytes)
- ✅ Size limits (10MB max)
- ✅ Secure filename generation
- ✅ Automatic file cleanup
- ✅ Rate limiting (5 req/min)
- ✅ CORS protection

## 🎓 Gemini 3 Hackathon

**Built for**: Google DeepMind Gemini 3 Global Hackathon
**Category**: Multimodal AI Analysis
**Innovation**: Structured reasoning over simple description

## 📄 License

MIT License - Built for educational and hackathon purposes

## 👥 Author

[CHOGOU Donald] - [https://github.com/MaximusDonald]

---

**⭐ If you find this project interesting, please star the repo!**
