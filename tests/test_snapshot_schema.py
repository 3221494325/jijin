"""看板数据契约测试：payload 结构、时间口径、隐私边界。

手机端（mobile_site / GitHub Pages）已下线，原先针对静态快照的断言改为
校验"payload 不携带任何密钥"这一通用约束。
"""
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
        self.assertIn("market", payload)
        self.assertIn("xray", payload)

    def test_payload_carries_no_secret(self):
        import dashboard
        payload = dashboard.collect()
        raw = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn("FUNDOS_LLM_API_KEY", raw)
        status = payload.get("llm_status") or {}
        masked = status.get("key_masked")
        if masked:
            self.assertIn("…", str(masked), "密钥只能以掩码形式出现")


if __name__ == "__main__":
    unittest.main()
