"""Tests for the intent recognition module."""

import pytest
from src.staking_optimizer.commands.intents import IntentRecognizer, Intent, IntentClassification


@pytest.fixture
def recognizer():
    """Create an intent recognizer instance."""
    return IntentRecognizer()


def test_intent_enum():
    """Test Intent enum values."""
    assert Intent.STAKE == "stake"
    assert Intent.UNSTAKE == "unstake"
    assert Intent.COMPOUND == "compound"
    assert Intent.CLAIM == "claim"
    assert Intent.VIEW == "view"
    assert Intent.HELP == "help"
    assert Intent.UNKNOWN == "unknown"


def test_intent_classification_model():
    """Test IntentClassification model."""
    classification = IntentClassification(
        intent=Intent.STAKE,
        confidence=0.95,
        parameters={"amount": "100", "token": "ETH"}
    )
    assert classification.intent == Intent.STAKE
    assert classification.confidence == 0.95
    assert classification.parameters == {"amount": "100", "token": "ETH"}


@pytest.mark.asyncio
async def test_recognize_stake_intent(recognizer):
    """Test recognizing stake intent."""
    text = "I want to stake 100 ETH with validator 0x123"
    result = await recognizer.recognize_intent(text)
    assert result.intent == Intent.STAKE
    assert result.confidence > 0.8
    assert "amount" in result.parameters
    assert "token" in result.parameters
    assert "validator" in result.parameters


@pytest.mark.asyncio
async def test_recognize_unstake_intent(recognizer):
    """Test recognizing unstake intent."""
    text = "unstake 50 ETH please"
    result = await recognizer.recognize_intent(text)
    assert result.intent == Intent.UNSTAKE
    assert result.confidence > 0.8
    assert "amount" in result.parameters
    assert "token" in result.parameters


@pytest.mark.asyncio
async def test_recognize_compound_intent(recognizer):
    """Test recognizing compound intent."""
    text = "compound my staking rewards"
    result = await recognizer.recognize_intent(text)
    assert result.intent == Intent.COMPOUND
    assert result.confidence > 0.8


@pytest.mark.asyncio
async def test_recognize_claim_intent(recognizer):
    """Test recognizing claim intent."""
    text = "claim my rewards"
    result = await recognizer.recognize_intent(text)
    assert result.intent == Intent.CLAIM
    assert result.confidence > 0.8


@pytest.mark.asyncio
async def test_recognize_view_intent(recognizer):
    """Test recognizing view intent."""
    text = "show me my staking position"
    result = await recognizer.recognize_intent(text)
    assert result.intent == Intent.VIEW
    assert result.confidence > 0.8


@pytest.mark.asyncio
async def test_recognize_help_intent(recognizer):
    """Test recognizing help intent."""
    text = "help me understand staking"
    result = await recognizer.recognize_intent(text)
    assert result.intent == Intent.HELP
    assert result.confidence > 0.8


@pytest.mark.asyncio
async def test_recognize_unknown_intent(recognizer):
    """Test recognizing unknown intent."""
    text = "completely unrelated query about weather"
    result = await recognizer.recognize_intent(text)
    assert result.intent == Intent.UNKNOWN
    assert result.confidence < 0.5


@pytest.mark.asyncio
async def test_parameter_extraction(recognizer):
    """Test parameter extraction from different intents."""
    # Test stake parameters
    stake_text = "stake 100.5 ETH with validator 0x123"
    stake_result = await recognizer.recognize_intent(stake_text)
    assert float(stake_result.parameters["amount"]) == 100.5
    assert stake_result.parameters["token"] == "ETH"
    assert stake_result.parameters["validator"] == "0x123"
    
    # Test unstake parameters
    unstake_text = "unstake half of my ETH"
    unstake_result = await recognizer.recognize_intent(unstake_text)
    assert "amount" in unstake_result.parameters
    assert unstake_result.parameters["token"] == "ETH"
