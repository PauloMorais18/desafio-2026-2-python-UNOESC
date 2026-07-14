"""Unit tests for document text extraction and chunking."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from app.services.document_ingestion_service import DocumentIngestionService, extract_text, split_text


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


if __name__ == "__main__":
    unittest.main()
