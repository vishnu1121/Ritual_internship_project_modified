"""
Response Templates Module

This module provides templates for generating consistent responses to user commands.
Templates are defined for various command outcomes and error conditions.
"""

import logging
import string
from enum import Enum
from typing import Dict, Optional, Any, Final

logger = logging.getLogger(__name__)

# Constants
DEFAULT_TEMPLATE: Final[str] = "Operation completed successfully."


class TemplateError(Exception):
    """Raised when template formatting fails."""
    pass


class ResponseType(str, Enum):
    """Enum for different response types.
    
    Attributes:
        SUCCESS: Successful operation response
        ERROR: Error condition response
        INFO: Informational response
        HELP: Help or guidance response
    """
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    HELP = "help"


class ResponseTemplates:
    """Manages templates for generating consistent responses.
    
    This class provides templates for various command outcomes and
    handles template formatting with provided parameters.
    
    Attributes:
        templates: Dictionary mapping template names to template strings
    """
    
    def __init__(self):
        """Initialize response templates.
        
        Loads default templates for various command outcomes and errors.
        """
        self.templates = self._load_default_templates()
        logger.info("Initialized ResponseTemplates")
    
    def _load_default_templates(self) -> Dict[str, str]:
        """Load default response templates.
        
        Returns:
            Dictionary mapping template names to template strings
            
        Ensures:
            - All required templates are loaded
            - All templates are valid format strings
        """
        templates = {
            # Success templates
            "stake_success": (
                "✅ Successfully staked {amount} {token} with validator {validator}.\n"
                "Transaction hash: {tx_hash}\n"
                "Current position: {position}"
            ),
            "unstake_success": (
                "✅ Successfully unstaked {amount} {token}.\n"
                "Transaction hash: {tx_hash}\n"
                "Remaining balance: {balance}"
            ),
            "compound_success": (
                "🔄 Successfully compounded {amount} {token} in rewards.\n"
                "Transaction hash: {tx_hash}\n"
                "Updated position: {position}"
            ),
            "claim_success": (
                "💰 Successfully claimed {amount} {token} in rewards.\n"
                "Transaction hash: {tx_hash}\n"
                "Sent to address: {address}"
            ),
            
            # Error templates
            "insufficient_balance": (
                "❌ Insufficient balance for {action}.\n"
                "Required: {required} {token}\n"
                "Available: {available} {token}"
            ),
            "invalid_amount": (
                "❌ Invalid amount specified.\n"
                "Amount must be between {min_amount} and {max_amount} {token}"
            ),
            "invalid_validator": (
                "❌ Invalid validator address: {validator}\n"
                "Please provide a valid validator address"
            ),
            
            # Info templates
            "position_info": (
                "📊 Current Staking Position:\n"
                "Staked: {staked} {token}\n"
                "Validator: {validator}\n"
                "Pending Rewards: {rewards} {token}\n"
                "Current APR: {apr}%"
            ),
            "help": (
                "🤖 Available Commands:\n"
                "- stake <amount> <token> with validator <address>\n"
                "- unstake <amount> <token>\n"
                "- compound rewards\n"
                "- claim rewards\n"
                "- view staking position"
            )
        }
        
        # Validate all templates
        for name, template in templates.items():
            try:
                # Only validate format string syntax, not parameter presence
                formatter = string.Formatter()
                list(formatter.parse(template))
            except Exception as e:
                logger.error(f"Invalid template {name}: {str(e)}")
                raise ValueError(f"Invalid template {name}: {str(e)}")
        
        logger.debug(f"Loaded {len(templates)} templates")
        return templates
    
    def get_template(self, template_name: str) -> Optional[str]:
        """Get a template by name.
        
        Args:
            template_name: Name of the template to retrieve
            
        Returns:
            Template string if found, None otherwise
            
        Requires:
            template_name is not None
        """
        if template_name is None:
            raise ValueError("Template name cannot be None")
            
        template = self.templates.get(template_name)
        if template is None:
            logger.warning(f"Template not found: {template_name}")
        return template
    
    def format_response(self, template_name: str, **kwargs: Any) -> str:
        """Format a response using a template and parameters.
        
        Args:
            template_name: Name of the template to use
            **kwargs: Parameters to format the template with
            
        Returns:
            Formatted response string
            
        Raises:
            TemplateError: If template formatting fails
            ValueError: If template does not exist
        """
        template = self.get_template(template_name)
        if template is None:
            raise ValueError(f"Template not found: {template_name}")

        try:
            # Check for required parameters
            required_params = {p[1] for p in string.Formatter().parse(template) if p[1] is not None}
            missing_params = required_params - set(kwargs.keys())
            
            if missing_params:
                raise TemplateError(f"Missing required parameters: {', '.join(missing_params)}")
                
            logger.debug(f"Formatting template {template_name} with params: {kwargs}")
            response = template.format(**kwargs)
            logger.debug(f"Formatted response: {response}")
            return response

        except KeyError as e:
            logger.error(f"Missing required parameter: {str(e)}")
            raise TemplateError(f"Missing required parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to format template: {str(e)}")
            raise TemplateError(f"Failed to format template: {str(e)}")
