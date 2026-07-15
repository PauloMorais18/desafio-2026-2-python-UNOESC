"""Tests for deterministic refusal outside the knowledge base."""

import unittest
from math import sqrt
from types import SimpleNamespace
from unittest.mock import patch

from app.repositories.conhecimento_repository import KnowledgeRepository
from app.services.pergunta_service import OUT_OF_SCOPE_RESPONSE, QuestionService


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
