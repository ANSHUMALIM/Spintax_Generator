# 📩 Spintax Email Generator with Azure OpenAI

This project is a production-ready **Spintax Email Generator** microservice powered by **Azure OpenAI**. It combines deterministic spintax variation with GPT-based template generation and quality checks for modern sales and outreach automation.

---

## 🔍 Features

- Uses GPT (via Azure OpenAI) to create valid spintax email templates from creative briefs.  
- Conducts deliverability QA (spam-tone-language checks).  
- Spins unique email variants using a custom Python `SpintaxGenerator`.  
- Supports personalized variable injection (`{first_name}`, `{company}`).  
- Formatting options: paragraph, bullet, or smart-mixed styling.  
- Fully modular and extendable.  

---

## 🛠️ Prerequisites

- Azure OpenAI access + deployed model (e.g., `gpt-35-turbo`)  
- Python 3.8+  
- Credentials: API key and endpoint from Azure  

---

## 🚀 Getting Started

### 1. Clone & Setup Virtual Environment

```bash
git clone https://github.com/ANSHUMALIM/Spintax_Generator.git
cd Spintax_Generator

# Create & activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
