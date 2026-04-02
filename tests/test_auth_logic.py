"""
test_auth_logic.py
Tests for pure authentication logic in auth_logic.py.
No Tkinter/display/database needed — runs in any environment.
using pytest framework. running command: pytest tests/test_auth_logic.py
"""

import pytest

from checkers.auth.auth_logic import (
    validate_password_policy,
    validate_email,
    validate_username,
    validate_login_fields,
    validate_register_fields,
)

# ==========================================================================
#                          Password Policy Tests
# ==========================================================================

class TestPasswordPolicy:

    # Valid password passes all requirements
    def test_valid_password_passes(self) -> None:
        assert validate_password_policy("Test@1234") is None

    # Password too short
    def test_password_too_short(self) -> None:
        error = validate_password_policy("Ab@1")
        assert error is not None
        assert "8" in error

    # Missing uppercase
    def test_password_missing_uppercase(self) -> None:
        error = validate_password_policy("test@1234")
        assert error is not None
        assert "uppercase" in error

    # Missing lowercase
    def test_password_missing_lowercase(self) -> None:
        error = validate_password_policy("TEST@1234")
        assert error is not None
        assert "lowercase" in error

    # Missing number
    def test_password_missing_number(self) -> None:
        error = validate_password_policy("Test@abcd")
        assert error is not None
        assert "number" in error

    # Missing special character
    def test_password_missing_special_character(self) -> None:
        error = validate_password_policy("Test12345")
        assert error is not None
        assert "special" in error

    # Exactly minimum length passes if other requirements met
    def test_password_exact_minimum_length(self) -> None:
        assert validate_password_policy("Test@12A") is None

    # Password below minimum length fails even with all other criteria
    def test_password_short_with_all_criteria(self) -> None:
        error = validate_password_policy("T@1a")
        assert error is not None

# ==========================================================================
#                          Email Validation Tests
# ==========================================================================

class TestEmailValidation:

    # Valid email passes
    def test_valid_email(self) -> None:
        assert validate_email("user@example.com") is True

    # Missing @ sign fails
    def test_email_missing_at(self) -> None:
        assert validate_email("userexample.com") is False

    # Missing domain dot fails
    def test_email_missing_dot(self) -> None:
        assert validate_email("user@examplecom") is False

    # Valid email passes
    def test_email_empty(self) -> None:
        assert validate_email("") is False

# ==========================================================================
#                          Username Validation Tests
# ==========================================================================

class TestUsernameValidation:

    # Valid username passes
    def test_valid_username(self) -> None:
        assert validate_username("piper123") is None

    # Username too short
    def test_username_too_short(self) -> None:
        error = validate_username("ab")
        assert error is not None

    # Username with special characters fails
    def test_username_with_special_chars(self) -> None:
        error = validate_username("user@name")
        assert error is not None

    # Username with spaces fails
    def test_username_with_spaces(self) -> None:
        error = validate_username("user name")
        assert error is not None

    # Minimum valid length (3 chars) passes
    def test_username_minimum_length(self) -> None:
        assert validate_username("abc") is None

# ==========================================================================
#                          Login Field Validation Tests
# ==========================================================================

class TestLoginFieldValidation:

    # Both fields filled — no error
    def test_both_fields_filled(self) -> None:
        assert validate_login_fields("testuser", "Test@1234") is None

    # Empty username returns error
    def test_empty_username(self) -> None:
        error = validate_login_fields("", "Test@1234")
        assert error is not None

    # Empty password returns error
    def test_empty_password(self) -> None:
        error = validate_login_fields("testuser", "")
        assert error is not None

    # Both fields empty returns error
    def test_both_fields_empty(self) -> None:
        error = validate_login_fields("", "")
        assert error is not None

    #  Whitespace-only username treated as empty
    def test_whitespace_username(self) -> None:
        error = validate_login_fields("   ", "Test@1234")
        assert error is not None

# ==========================================================================
#                          Register Field Validation Tests
# ==========================================================================

class TestRegisterFieldValidation:

    # All valid fields — no error
    def test_all_valid_fields(self) -> None:
        error = validate_register_fields(
            "newuser", "new@email.com", "Test@1234", "Test@1234"
        )
        assert error is None

    # Any empty field returns error
    def test_empty_username(self) -> None:
        error = validate_register_fields("", "new@email.com", "Test@1234", "Test@1234")
        assert error is not None

    def test_empty_email(self) -> None:
        error = validate_register_fields("newuser", "", "Test@1234", "Test@1234")
        assert error is not None

    def test_empty_password(self) -> None:
        error = validate_register_fields("newuser", "new@email.com", "", "Test@1234")
        assert error is not None

    def test_empty_confirm(self) -> None:
        error = validate_register_fields("newuser", "new@email.com", "Test@1234", "")
        assert error is not None

    # Passwords do not match
    def test_passwords_do_not_match(self) -> None:
        error = validate_register_fields(
            "newuser", "new@email.com", "Test@1234", "Different@1234"
        )
        assert error is not None
        assert "match" in error

    # Invalid email format
    def test_invalid_email(self) -> None:
        error = validate_register_fields(
            "newuser", "invalidemail", "Test@1234", "Test@1234"
        )
        assert error is not None

    # Short username
    def test_short_username(self) -> None:
        error = validate_register_fields(
            "ab", "new@email.com", "Test@1234", "Test@1234"
        )
        assert error is not None

    # Weak password fails
    def test_weak_password(self) -> None:
        error = validate_register_fields(
            "newuser", "new@email.com", "weak", "weak"
        )
        assert error is not None

    # Password mismatch checked before policy
    def test_mismatch_checked_before_policy(self) -> None:
        # Both passwords are weak AND don't match -> report mismatch first
        error = validate_register_fields(
            "newuser", "new@email.com", "weak1", "weak2"
        )
        assert "match" in error
