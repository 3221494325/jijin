# FundOS Project Scaffolder
"""Scaffold FundOS project structure for new modules."""

import os
import argparse

TEMPLATES = {
    "data-provider": """\"\"\"{name} data provider for FundOS Data Hub.\"\"\"

from data_hub.providers.base import BaseProvider, ProviderCapability

class {class_name}Provider(BaseProvider):
    def __init__(self, config: dict = None):
        self.config = config or {{}}
        self._session = None

    async def fetch(self, code: str, data_type: str, **params) -> dict:
        raise NotImplementedError

    async def health_check(self) -> bool:
        raise NotImplementedError

    def capability(self) -> ProviderCapability:
        return ProviderCapability(
            asset_types=[],
            data_types=[],
            rate_limit=60,
            region="cn"
        )
""",
    "quant-strategy": """\"\"\"{name} trading strategy.\"\"\"

from quant.backtest.environment import BTE_V2

class {class_name}Strategy(BTE_V2):
    def prepare(self):
        pass

    def run(self, date):
        pass
""",
    "ai-tool": """package tools

import "context"

type {class_name}Tool struct{{}}

func (t *{class_name}Tool) Name() string {{ return "{name}" }}
func (t *{class_name}Tool) Description() string {{ return "" }}
func (t *{class_name}Tool) Execute(ctx context.Context, params map[string]any) (string, error) {{
    return "", nil
}}
""",
}

def to_class_name(name: str) -> str:
    return "".join(w.capitalize() for w in name.replace("-", "_").split("_"))

def main():
    parser = argparse.ArgumentParser(description="Scaffold FundOS modules")
    parser.add_argument("type", choices=["data-provider", "quant-strategy", "ai-tool"])
    parser.add_argument("name", help="Module name (kebab-case)")
    parser.add_argument("--path", default=".", help="Output directory")
    args = parser.parse_args()

    template = TEMPLATES[args.type]
    class_name = to_class_name(args.name)

    ext_map = {
        "data-provider": ".py",
        "quant-strategy": ".py",
        "ai-tool": ".go",
    }
    ext = ext_map[args.type]
    filename = f"{args.name}{ext}"

    content = template.format(name=args.name, class_name=class_name)
    filepath = os.path.join(args.path, filename)
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[FundOS] Created {args.type}: {filepath}")

if __name__ == "__main__":
    main()
