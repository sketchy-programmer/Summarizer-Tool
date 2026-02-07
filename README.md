<div align="center">

# ✏️ Shortify

### AI-Powered Text Summarizer & Paraphraser

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![Stripe](https://img.shields.io/badge/Stripe-Payments-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://stripe.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<p align="center">
  <strong>Transform lengthy texts into concise summaries, creative paraphrases, and clear code explanations with the power of AI.</strong>
</p>

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api-reference) • [Deployment](#-deployment)

---

</div>

## Overview

**Shortify** is a dual-platform AI text processing tool that combines a web application with a native desktop app. Powered by OpenAI's GPT-3.5, it offers intelligent text summarization, paraphrasing, and code explanation capabilities.

<table>
<tr>
<td width="50%">

### 🌐 Web Application
- User authentication & registration
- Premium subscription via Stripe
- Web-based summarization tool
- Dashboard for premium users

</td>
<td width="50%">

### 💻 Desktop Application
- Floating icon for quick access
- Works with any application
- Right-click context menu
- Customizable settings

</td>
</tr>
</table>

---

## ✨ Features

<table>
<tr>
<td align="center" width="33%">
<img src="https://img.shields.io/badge/-Summarize-667eea?style=flat-square" alt="Summarize"/>
<br><br>
<strong>Text Summarization</strong>
<br>
Condense long articles, documents, and text into key points
</td>
<td align="center" width="33%">
<img src="https://img.shields.io/badge/-Paraphrase-764ba2?style=flat-square" alt="Paraphrase"/>
<br><br>
<strong>Paraphrasing</strong>
<br>
Rewrite text in different words while preserving meaning
</td>
<td align="center" width="33%">
<img src="https://img.shields.io/badge/-Code-00d4aa?style=flat-square" alt="Code"/>
<br><br>
<strong>Code Explanation</strong>
<br>
Get clear explanations of code snippets in plain English
</td>
</tr>
</table>

### Writing Styles

| Style | Description |
|-------|-------------|
| 🎯 **Default** | Clear and balanced output |
| 🎓 **Academic** | Formal, structured with technical language |
| 💬 **Casual** | Conversational and easy to understand |
| 💼 **Business** | Professional with actionable insights |
| 🎨 **Creative** | Engaging with vivid language |

---

## 🛠️ Tech Stack

<div align="center">

| Category | Technologies |
|----------|-------------|
| **Backend** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white) |
| **AI/ML** | ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white) |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat-square&logo=postgresql&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white) |
| **Payments** | ![Stripe](https://img.shields.io/badge/Stripe-635BFF?style=flat-square&logo=stripe&logoColor=white) |
| **Desktop** | ![Tkinter](https://img.shields.io/badge/Tkinter-3776AB?style=flat-square&logo=python&logoColor=white) |
| **Deployment** | ![Heroku](https://img.shields.io/badge/Heroku-430098?style=flat-square&logo=heroku&logoColor=white) ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=flat-square&logo=gunicorn&logoColor=white) |

</div>

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API Key
- Stripe Account (for payments)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/Summarizer-Tool.git
cd Summarizer-Tool

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables

Create a `.env` file in the root directory:

```env
# Required
SECRET_KEY=your_flask_secret_key
OPENAI_API_KEY=your_openai_api_key

# For Stripe Payments
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key

# For Production (PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

---

## 🚀 Usage

### Web Application

```bash
# Development
cd web
python app.py

# Production
gunicorn web.app:app
```

Visit `http://localhost:5000` in your browser.

### Desktop Application

```bash
# Run directly
cd desktop
python main.py

# Build executable
python package.py
```

#### Desktop App Controls

| Action | How to Use |
|--------|-----------|
| **Move** | Drag the pencil icon |
| **Open Menu** | Right-click the icon |
| **Summarize** | Copy text → Right-click → Summarize |
| **Paraphrase** | Copy text → Right-click → Paraphrase |
| **Explain Code** | Copy code → Right-click → Explain Code |
| **Settings** | Right-click → Settings |

---

## 📡 API Reference

### Authentication Required

All API endpoints require user authentication.

### Endpoints

<details>
<summary><strong>POST /api/summarize</strong></summary>

Summarize text content.

**Request Body:**
```json
{
  "text": "Your long text here...",
  "min_length": 100,
  "max_length": 150,
  "style": "default"
}
```

**Response:**
```json
{
  "success": true,
  "result": "Summarized text..."
}
```
</details>

<details>
<summary><strong>POST /api/paraphrase</strong></summary>

Paraphrase text content.

**Request Body:**
```json
{
  "text": "Your text here...",
  "min_length": 100,
  "max_length": 200,
  "style": "casual"
}
```

**Response:**
```json
{
  "success": true,
  "result": "Paraphrased text..."
}
```
</details>

<details>
<summary><strong>POST /api/code-summarize</strong></summary>

Explain code snippets.

**Request Body:**
```json
{
  "text": "def hello(): print('Hello')",
  "max_length": 150,
  "language": "python"
}
```

**Response:**
```json
{
  "success": true,
  "result": "This Python function..."
}
```
</details>

---

## ☁️ Deployment

### Heroku Deployment

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY=your_secret_key
heroku config:set OPENAI_API_KEY=your_openai_key
heroku config:set STRIPE_PUBLIC_KEY=your_stripe_public_key
heroku config:set STRIPE_SECRET_KEY=your_stripe_secret_key

# Deploy
git push heroku main
```

### Configuration Files

| File | Purpose |
|------|---------|
| `Procfile` | Heroku process configuration |
| `runtime.txt` | Python version specification |
| `requirements.txt` | Python dependencies |

---

## 📁 Project Structure

```
Summarizer-Tool/
├── 📂 web/                    # Flask web application
│   ├── app.py                 # Main Flask app
│   ├── templates/             # HTML templates
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   └── web_tool.html
│   └── static/                # Static files & executables
│
├── 📂 desktop/                # Desktop application
│   ├── main.py                # Entry point
│   ├── gui.py                 # Tkinter GUI
│   ├── summarizer.py          # OpenAI integration
│   ├── config.py              # Configuration
│   └── assets/                # Images & resources
│
├── 📄 Procfile                # Heroku configuration
├── 📄 runtime.txt             # Python version
├── 📄 requirements.txt        # Dependencies
├── 📄 package.py              # PyInstaller build script
└── 📄 README.md               # This file
```

---

## 💳 Premium Features

Shortify offers a freemium model with premium features:

| Feature | Free | Premium |
|---------|:----:|:-------:|
| Web Demo | ✅ | ✅ |
| Desktop App | ❌ | ✅ |
| All Writing Styles | ❌ | ✅ |
| Unlimited Usage | ❌ | ✅ |
| Priority Support | ❌ | ✅ |

**Premium Price:** $1.00 (one-time payment via Stripe)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

### Made with ❤️ and AI

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/yourusername/Summarizer-Tool)

</div>
