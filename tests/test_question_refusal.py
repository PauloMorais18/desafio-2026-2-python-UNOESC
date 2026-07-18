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

    def test_general_subject_without_source_uses_support(self) -> None:
        answer, error, status = QuestionService._resolve_answer(
            "Qual é a previsão do tempo?", "", False,
            requires_institutional_context=False,
        )
        self.assertEqual(answer, OUT_OF_SCOPE_RESPONSE)
        self.assertIn("WhatsApp", answer)
        self.assertIsNone(error)
        self.assertEqual(status, "sem_resposta")

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

    def test_matricula_typo_from_chat_is_corrected_before_search(self) -> None:
        normalized = QuestionService._normalize_institutional_query(
            "quero fazer minha maticula"
        )
        self.assertIn("matricula", normalized.split())
        self.assertTrue(QuestionService._requires_institutional_context(normalized))

    def test_rematricula_intent_is_mapped_without_exact_keyword(self) -> None:
        normalized = QuestionService._normalize_institutional_query(
            "como faco para me inscrever novamente?"
        )
        self.assertIn("rematricula", normalized.split())
        self.assertTrue(QuestionService._requires_institutional_context(normalized))
    def test_extractive_fallback_distinguishes_matricula_and_rematricula(self) -> None:
        context = (
            "A matrícula inicial é realizada online. "
            "A rematrícula ocorre semestralmente conforme calendário acadêmico. "
            "O aluno seleciona disciplinas, confirma a grade e finaliza o processo."
        )
        initial = QuestionService._extract_grounded_answer(
            "quero fazer minha maticula", context
        )
        renewal = QuestionService._extract_grounded_answer(
            "como faço para me inscrever novamente?", context
        )
        self.assertIn("1. Início online: A matrícula inicial é realizada online.", initial)
        self.assertIn("A base institucional não identifica o portal", initial)
        self.assertNotIn("PDF", initial)
        self.assertNotIn("página", initial.lower())
        self.assertIn("1. Período da rematrícula", renewal)
        self.assertIn("2. Seleção das disciplinas", renewal)
        self.assertIn("Finalize o processo", renewal)

    def test_refazer_matricula_is_understood_as_rematricula(self) -> None:
        normalized = QuestionService._normalize_institutional_query(
            "me de o passo a passo para refazer a matricula"
        )
        self.assertIn("rematricula", normalized.split())
        self.assertNotIn("matricula", normalized.split())
    def test_short_follow_up_uses_latest_user_message_from_same_chat(self) -> None:
        history = [
            SimpleNamespace(message_type=1, content="como faço minha matrícula?"),
            SimpleNamespace(message_type=2, content="A matrícula inicial é online."),
        ]
        contextualized = QuestionService._contextualize_question(
            "consegue ser mais detalhado?", history
        )
        self.assertIn("matrícula", contextualized)
        self.assertIn("mais detalhado", contextualized)
        self.assertTrue(QuestionService._requires_institutional_context(contextualized))

    def test_unrelated_question_does_not_inherit_previous_subject(self) -> None:
        history = [SimpleNamespace(message_type=1, content="como faço minha matrícula?")]
        contextualized = QuestionService._contextualize_question(
            "qual é a previsão do tempo?", history
        )
        self.assertEqual(contextualized, "qual é a previsão do tempo?")
    def test_grounding_gate_rejects_verbose_hallucination(self) -> None:
        context = "A matrícula inicial é realizada online."
        invented = "Para fazer a matrícula, entregue CPF, agende uma reunião e aguarde um e-mail."
        self.assertFalse(QuestionService._answer_is_grounded(invented, context))
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
