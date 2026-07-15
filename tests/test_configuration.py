"""Validation tests for database-backed runtime settings."""

import unittest
from unittest.mock import MagicMock

from app.services.configuration_service import ConfigurationService


class ConfigurationTests(unittest.TestCase):
    def test_accepts_support_phone_with_country_code(self) -> None:
        values = ConfigurationService._validate({"telefone_suporte_whatsapp": "554935512034"})
        self.assertEqual(values["telefone_suporte_whatsapp"], "554935512034")

    def test_rejects_phone_format_that_cannot_build_wa_link(self) -> None:
        with self.assertRaises(ValueError):
            ConfigurationService._validate({"telefone_suporte_whatsapp": "+55 (49) 3551-2034"})

    def test_inserts_phone_in_out_of_scope_message(self) -> None:
        service = ConfigurationService(MagicMock())
        service.get = MagicMock(side_effect=lambda key: {
            "telefone_suporte_whatsapp": "554935512034",
            "mensagem_fora_escopo": "Fale com o suporte: {telefone}",
        }[key])
        self.assertEqual(service.out_of_scope_message(), "Fale com o suporte: 554935512034")
