import unittest
from datetime import datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class SnapshotSchemaTests(unittest.TestCase):
    def test_local_snapshot_metadata(self):
        import dashboard
        payload = dashboard.collect()
        meta = payload["snapshot_meta"]
        self.assertEqual(meta["source"], "local_computer")
        self.assertEqual(meta["timezone"], "Asia/Shanghai")
        self.assertEqual(meta["status"], "success")
        self.assertIsNotNone(datetime.fromisoformat(meta["generated_at"]).tzinfo)
        self.assertIn("portfolio", payload)

    def test_public_snapshot_has_no_api_key(self):
        path = ROOT / "mobile_site" / "data.json"
        if not path.exists():
            self.skipTest("本地未生成手机快照")
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        self.assertNotIn("FUNDOS_LLM_API_KEY", raw)
        if "snapshot_meta" in data:
            self.assertIn(data["snapshot_meta"]["source"], {"local_computer", "github_actions"})

if __name__ == "__main__":
    unittest.main()
