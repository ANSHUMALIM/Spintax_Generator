# aoai_client.py
from __future__ import annotations
import os
import re
import random
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

def create_client(*, use_managed_identity: bool = False) -> AzureOpenAI:
    """
    Return an authenticated AzureOpenAI client.

    If `use_managed_identity` is True the SDK requests a bearer
    token via DefaultAzureCredential. Otherwise it falls back to API-key auth.
    """
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")

    if use_managed_identity:
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default",
        )
        return AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version=api_version,
        )

    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=api_version,
    )
# template_builder.py

load_dotenv()

SYSTEM_PROMPT = """
You are a world-class B2B sales copywriter.
Write outreach email templates in valid spintax using curly braces.
Respond ONLY with valid spintax in the choice|format
Each template must stay under 120 words and sound natural.
Use short paragraphs and, when possible, bullet points to make content easier to scan.
DO NOT output placeholders like [company name]; if a variable (e.g., company, first_name) has no value, use a generic word (like Company). 
For first_name use 'there' if no value is present. If there is a value, do create regular expression for it. 
Keep templates under 120 words and sound natural.
Output only spintax, never plain text.
Let there be nothing metioned like "first_name" in the greetings part of the email.
"""

def draft_spintax_template(brief, variables=None, format_type=None):
    client = create_client()
    format_instruction = ""
    if format_type == "bullets":
        format_instruction = "Present the main selling points as a bullet list where suitable."
    elif format_type == "paragraphs":
        format_instruction = "Organize the message using clear, brief paragraphs."
    else:
        format_instruction = "Use a mix of short paragraphs and bullets as appropriate."
    user_prompt = (
        f"Brief: {brief}\n"
        f"Format: {format_instruction}\n"
        f"Placeholders/Variables: {', '.join(variables or [])}"
    )
    response = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        temperature=0.8,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content.strip()
def llm_quality_check(email_text: str) -> list[str]:
    """
    Ask GPT to flag spam-trigger words, tone problems, or grammar issues.

    Returns a list of warnings; empty if none.
    """
    client = create_client()
    critique = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        temperature=0,
        messages=[
            {"role": "system",
             "content": "You are an email deliverability auditor. "
                        "Return JSON list of any issues you find."},
            {"role": "user", "content": email_text},
        ],
    )
    return critique.choices[0].message.content.strip("`[]").split(",")  # quick parse



class SpintaxGenerator:

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
            
    def generate_variations(self, template: str, variables: Dict[str, str] = {},
                            count: int = 1, unique: bool = True,
                            format_type: Optional[str] = None) -> List[str]:
        """
        Generate spintax-based email variations.
        format_type: 'bullets', 'paragraphs', or None/'auto'.
        """
        results = set() if unique else []
        while len(results) < count:
            text = self._spin(template)
            text = self._substitute_variables(text, variables)
            text = self._apply_formatting(text, format_type)
            if unique:
                results.add(text)
            else:
                results.append(text)
        return list(results)
    def _spin(self, s: str) -> str:
        pattern = re.compile(r'\{([^{}]*)\}')
        while True:
            match = pattern.search(s)
            if not match:
                break
            options = match.group(1).split('|')
            replacement = random.choice(options)
            s = s[:match.start()] + replacement + s[match.end():]
        return s
    def _substitute_variables(self, text: str, variables: Dict[str, str]) -> str:
        """
        Replace {var} with value from variables dict,
        or fallback to per-variable custom text.
        """
        def replacer(match):
            var = match.group(1)
            value = variables.get(var, "")
            # If still empty after lookup, use plain var name (but not as a placeholder)
            return value if value else var.lower()
        # Replace all {var} with correct value or fallback
        return re.sub(r"\{(\w+)\}", replacer, text)
        
    def _apply_formatting(self, text: str, format_type: Optional[str]) -> str:
        """
        Apply the requested output formatting.
        """
        if format_type == "bullets":
            # Attempt to split on periods or semicolons; turn into bullet list.
            # A more advanced approach can use NLP or LLM, but this covers many cases.
            points = re.split(r'[.;]\s*', text)
            points = [p.strip() for p in points if p.strip()]
            if len(points) > 1:
                return "\n- " + "\n- ".join(points)
            return text
        elif format_type == "paragraphs":
            # Split on two or more newlines or sentences for paragraphs
            paras = re.split(r'(?<=[.?!])\s+(?=[A-Z])', text)
            return "\n\n".join(p.strip() for p in paras if p.strip())
        # Default: no extra formatting
        return text


    
# spintax_service.py


email_template = input("Enter email template: ")

class LLMBackedSpintaxService:
    def __init__(self, seed: int | None = None) -> None:
        self.spinner = SpintaxGenerator(seed=seed)

    def new_template_from_brief(self, brief: str, vars: dict | None = None) -> str:
        raw = draft_spintax_template(brief, vars)
        issues = llm_quality_check(raw)
        if issues and any("sspam" in i.lower() for i in issues):
            raise ValueError(f"Template blocked by QA: {issues}")
        return raw

    def produce_emails(
        self,
        template: str,
        variables: dict,
        n_variations: int = 25,
    ) -> list[str]:
        return self.spinner.generate_variations(
            template,
            variables=variables,
            count=n_variations,
            unique=True,
        )
if __name__ == "__main__":
    service = LLMBackedSpintaxService(seed=42)

    # 1️⃣ Ask GPT to draft a template
    tpl = service.new_template_from_brief(
        {email_template},
        # "Invite VPs of Engineering to a free 15-min demo of our CI/CD insights tool.",
        # vars={"first_name": firstName, "company": Company_name},
        vars={"first_name": "", "company": ""}


    )
    # tpl = tpl.replace("({first_name|there})" or "({there|first_name})" , "({first_name})")  # Ensure first_name is always present
    # tpl = tpl.replace("{company|our organization}", "({company}|our organization)")
    tpl = re.sub(r"\(?\{(first_name\|there|there\|first_name)\}\)?", "{first_name}", tpl)
    print("=== GPT-drafted template ===")
    print(tpl)

    # 2️⃣ Spin 5 personalized variants
    variants = service.produce_emails(
        template=tpl,
        # variables={"first_name": firstName, "company": Company_name},
        variables={"first_name": "Ada", "company": "Acme Cloud"},
        n_variations=5,
    )
    print("\n=== Ready-to-send variants ===")
    for v in variants:
        print("-", v)
