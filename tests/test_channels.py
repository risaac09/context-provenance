import json
import unittest

from provenance.channels import ChannelType, ProvenanceRecord, Source


class ProvenanceRecordTests(unittest.TestCase):
    def test_record_always_contains_all_four_channels(self):
        record = ProvenanceRecord("Title", "Author", "2026-08-21")

        self.assertEqual(set(record.channels), set(ChannelType))
        self.assertEqual(record.total_sources, 0)
        self.assertEqual(record.opacity_ratio, 1.0)

    def test_round_trip_preserves_sources_notes_and_summary(self):
        record = ProvenanceRecord("Title", "Author", "2026-08-21", model="model")
        record.add_source(Source(
            channel=ChannelType.RETRIEVED,
            label="Primary source",
            description="A retrieved document",
            url="https://example.com/source",
            weight=0.75,
        ))
        record.add_source(Source(
            channel=ChannelType.TRAINING,
            label="Training data",
            description="Opaque source",
            retrievable=False,
        ))
        record.channels[ChannelType.TRAINING].note = "Not retrievable"

        restored = ProvenanceRecord.from_dict(json.loads(record.to_json()))

        self.assertEqual(restored.total_sources, 2)
        self.assertEqual(restored.retrievable_sources, 1)
        self.assertEqual(restored.opacity_ratio, 0.5)
        self.assertEqual(
            restored.channels[ChannelType.TRAINING].note,
            "Not retrievable",
        )
        source = restored.channels[ChannelType.RETRIEVED].sources[0]
        self.assertEqual(source.url, "https://example.com/source")
        self.assertEqual(source.weight, 0.75)

    def test_weight_must_be_a_probability(self):
        for weight in (-0.01, 1.01):
            with self.subTest(weight=weight), self.assertRaises(ValueError):
                Source(ChannelType.RETRIEVED, "x", "x", weight=weight)


if __name__ == "__main__":
    unittest.main()
