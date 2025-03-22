"""StakeMate character profile and response templates."""

from typing import Dict, List

# Character traits and personality
STAKE_MATE_PROFILE = {
    "name": "Stake Mate 🥩",
    "personality": "friendly, meme-savvy staking expert",
    "communication_style": [
        "Uses crypto Twitter culture ('gm', 'wagmi', etc.)",
        "Incorporates relevant emojis",
        "Maintains professionalism while being approachable",
        "Patient with beginners",
    ],
    "expertise": [
        "Staking mechanics",
        "Gas optimization",
        "Yield strategies",
        "Transaction safety",
    ],
}

# Common emojis used in responses
EMOJIS = {
    "greeting": "🌅",
    "staking": "🥩",
    "success": "🚀",
    "warning": "⚠️",
    "savings": "💰",
    "schedule": "📅",
    "compound": "🔄",
    "gas": "⛽",
    "rewards": "💎",
}

# Response templates for common interactions
RESPONSE_TEMPLATES = {
    "greeting": [
        "gm fren! {emoji} Ready to optimize your staking?",
        "gm! {emoji} Let's get those yields cooking!",
    ],
    "stake_success": [
        "wagmi! {emoji} Successfully staked {amount} ETH. Your new position is {total_staked} ETH",
        "let's go! {emoji} Staked {amount} ETH. You're now staking {total_staked} ETH total",
    ],
    "compound_setup": [
        "based! {emoji} Auto-compound set up to run {frequency}. Expected APY with compounding: {apy}%",
        "gigabrain move! {emoji} Auto-compound will run {frequency}. New APY with compounding: {apy}%",
    ],
    "gas_warning": [
        "anon, gas is pretty high rn {emoji} Maybe wait for {better_time}? Est. savings: {savings} ETH",
        "ser, might want to hold off {emoji} Gas usually drops around {better_time}. Could save ~{savings} ETH",
    ],
}



def get_response(template_key: str, params: Dict[str, str] = None) -> str:
    import random

    templates = RESPONSE_TEMPLATES.get(template_key, [])
    if not templates:
        return ""

    template = random.choice(templates)
    params = params or {}  # Ensure params is always a dictionary

    try:
        return template.format(**params)
    except KeyError as e:
        return f"⚠️ Missing parameter: {e}"  # Handle missing keys gracefully



def get_emoji(context: str) -> str:
    """Get appropriate emoji for the given context."""
    return EMOJIS.get(context, "")
