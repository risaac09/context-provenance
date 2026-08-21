import json
import tempfile
import unittest
from pathlib import Path

from provenance.analyzer import analyze_transcript
from provenance.channels import ChannelType


class AnalyzerTests(unittest.TestCase):
    def test_jsonl_classifies_tools_deduplicates_files_and_adds_training(self):
        rows = [
            {
                "timestamp": "2026-08-21T12:00:00Z",
                "content": "Read `/tmp/notes.md` before continuing.",
                "tool_calls": [
                    {"name": "read_file", "input": {"path": "/tmp/notes.md"}},
                    {"name": "web_search", "input": {"query": "source", "url": "https://example.com"}},
                    {"name": "memory_search", "input": {"query": "prior session"}},
                    {"name": "load_skill", "input": {"skill": "source-check"}},
                ],
            }
        ]
        with tempfile.TemporaryDirectory() as raw_tmp:
            transcript = Path(raw_tmp) / "conversation.jsonl"
            transcript.write_text("\n".join(json.dumps(row) for row in rows))
            record = analyze_transcript(str(transcript), title="Test", author="A")

        self.assertEqual(record.created, "2026-08-21")
        self.assertEqual(
            [s.label for s in record.channels[ChannelType.RETRIEVED].sources].count("notes.md"),
            1,
        )
        self.assertEqual(len(record.channels[ChannelType.SKILL].sources), 1)
        self.assertEqual(len(record.channels[ChannelType.CONVERSATION].sources), 1)
        training = record.channels[ChannelType.TRAINING].sources
        self.assertEqual(len(training), 1)
        self.assertFalse(training[0].retrievable)

    def test_structured_content_does_not_crash_analysis(self):
        with tempfile.TemporaryDirectory() as raw_tmp:
            transcript = Path(raw_tmp) / "conversation.json"
            transcript.write_text(json.dumps({"messages": [{"content": {"text": "hello"}}]}))
            record = analyze_transcript(str(transcript))

        self.assertEqual(record.total_sources, 1)
        self.assertEqual(record.retrievable_sources, 0)


if __name__ == "__main__":
    unittest.main()
