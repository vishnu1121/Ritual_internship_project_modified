"""Intent recognition for staking commands."""
import re
from typing import Dict, Optional

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

from .models import Intent, IntentClassification


class IntentRecognizer:
    """Recognizes intents from natural language requests."""

    def __init__(self):
        """Initialize the intent recognizer."""
        self.output_parser = JsonOutputParser()
        self.llm = ChatOpenAI(temperature=0)
        self._setup_prompts()

    def _setup_prompts(self):
        """Set up the prompt templates."""
        template = """
        Classify the intent of the following staking request and extract any relevant parameters.
        The request should be classified into one of the following intents:
        - stake: Request to stake tokens
        - unstake: Request to unstake tokens
        - compound: Request to compound rewards
        - claim: Request to claim rewards
        - view: Request to view staking position
        - help: Request for help or information
        - unknown: Unknown or invalid request (use this with confidence < 0.5 if the request doesn't clearly match any other intent)

        For each intent, extract the following parameters if present:
        - stake: amount (as string), token (string), validator (string)
        - unstake: amount (as string, can be a number or "half" or "all"), token (string)
        - compound: no parameters needed
        - claim: no parameters needed
        - view: no parameters needed
        - help: topic (string, optional)
        - unknown: no parameters needed

        IMPORTANT: All parameter values must be strings, even numbers (e.g. "100.5" not 100.5)

        For your response, output a JSON object with the following structure:
        {{
            "intent": "one of [stake, unstake, compound, claim, view, help, unknown]",
            "confidence": "a float between 0 and 1 indicating confidence in the classification. For unknown intents, use a confidence < 0.5",
            "parameters": {{
                "amount": "string if present",
                "token": "string if present",
                "validator": "string if present",
                "topic": "string if present"
            }}
        }}

        Request: {request}

        {format_instructions}
        """

        self.prompt = PromptTemplate(
            template=template,
            input_variables=["request", "format_instructions"]
        )

    def _extract_parameters(self, text: str) -> Dict[str, str]:
        """Extract parameters from text.
        
        Args:
            text: Text to extract parameters from
            
        Returns:
            Dictionary of extracted parameters
        """
        # Extract amount and token
        amount_match = re.search(r'(\d+(?:\.\d+)?)\s*([A-Za-z]+)', text)
        validator_match = re.search(r'0x[a-fA-F0-9]+', text)
        
        params = {}
        if amount_match:
            params['amount'] = amount_match.group(1)
            params['token'] = amount_match.group(2)
        if validator_match:
            params['validator'] = validator_match.group(0)
            
        return params

    async def recognize_intent(self, text: str) -> IntentClassification:
        """Recognize intent from text.
        
        Args:
            text: Text to recognize intent from
            
        Returns:
            Recognized intent classification
        """
        # Extract parameters
        params = self._extract_parameters(text)
        
        # Format the prompt
        _input = self.prompt.format_prompt(request=text, format_instructions=self.output_parser.get_format_instructions())
        
        # Get the completion
        output = await self.llm.ainvoke(_input.to_string())
        
        # Parse the output
        parsed = self.output_parser.parse(output.content)
        
        # Convert to IntentClassification
        return IntentClassification(
            intent=parsed["intent"],
            parameters=parsed.get("parameters", {}),  # Use parameters from the parsed output
            confidence=parsed["confidence"]
        )
