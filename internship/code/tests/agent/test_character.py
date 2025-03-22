"""Tests for the StakeMate character."""
import pytest

from src.staking_optimizer.agent.character import StakeMateCharacter


@pytest.fixture
def character():
    """Create a StakeMate character instance."""
    return StakeMateCharacter()


def test_format_response_valid_topic(character):
    """Test formatting response for valid topic."""
    response = character.format_response("staking_overview")
    assert "Staking is a way to earn rewards" in response
    assert "Key points:" in response


def test_format_response_invalid_topic(character):
    """Test formatting response for invalid topic."""
    with pytest.raises(ValueError, match="Unknown topic"):
        character.format_response("invalid_topic")


def test_format_apr_recommendation_decrease_significant(character):
    """Test APR recommendation for significant decrease."""
    response = character.format_apr_recommendation(0.03, 0.06)  # 3% vs 6%
    assert "dropped significantly" in response
    assert "Consider reviewing your position" in response


def test_format_apr_recommendation_decrease_minor(character):
    """Test APR recommendation for minor decrease."""
    response = character.format_apr_recommendation(0.049, 0.05)  # 4.9% vs 5%
    assert "decreased slightly" in response
    assert "Continue monitoring" in response


def test_format_apr_recommendation_increase(character):
    """Test APR recommendation for increase."""
    response = character.format_apr_recommendation(0.06, 0.05)  # 6% vs 5%
    assert "Good news!" in response
    assert "increased" in response


def test_format_apr_recommendation_stable(character):
    """Test APR recommendation for stable APR."""
    response = character.format_apr_recommendation(0.05, 0.05)  # 5% vs 5%
    assert "remains stable" in response
