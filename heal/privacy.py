"""
Privacy module for anonymizing sensitive data before sending to LLM.

This module provides functionality to mask sensitive information like:
- Personal names (PERSNAME)
- Dates (DATE)
- Contact information (email, phone)
- Addresses (ADDRESS)
- ID numbers (PESEL, etc.)
- Amounts (AMOUNT)
"""

import re
from typing import Optional, Dict, Any

# Check if priv-masker is available
PRIV_MASKER_AVAILABLE = False
try:
    import spacy
    from priv_masker import add_pipeline, analyse_text
    PRIV_MASKER_AVAILABLE = True
except ImportError:
    pass


class PrivacyMasker:
    """Handles anonymization of sensitive data in text."""
    
    def __init__(self, language: str = "pl"):
        """
        Initialize the privacy masker.
        
        Args:
            language: Language code (default: "pl" for Polish)
        """
        self.language = language
        self.nlp = None
        self.enabled = False
        
        if PRIV_MASKER_AVAILABLE:
            try:
                # Try to load the Polish model
                if language == "pl":
                    self.nlp = spacy.load("pl_nask")
                    add_pipeline(self.nlp)
                    self.enabled = True
            except OSError:
                # Model not installed
                pass
    
    def is_available(self) -> bool:
        """Check if privacy masking is available."""
        return self.enabled
    
    def get_install_instructions(self) -> str:
        """Get installation instructions for privacy masking."""
        if not PRIV_MASKER_AVAILABLE:
            return """Privacy masking not available. Install with:
    pip install heal[privacy]
    python -m spacy download pl_nask-0.0.5"""
        elif not self.enabled:
            return """SpaCy model not installed. Install with:
    python -m spacy download pl_nask-0.0.5"""
        return ""
    
    def anonymize(
        self,
        text: str,
        mask_names: bool = True,
        mask_dates: bool = True,
        mask_contacts: bool = True,
        mask_addresses: bool = True,
        mask_ids: bool = True,
        mask_amounts: bool = False,
    ) -> str:
        """
        Anonymize sensitive data in text.
        
        Args:
            text: Input text to anonymize
            mask_names: Mask personal names
            mask_dates: Mask dates
            mask_contacts: Mask email and phone numbers
            mask_addresses: Mask addresses
            mask_ids: Mask ID numbers (PESEL, etc.)
            mask_amounts: Mask monetary amounts
            
        Returns:
            Anonymized text with sensitive data masked
        """
        if not self.enabled:
            # Fallback to basic regex-based masking
            return self._basic_anonymize(text, mask_contacts, mask_ids)
        
        # Use priv-masker for advanced anonymization
        masked_components = {
            'persname_mask': mask_names,
            'date_mask': mask_dates,
            'contact_mask': mask_contacts,
            'address_mask': mask_addresses,
            'id_numbers_mask': mask_ids,
            'amount_mask': mask_amounts,
        }
        
        doc = self.nlp(text)
        anonymized = analyse_text(doc, masked_components)
        return anonymized
    
    def _basic_anonymize(
        self,
        text: str,
        mask_contacts: bool = True,
        mask_ids: bool = True,
    ) -> str:
        """
        Basic regex-based anonymization (fallback when priv-masker not available).
        
        Args:
            text: Input text
            mask_contacts: Mask email and phone
            mask_ids: Mask ID-like numbers
            
        Returns:
            Text with basic masking applied
        """
        result = text
        
        if mask_contacts:
            # Mask emails
            result = re.sub(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                '[EMAIL]',
                result
            )
            
            # Mask phone numbers (various formats)
            result = re.sub(
                r'\b(?:\+?48)?[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{3}\b',
                '[PHONE]',
                result
            )
            result = re.sub(
                r'\b\d{3}[-\s]?\d{3}[-\s]?\d{4}\b',
                '[PHONE]',
                result
            )
        
        if mask_ids:
            # Mask PESEL (11 digits)
            result = re.sub(
                r'\b\d{11}\b',
                '[ID_NUMBER]',
                result
            )
            
            # Mask credit card numbers
            result = re.sub(
                r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
                '[CARD_NUMBER]',
                result
            )
        
        return result


def anonymize_shell_output(
    output: str,
    enable_privacy: bool = False,
    **mask_options
) -> str:
    """
    Anonymize shell output before sending to LLM.
    
    Args:
        output: Shell command output
        enable_privacy: Whether to enable privacy masking
        **mask_options: Options for what to mask (mask_names, mask_dates, etc.)
        
    Returns:
        Anonymized output or original if privacy is disabled
    """
    if not enable_privacy:
        return output
    
    masker = PrivacyMasker()
    
    if not masker.is_available():
        # Use basic masking as fallback
        return masker._basic_anonymize(output)
    
    return masker.anonymize(output, **mask_options)


def get_privacy_status() -> Dict[str, Any]:
    """
    Get privacy masking availability status.
    
    Returns:
        Dictionary with status information
    """
    masker = PrivacyMasker()
    
    return {
        'available': masker.is_available(),
        'priv_masker_installed': PRIV_MASKER_AVAILABLE,
        'model_loaded': masker.enabled,
        'install_instructions': masker.get_install_instructions() if not masker.is_available() else None,
    }
