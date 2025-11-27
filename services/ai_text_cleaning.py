"""
AI-Powered Text Cleaning Service
Uses LLM to extract only essential content from crawled text
Removes navigation, footers, SEO metadata, and unnecessary context
Uses system OpenAI credentials for AI-powered features
"""
import os
from flask import g, current_app


def get_system_llm():
    """Get system LLM instance (OpenAI fallback) for AI-powered features"""
    try:
        # Try to get from Flask context first
        llm = getattr(g, 'llm', None)
        if llm:
            return llm
        
        # Try to get from app config
        if current_app:
            llm = current_app.config.get('LLM', None)
            if llm:
                return llm
        
        # Fallback: Create OpenAI LLM directly using env credentials
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        if openai_api_key:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.3,
                openai_api_key=openai_api_key
            )
            print("🤖 Using system OpenAI for AI cleaning")
            return llm
        
        return None
    except Exception as e:
        print(f"⚠️ Error getting system LLM: {e}")
        return None


def clean_text_with_ai(raw_text, llm=None):
    """
    Use AI to clean and restructure crawled text, keeping only essential content
    
    Args:
        raw_text: Raw extracted text from website
        llm: LLM instance (optional, will try to get from Flask g if not provided)
    
    Returns:
        Cleaned and restructured text with only essential content
    """
    if not raw_text or len(raw_text.strip()) < 50:
        return raw_text
    
    # Get LLM instance (use system OpenAI for AI-powered features)
    if not llm:
        llm = get_system_llm()
    
    if not llm:
        print("⚠️ System LLM (OpenAI) not available for AI cleaning, returning original text")
        return raw_text
    
    # Create prompt for AI cleaning
    prompt = f"""You are a content extraction assistant. Your task is to clean and restructure the following text extracted from a website, keeping ONLY the essential content that actually exists in the source text.

CRITICAL RULE: ONLY EXTRACT WHAT IS ACTUALLY IN THE SOURCE TEXT. DO NOT ADD, INVENT, OR CREATE ANY INFORMATION THAT IS NOT PRESENT IN THE ORIGINAL TEXT.

REMOVE:
- Navigation menus and links (except important content links)
- Header/footer navigation elements (menus, breadcrumbs)
- SEO metadata and experiment notes
- Repetitive headers and formatting
- Copyright notices and generic legal text
- Social media icons/links (unless they contain important information)
- "Skip to main content" and similar UI elements
- Breadcrumbs and site structure elements
- Advertisement text
- Cookie notices and legal disclaimers (unless they are the main content)

KEEP (ONLY IF PRESENT IN SOURCE TEXT):
- Main article/content text
- Important headings and subheadings
- Key information and facts
- Educational content
- Product/service descriptions
- Core message and value proposition
- Contact information (phone numbers, email addresses, physical addresses, website URLs) - ONLY if they exist in the source
- Business hours and location details - ONLY if present in source
- Pricing information - ONLY if present in source
- Booking/reservation links - ONLY if present in source

STRICT RULES FOR CONTACT INFORMATION:
- ONLY extract contact information that is ACTUALLY PRESENT in the source text
- DO NOT add example phone numbers, emails, or addresses
- DO NOT create placeholder contact information
- DO NOT add "(example)" or similar annotations
- DO NOT create a "Contact Information" section if no contact details exist in the source
- If contact info exists in the source, preserve it exactly as it appears (or format it clearly if it's scattered)
- If NO contact information exists in the source, do NOT mention contact information at all

RESTRUCTURE:
- Use clear, concise headings
- Organize content logically
- Remove redundant information
- Keep only the most important details that exist in the source
- Maintain readability and flow
- Only add a "Contact Information" section if contact details ACTUALLY EXIST in the source text

INPUT TEXT:
{raw_text[:8000]}  # Limit to avoid token limits

OUTPUT: Clean, restructured content with ONLY the information that exists in the source text. Do not add, invent, or create any information. If no contact information exists in the source, do not include any contact information section."""

    try:
        # Use LLM to clean the text
        if hasattr(llm, 'invoke'):
            # LangChain-style LLM
            response = llm.invoke(prompt)
            cleaned_text = response.content if hasattr(response, 'content') else str(response)
        elif hasattr(llm, 'generate'):
            # OpenAI-style LLM
            response = llm.generate([prompt])
            cleaned_text = response.generations[0][0].text if response.generations else str(response)
        else:
            # Try direct call
            cleaned_text = str(llm(prompt))
        
        # Clean up the response
        cleaned_text = cleaned_text.strip()
        
        # Remove any prompt artifacts that might have been included
        if "OUTPUT:" in cleaned_text:
            cleaned_text = cleaned_text.split("OUTPUT:")[-1].strip()
        if "INPUT TEXT:" in cleaned_text:
            cleaned_text = cleaned_text.split("INPUT TEXT:")[0].strip()
        
        print(f"✅ AI cleaned text: {len(raw_text)} → {len(cleaned_text)} characters")
        
        return cleaned_text
        
    except Exception as e:
        print(f"⚠️ AI cleaning failed: {e}")
        import traceback
        traceback.print_exc()
        # Return original text if AI cleaning fails
        return raw_text

