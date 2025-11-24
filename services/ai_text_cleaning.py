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
    prompt = f"""You are a content extraction assistant. Your task is to clean and restructure the following text extracted from a website, keeping ONLY the essential content and removing all unnecessary elements.

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

KEEP (CRITICAL - DO NOT REMOVE):
- Main article/content text
- Important headings and subheadings
- Key information and facts
- Educational content
- Product/service descriptions
- Core message and value proposition
- **ALL CONTACT INFORMATION** (phone numbers, email addresses, physical addresses, website URLs)
- **FOOTER CONTACT DETAILS** (extract and preserve phone, email, address, booking links from footers)
- Important links to other pages (not navigation)
- Business hours and location details
- Pricing information (if relevant)
- Booking/reservation links and information

SPECIAL INSTRUCTIONS FOR CONTACT INFORMATION:
- Extract ALL phone numbers, email addresses, and physical addresses
- Preserve website URLs and booking links
- If contact info is in footer, extract it and include it in a "Contact Information" section at the end
- Format contact information clearly (e.g., "Phone: +1-555-1234", "Email: info@example.com", "Address: 123 Main St")
- Keep all reservation/booking links and contact methods

RESTRUCTURE:
- Use clear, concise headings
- Organize content logically
- Remove redundant information
- Keep only the most important details
- Maintain readability and flow
- Add a "Contact Information" section at the end if contact details were found in footer

INPUT TEXT:
{raw_text[:8000]}  # Limit to avoid token limits

OUTPUT: Clean, restructured content with only essential information. Include a "Contact Information" section at the end if contact details were found. Be concise but comprehensive."""

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

