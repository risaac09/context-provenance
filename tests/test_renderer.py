import json
import re
import tempfile
import unittest
from pathlib import Path

from provenance.channels import ChannelType, ProvenanceRecord, Source
from provenance.renderer import render_swimlane


class RendererTests(unittest.TestCase):
    def test_renderer_escapes_html_script_data_and_unsafe_links(self):
        hostile = "</SCRIPT><img src=x onerror=alert(1)>"
        record = ProvenanceRecord(hostile, "A & B", "2026-08-21")
        record.add_source(Source(
            channel=ChannelType.RETRIEVED,
            label=hostile,
            description=hostile,
            url="javascript:alert(1)",
        ))

        html = render_swimlane(record)

        self.assertIn("&lt;/SCRIPT&gt;&lt;img", html)
        self.assertNotIn('href="javascript:', html)
        self.assertIn("rel=\"noopener noreferrer\"", render_swimlane(self._safe_record()))
        embedded = re.search(
            r"window\.__PROVENANCE__ = (.*?);\s*</script>",
            html,
            re.DOTALL,
        ).group(1)
        self.assertNotIn("</SCRIPT>", embedded)
        self.assertEqual(
            json.loads(embedded)["context_provenance"]["title"],
            hostile,
        )

    def test_renderer_writes_the_returned_html(self):
        record = self._safe_record()
        with tempfile.TemporaryDirectory() as raw_tmp:
            output = Path(raw_tmp) / "report.html"
            html = render_swimlane(record, str(output))
            self.assertEqual(output.read_text(), html)

    @staticmethod
    def _safe_record():
        record = ProvenanceRecord("Title", "Author", "2026-08-21")
        record.add_source(Source(
            channel=ChannelType.RETRIEVED,
            label="Source",
            description="Description",
            url="https://example.com",
        ))
        return record


if __name__ == "__main__":
    unittest.main()
