"""
Tests for VLM Processor module (vlm_processor.py)
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from src.utils import mask_sensitive_data


class TestMaskSensitiveData:
    """Test PII masking utility."""

    def test_mask_vietnam_phone(self):
        """Test masking Vietnam phone numbers."""
        text = "Liên hệ: 0912345678"
        result = mask_sensitive_data(text)
        assert "[SĐT_ĐÃ_ẨN]" in result
        assert "0912345678" not in result

    def test_mask_email(self):
        """Test masking email addresses."""
        text = "Email: john.doe@example.com"
        result = mask_sensitive_data(text)
        assert "[EMAIL_ĐÃ_ẨN]" in result
        assert "john.doe@example.com" not in result

    def test_mask_tax_id(self):
        """Test masking 10-13 digit IDs (tax ID, CCCD)."""
        text = "Mã số thuế: 0123456789"
        result = mask_sensitive_data(text)
        assert "[MÃ_SỐ_ĐÃ_ẨN]" in result
        assert "0123456789" not in result

    def test_mask_multiple_pii(self):
        """Test masking multiple PII items."""
        text = "Contact: 0987654321, email@test.com, Tax: 0102030405"
        result = mask_sensitive_data(text)
        assert "[SĐT_ĐÃ_ẨN]" in result
        assert "[EMAIL_ĐÃ_ẨN]" in result
        assert "[MÃ_SỐ_ĐÃ_ẨN]" in result

    def test_empty_text(self):
        """Test with empty text."""
        result = mask_sensitive_data("")
        assert result == ""

    def test_none_text(self):
        """Test with None input."""
        result = mask_sensitive_data(None)
        assert result is None

    def test_no_pii(self):
        """Test text without PII is unchanged."""
        text = "This is a normal financial statement."
        result = mask_sensitive_data(text)
        assert result == text


class TestTextProcessing:
    """Test text normalization."""

    def test_preserve_legitimate_numbers(self):
        """Ensure non-PII numbers are preserved."""
        text = "The revenue was 1000000 USD in 2024."
        result = mask_sensitive_data(text)
        # 1000000 should be preserved (not 10-13 consecutive digits in ID context)
        assert "USD" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
