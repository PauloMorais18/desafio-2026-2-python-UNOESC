"""Tests for deterministic refusal outside the knowledge base."""

import unittest
from math import sqrt
from types import SimpleNamespace
from unittest.mock import patch

from app.repositories.conhecimento_repository import KnowledgeRepository
from app.services.pergunta_service import GENERAL_SCOPE_RESPONSE, OUT_OF_SCOPE_RESPONSE, QuestionService


class QuestionRefusalTests(unittest.TestCase):
    def test_does_not_call_llm_without_retrieved_context(self) -> None:
        with patch.object(QuestionService, "_generate_answer") as generate:
            answer, error, status = QuestionService._resolve_answer(
                "Qual é a previsão do tempo?", "", False
            )

        self.assertEqual(answer, OUT_OF_SCOPE_RESPONSE)
        self.assertIsNone(error)
        self.assertEqual(status, "sem_resposta")
        generate.assert_not_called()

    def test_calls_llm_only_when_context_was_found(self) -> None:
        with patch.object(
            QuestionService, "_generate_answer", return_value=("Resposta baseada na fonte.", None)
        ) as generate:
            answer, error, status = QuestionService._resolve_answer(
                "Como faço a matrícula?", "Trecho sobre matrícula", True
            )

        self.assertEqual(answer, "Resposta baseada na fonte.")
        self.assertIsNone(error)
        self.assertEqual(status, "respondida")
        generate.assert_called_once()

    def test_semantic_gate_rejects_weak_textual_coincidence(self) -> None:
        repository = KnowledgeRepository(None)  # type: ignore[arg-type]
        weak = SimpleNamespace(embedding=[0.57, sqrt(1 - 0.57**2)])
        strong = SimpleNamespace(embedding=[0.75, sqrt(1 - 0.75**2)])
        with patch(
            "app.repositories.conhecimento_repository.EmbeddingService.embed_query",
            return_value=[1.0, 0.0],
        ), patch(
            "app.repositories.conhecimento_repository.ConfigurationService.minimum_similarity",
            return_value=0.65,
        ):
            approved = repository._semantic_gate(
                "pergunta do aluno", [(weak, 1.0), (strong, 1.0)]
            )

        self.assertEqual(len(approved), 1)
        self.assertIs(approved[0][0], strong)
        self.assertAlmostEqual(approved[0][1], 0.75)

    def test_strong_literal_match_can_confirm_institutional_source(self) -> None:
        repository = KnowledgeRepository(None)  # type: ignore[arg-type]
        record = SimpleNamespace(embedding=[0.604, sqrt(1 - 0.604**2)])
        with patch(
            "app.repositories.conhecimento_repository.EmbeddingService.embed_query",
            return_value=[1.0, 0.0],
        ), patch(
            "app.repositories.conhecimento_repository.ConfigurationService.minimum_similarity",
            return_value=0.65,
        ):
            approved = repository._semantic_gate(
                "como faço minha matrícula?",
                [(record, 1.0)],
                allow_strong_textual_match=True,
            )
        self.assertEqual(approved, [(record, 1.0)])

    def test_greeting_is_answered_without_support_or_llm(self) -> None:
        greeting = QuestionService._direct_conversation_response("opa")
        with patch.object(QuestionService, "_generate_answer") as generate:
            answer, error, status = QuestionService._resolve_answer(
                "opa", "", False, direct_response=greeting,
                requires_institutional_context=False,
            )
        self.assertIn("Olá", answer)
        self.assertNotIn("554935512034", answer)
        self.assertIsNone(error)
        self.assertEqual(status, "respondida")
        generate.assert_not_called()

    def test_general_subject_does_not_send_user_to_support(self) -> None:
        answer, error, status = QuestionService._resolve_answer(
            "Qual é a previsão do tempo?", "", False,
            requires_institutional_context=False,
        )
        self.assertEqual(answer, GENERAL_SCOPE_RESPONSE)
        self.assertNotIn("WhatsApp", answer)
        self.assertIsNone(error)
        self.assertEqual(status, "respondida")

    def test_institutional_question_without_source_uses_support(self) -> None:
        self.assertTrue(QuestionService._requires_institutional_context("Como faço minha matrícula?"))
        answer, _, status = QuestionService._resolve_answer(
            "Como faço minha matrícula?", "", False,
            requires_institutional_context=True,
        )
        self.assertIn("554935512034", answer)
        self.assertEqual(status, "sem_resposta")

    def test_typo_in_institutional_term_is_corrected_before_search(self) -> None:
        normalized = QuestionService._normalize_institutional_query(
            "como posso fazer minha matrcula?"
        )
        self.assertIn("matricula", normalized.split())
        self.assertTrue(QuestionService._requires_institutional_context(normalized))

    def test_search_fallback_tries_preferred_mode_then_the_other_modes(self) -> None:
        repository = KnowledgeRepository(None)  # type: ignore[arg-type]
        record = SimpleNamespace(id=7)

        def search(_question: str, mode: str, _limit: int):
            return [(record, 1.0)] if mode == "like" else []

        with patch.object(repository, "search", side_effect=search) as mocked_search, patch(
            "app.repositories.conhecimento_repository.ConfigurationService.source_limit",
            return_value=3,
        ):
            matches = repository.search_with_fallback(
                "como posso fazer minha matricula", "embeddings"
            )

        self.assertEqual(matches, [(record, 1.0)])
        self.assertEqual(
            [call.args[1] for call in mocked_search.call_args_list],
            ["embeddings", "like", "full_text"],
        )

    def test_basic_arithmetic_is_answered_without_documents(self) -> None:
        answer = QuestionService._direct_conversation_response("quanto é 2+2?")
        self.assertEqual(answer, "O resultado de 2+2 é 4.")
        self.assertFalse(QuestionService._requires_institutional_context("quanto é 2+2?"))

    def test_conversation_opener_invites_the_actual_question(self) -> None:
        answer = QuestionService._direct_conversation_response("tenho uma dúvida")
        self.assertEqual(answer, "Claro! Pode enviar sua dúvida.")
