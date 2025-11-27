"""Unified LLM Service - Factory pattern for multiple providers"""
from langchain_openai import ChatOpenAI
import os


class LLMProvider:
    """Unified interface for all LLM providers"""
    
    @staticmethod
    def get_llm(provider="openai", model=None, api_key=None, temperature=0.3, max_tokens=2000, **kwargs):
        """
        Factory method to get LLM instance based on provider
        
        Args:
            provider: 'openai' (default), 'claude', 'gemini', 'deepseek', 'groq', 'together'
            model: Model name (e.g., 'gpt-4o-mini', 'claude-3-5-sonnet')
            api_key: Provider-specific API key (uses env var if None)
            temperature: Temperature for response (0.0-2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional provider-specific parameters
        
        Returns:
            LangChain LLM instance
        """
        # Default to OpenAI if provider not specified
        if not provider or provider == "openai":
            provider = "openai"
        
        # Get API key from parameter or environment (provider-specific)
        if not api_key:
            if provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY", "")
            elif provider == "claude":
                api_key = os.getenv("ANTHROPIC_API_KEY", "")
            elif provider == "gemini":
                api_key = os.getenv("GOOGLE_API_KEY", "")
            elif provider == "deepseek":
                api_key = os.getenv("DEEPSEEK_API_KEY", "")
            elif provider == "groq":
                api_key = os.getenv("GROQ_API_KEY", "")
            elif provider == "together":
                api_key = os.getenv("TOGETHER_API_KEY", "")
            else:
                api_key = os.getenv(f"{provider.upper()}_API_KEY", "")
        
        if not api_key:
            raise ValueError(f"API key required for {provider}. Set {provider.upper()}_API_KEY environment variable or pass api_key parameter.")
        
        # Default model if not specified
        if not model:
            if provider == "openai":
                model = "gpt-4o-mini"
            else:
                raise ValueError(f"Model required for {provider}")
        
        # Initialize provider-specific LLM
        if provider == "openai":
            return ChatOpenAI(
                model=model,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        
        elif provider == "claude":
            try:
                # Import with better error handling
                from langchain_anthropic import ChatAnthropic
            except ImportError as e:
                error_msg = str(e)
                if "ModelProfile" in error_msg or "cannot import name" in error_msg:
                    raise ValueError(
                        f"LangChain version compatibility issue. "
                        f"Try: pip install --upgrade langchain-anthropic langchain-core && restart Flask app. "
                        f"Error: {error_msg}"
                    )
                raise ValueError(f"langchain-anthropic package not installed. Install with: pip install langchain-anthropic. Error: {error_msg}")
            except Exception as e:
                error_msg = str(e)
                if "ModelProfile" in error_msg or "cannot import name" in error_msg:
                    raise ValueError(
                        f"LangChain version compatibility issue. "
                        f"Try: pip install --upgrade langchain-anthropic langchain-core && restart Flask app. "
                        f"Error: {error_msg}"
                    )
                raise ValueError(f"Failed to import ChatAnthropic: {error_msg}")
            
            try:
                return ChatAnthropic(
                    model=model,
                    api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            except Exception as e:
                # Provide more helpful error message
                error_msg = str(e)
                if "ModelProfile" in error_msg or "cannot import name" in error_msg:
                    raise ValueError(
                        f"LangChain version compatibility issue detected during initialization. "
                        f"Please run: pip install --upgrade langchain-anthropic langchain-core "
                        f"and restart your Flask application. "
                        f"Error: {error_msg}"
                    )
                raise ValueError(f"Failed to initialize Claude LLM: {error_msg}")
        
        elif provider == "gemini":
            # TODO: Implement when langchain-google-genai is added
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=model,
                google_api_key=api_key,
                temperature=temperature,
                max_output_tokens=max_tokens,
                **kwargs
            )
        
        elif provider == "deepseek":
            # Uses OpenAI-compatible API
            return ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url="https://api.deepseek.com/v1",
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        
        elif provider == "groq":
            # TODO: Implement when langchain-groq is added
            from langchain_groq import ChatGroq
            return ChatGroq(
                model=model,
                groq_api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        
        elif provider == "together":
            # TODO: Implement when langchain-together is added
            from langchain_together import Together
            return Together(
                model=model,
                together_api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        
        else:
            raise ValueError(f"Unsupported provider: {provider}. Supported: openai, claude, gemini, deepseek, groq, together")
    
    @staticmethod
    def get_default_llm(temperature=0.3, max_tokens=2000, **kwargs):
        """
        Get default LLM (OpenAI) with system configuration
        
        Args:
            temperature: Temperature for response (0.0-2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters
        
        Returns:
            LangChain LLM instance (OpenAI)
        """
        return LLMProvider.get_llm(
            provider="openai",
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY", ""),
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

