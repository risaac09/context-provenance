import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
    def test_analyze_writes_json_and_html(self):
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            transcript = tmp / "input.jsonl"
            output = tmp / "record.json"
            transcript.write_text(json.dumps({
                "timestamp": "2026-08-21T00:00:00Z",
                "tool_calls": [{"name": "read_file", "input": {"path": "/tmp/source.md"}}],
            }))

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "provenance",
                    "analyze",
                    str(transcript),
                    "--title",
                    "CLI test",
                    "--author",
                    "Tester",
                    "--output",
                    str(output),
                    "--html",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("Provenance written", result.stdout)
            self.assertTrue(output.is_file())
            self.assertTrue((tmp / "record.html").is_file())
            data = json.loads(output.read_text())
            self.assertEqual(data["context_provenance"]["title"], "CLI test")


if __name__ == "__main__":
    unittest.main()
