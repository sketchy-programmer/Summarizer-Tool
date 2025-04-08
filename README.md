# AI Summarizer Deployment Guide

## Prerequisites
- Python 3.8+
- Stripe Account
- OpenAI API Key

## Environment Setup
1. Create a `.env` file with:
```
SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_key
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
```

## Web Deployment
- Use Heroku or similar platform
- Set environment variables
- Run `gunicorn app:app`

## Desktop App Distribution
- Run `python package.py`
- Executable will be in `dist/` directory