import openai
import traceback
from config import API_KEY

class SummarizerError(Exception):
    """Custom exception for Shortify processing errors."""
    pass

def summarize_text(text, max_length=150, min_length=100, style="default"):
    """
    Summarizes the selected text using the OpenAI API.
    
    Args:
        text (str): Text to summarize
        max_length (int): Maximum summary length
        min_length (int): Minimum summary length
        style (str): Writing style for the summary
    
    Returns:
        str: Summarized text
    """
    try:
        # Validate input
        if not text or len(text.strip()) < 50:
            raise SummarizerError("Text is too short to summarize.")
            
        # Define style instructions
        style_instructions = {
            "default": "Provide a clear and concise summary",
            "academic": "Provide a formal academic summary with structured points and technical language",
            "casual": "Provide a casual, conversational summary in simple language",
            "business": "Provide a professional business-oriented summary focusing on key actionable insights",
            "creative": "Provide a creative and engaging summary with vivid language"
        }
        
        style_instruction = style_instructions.get(style, style_instructions["default"])

        client = openai.OpenAI(api_key=API_KEY)
        response = client.chat.completions.create(
            model="gpt-4.5-preview",
            messages=[
                {
                    "role": "system", 
                    "content": f"{style_instruction} between {min_length}-{max_length} words. Capture the key points and main ideas."
                },
                {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
            ],
            max_tokens=500,
            temperature=0.7
        )
        summary = response.choices[0].message.content.strip()
        
        # Additional validation
        if len(summary) < min_length:
            raise SummarizerError("Generated summary is too short.")
        
        return summary
    
    except SummarizerError as e:
        return f"Summarization Error: {str(e)}"
    except Exception as e:
        traceback.print_exc()
        return f"Unexpected Error: {str(e)}"

def summarize_code(code, max_length=150, language=None):
    """
    Summarizes code snippets with language-specific handling.
    
    Args:
        code (str): Code to summarize
        max_length (int): Maximum summary length in words
        language (str): Programming language of the code (if known)
    
    Returns:
        str: Summarized explanation of the code
    """
    try:
        # Validate input
        if not code or len(code.strip()) < 20:
            raise SummarizerError("Code snippet is too short to summarize.")
        
        # If language is not specified, attempt to detect it
        language_prompt = f"The code is written in {language}." if language else "Detect the programming language and note it in your response."
        
        client = openai.OpenAI(api_key=API_KEY)
        response = client.chat.completions.create(
            model="gpt-4.5-preview",
            messages=[
                {
                    "role": "system", 
                    "content": f"You are a code analysis expert. {language_prompt} Provide a clear, concise explanation of what this code does in {max_length} words or less. Focus on the overall purpose, key functions, and important logic. Include any important edge cases or potential issues."
                },
                {"role": "user", "content": f"Summarize this code:\n\n```\n{code}\n```"}
            ],
            max_tokens=500,
            temperature=0.7
        )
        summary = response.choices[0].message.content.strip()
        
        return summary
    
    except SummarizerError as e:
        return f"Code Summarization Error: {str(e)}"
    except Exception as e:
        traceback.print_exc()
        return f"Unexpected Error: {str(e)}"

def paraphrase_text(text, max_length=200, min_length=100, style="default"):
    """
    Paraphrases the selected text using the OpenAI API.
    
    Args:
        text (str): Text to paraphrase
        max_length (int): Maximum paraphrase length
        min_length (int): Minimum paraphrase length
        style (str): Writing style for the paraphrase
    
    Returns:
        str: Paraphrased text
    """
    try:
        # Validate input
        if not text or len(text.strip()) < 20:
            raise SummarizerError("Text is too short to paraphrase.")
            
        # Define style instructions
        style_instructions = {
            "default": "Rewrite this text in a clear and concise manner",
            "academic": "Rewrite this text in a formal academic style with technical language",
            "casual": "Rewrite this text in a casual, conversational tone with simple language",
            "business": "Rewrite this text in a professional business style",
            "creative": "Rewrite this text in a creative and engaging style with vivid language"
        }
        
        style_instruction = style_instructions.get(style, style_instructions["default"])

        client = openai.OpenAI(api_key=API_KEY)
        response = client.chat.completions.create(
            model="gpt-4.5-preview",
            messages=[
                {
                    "role": "system", 
                    "content": f"{style_instruction}. The output should be between {min_length}-{max_length} words while preserving the original meaning."
                },
                {"role": "user", "content": f"Paraphrase the following text:\n\n{text}"}
            ],
            max_tokens=500,
            temperature=0.7
        )
        paraphrased = response.choices[0].message.content.strip()
        
        # Additional validation
        if len(paraphrased) < min_length:
            raise SummarizerError("Generated paraphrase is too short.")
        
        return paraphrased
    
    except SummarizerError as e:
        return f"Paraphrasing Error: {str(e)}"
    except Exception as e:
        traceback.print_exc()
        return f"Unexpected Error: {str(e)}"