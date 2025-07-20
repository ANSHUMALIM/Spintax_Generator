:incoming_envelope: Spintax Email Generator with Azure OpenAI
This project is a production-ready Spintax Email Generator microservice powered by Azure OpenAI. It combines deterministic spintax variation with GPT-based template generation and quality checks for modern sales and outreach automation.

:mag: Features
Uses GPT (via Azure OpenAI) to create valid spintax email templates from creative briefs.
Conducts deliverability QA (spam-tone-language checks).
Spins unique email variants using a custom Python SpintaxGenerator.
Supports personalized variable injection ({first_name}, {company}).
Formatting options: paragraph, bullet, or smart-mixed styling.
Fully modular and extendable.

:hammer_and_wrench: Prerequisites
Azure OpenAI access + deployed model (e.g., gpt-35-turbo)
Python 3.8+
Credentials: API key and endpoint from Azure

:rocket: Getting Started
1. Clone & Setup Virtual Environment
bash
git clone https://github.com/your-username/spintax-email-generator.git
cd spintax-email-generator

# Create & activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

2. Install dependencies
-pip install "openai>=1.14.0" azure-identity python-dotenv
-pip install python-dotenv

Run the service:
bash
python main.py

It will ask you for a short email brief (e.g. Invite engineering leads to a demo).
GPT will return a valid spintax email.
The service checks for spam/tone issues.
Five unique email variants will be printed using provided variables.(Which can be extended further)
