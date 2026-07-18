"""Unit tests for document text extraction and chunking."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from app.services.document_ingestion_service import DocumentIngestionService, extract_text, split_text
from app.services.embedding_service import cosine_similarity


class DocumentIngestionTests(unittest.TestCase):
    def test_extracts_utf8_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "contexto.txt"
            path.write_text("Matrícula disponível no portal acadêmico.", encoding="utf-8")
            self.assertIn("Matrícula", extract_text(path))

    def test_splits_long_text_with_overlap(self) -> None:
        text = " ".join(f"Informação acadêmica número {index}." for index in range(250))
        chunks = split_text(text, chunk_size=500, overlap=80)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunk.strip() for chunk in chunks))
        self.assertTrue(all(len(chunk) <= 500 for chunk in chunks))

    def test_indexes_only_documents_not_already_active(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "novo.txt").write_text("Conteúdo novo", encoding="utf-8")
            (root / "existente.txt").write_text("Conteúdo existente", encoding="utf-8")
            service = DocumentIngestionService(MagicMock())
            service.has_active_chunks = MagicMock(side_effect=lambda name: name == "existente.txt")
            service.index = MagicMock(return_value=1)

            indexed = service.index_missing(root, {".txt"})

            self.assertEqual(indexed, {"novo.txt": 1})
            service.index.assert_called_once_with(root / "novo.txt")

    def test_pdf_pages_are_separated_and_repeated_boilerplate_is_deduplicated(self) -> None:
        text = (
            "Página inicial. Texto repetido.\f"
            "Segunda seção. Texto repetido. Informação exclusiva."
        )
        chunks = split_text(text, chunk_size=1600, overlap=0)
        self.assertEqual(len(chunks), 2)
        self.assertTrue(chunks[0].startswith("Página 1"))
        self.assertTrue(chunks[1].startswith("Página 2"))
        self.assertEqual(" ".join(chunks).count("Texto repetido."), 1)
        self.assertIn("Informação exclusiva.", chunks[1])
    def test_cosine_similarity_ranks_related_vectors(self) -> None:
        self.assertAlmostEqual(cosine_similarity([1.0, 0.0], [1.0, 0.0]), 1.0)
        self.assertAlmostEqual(cosine_similarity([1.0, 0.0], [0.0, 1.0]), 0.0)
        self.assertEqual(cosine_similarity([1.0], [1.0, 2.0]), 0.0)


if __name__ == "__main__":
    unittest.main()
