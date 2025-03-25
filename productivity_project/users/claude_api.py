import os
import anthropic
from django.conf import settings

class ClaudeAIClient:
    """Client for interacting with Claude AI API."""
    
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=settings.CLAUDE_API_KEY,
        )
        self.model = settings.CLAUDE_MODEL
        self.max_tokens = settings.CLAUDE_MAX_TOKENS
    
    def generate_response(self, prompt, system_prompt=None):
        """Generate a response from Claude based on the given prompt."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            # Log error but don't expose API issues to users
            print(f"Claude API error: {e}")
            return "I'm unable to provide insights at the moment. Please try again later."