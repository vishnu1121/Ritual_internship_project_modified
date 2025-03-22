"""Tests for the SafetyValidator."""
import pytest
from src.staking_optimizer.safety.validator import SafetyValidator


@pytest.fixture
def validator():
    """Create a SafetyValidator instance."""
    return SafetyValidator()


def test_validate_safe_request(validator):
    """Test validation of safe staking-related requests."""
    safe_requests = [
        "stake 100 tokens",
        "compound my rewards",
        "check gas prices",
        "schedule auto-compound",
        "withdraw my balance",
        "what is the current APR?",
        "show my delegation info",
        "monitor my staking returns",
    ]
    for request in safe_requests:
        is_valid, reason = validator.validate_request(request)
        assert is_valid, f"Request '{request}' failed: {reason}"


def test_validate_unsafe_request(validator):
    """Test validation of unsafe requests."""
    unsafe_requests = [
        # System security
        "delete all files",
        "rm -rf /",
        "format disk",
        "sudo command",
        "chmod 777 file",
        "chown user file",
        
        # Malicious intent
        "hack the contract",
        "exploit vulnerability",
        "attack the network",
        "steal funds",
        "install malware",
        "spread virus",
        
        # Smart contract security
        "use reentrancy attack",
        "cause integer overflow",
        "trigger underflow",
        "frontrun transactions",
        "add backdoor",
        
        # Network security
        "launch ddos attack",
        "spoof address",
        "intercept transactions",
        
        # Data security
        "dump all data",
        "leak private key",
        "expose secret key",
    ]
    for request in unsafe_requests:
        is_valid, reason = validator.validate_request(request)
        assert not is_valid, f"Request '{request}' should be blocked but wasn't"
        assert reason != "OK", f"Request '{request}' should have error reason"


def test_validate_irrelevant_request(validator):
    """Test validation of non-staking-related requests."""
    irrelevant_requests = [
        "what's the weather like?",
        "order pizza",
        "play music",
        "send email",
        "browse internet",
    ]
    for request in irrelevant_requests:
        is_valid, reason = validator.validate_request(request)
        assert not is_valid, f"Request '{request}' should be irrelevant but wasn't"
        assert "try to ask me about staking related topics" in reason.lower()


def test_request_length_limit(validator):
    """Test request length validation."""
    # Generate a very long request
    long_request = "stake tokens " * 200
    is_valid, reason = validator.validate_request(long_request)
    assert not is_valid
    assert "too long" in reason.lower()


def test_safety_score(validator):
    """Test safety score calculation."""
    # Test high safety score
    request = "stake 100 tokens and compound rewards when gas is low"
    is_valid, reason = validator.validate_request(request)
    assert is_valid
    assert reason == "OK"
    
    # Test medium safety score (complex request)
    request = "stake 100 tokens " + "and check balance " * 20
    is_valid, reason = validator.validate_request(request)
    assert not is_valid
    assert "safety check" in reason.lower()
    
    # Test low safety score (special characters)
    request = "stake 100 tokens !@#$%^&*()_+" * 5
    is_valid, reason = validator.validate_request(request)
    assert not is_valid
    assert "safety check" in reason.lower()


def test_add_blocked_pattern(validator):
    """Test adding new blocked patterns."""
    # Add new pattern
    validator.add_blocked_pattern(r"(?i)dangerous")
    is_valid, reason = validator.validate_request("this is a dangerous operation")
    assert not is_valid
    assert "blocked pattern" in reason.lower()
    
    # Test duplicate pattern
    original_count = len(validator._blocked_patterns)
    validator.add_blocked_pattern(r"(?i)dangerous")
    assert len(validator._blocked_patterns) == original_count


def test_add_required_keyword(validator):
    """Test adding new required keywords."""
    # Add new keyword
    validator.add_required_keyword("invest")
    is_valid, reason = validator.validate_request("invest in staking")
    assert is_valid
    assert reason == "OK"
    
    # Test duplicate keyword
    original_count = len(validator._required_keywords)
    validator.add_required_keyword("invest")
    assert len(validator._required_keywords) == original_count


def test_mixed_content_validation(validator):
    """Test validation of requests with mixed content."""
    # Safe content with unsafe elements
    request = "stake 100 tokens and hack the network"
    is_valid, reason = validator.validate_request(request)
    assert not is_valid
    assert "blocked pattern" in reason.lower()
    
    # Irrelevant content with staking keywords
    request = "play music while checking stake balance"
    is_valid, reason = validator.validate_request(request)
    assert is_valid  # Should pass because it contains staking keywords
    assert reason == "OK"
