#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FundOS 免费大模型一键接入向导

用法:
  python setup_llm.py                       # 交互式向导（推荐）
  python setup_llm.py --provider bigmodel --key XXXX
  python setup_llm.py --test               # 只测试当前配置
  python setup_llm.py --status             # 查看当前配置

免费供应商（2026-08 调研，政策以官方页面为准）:
  bigmodel    智谱 BigModel —— GLM-4-Flash 系列【永久免费·不限量】（推荐）
              注册: https://open.bigmodel.cn → 控制台 → API 密钥
  siliconflow 硅基流动 —— 注册送 14 元 + 部分小模型永久免费，一个 Key 调 100+ 模型
              注册: https://cloud.siliconflow.cn → API 密钥
  modelscope  魔搭 ModelScope —— 每日 2000 次免费推理（需绑定阿里云账号）
              注册: https://www.modelscope.cn → 访问令牌
"""
import argparse
import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fundos_llm  # noqa: E402

PROVIDERS = {
    "bigmodel": {
        "name": "智谱 BigModel（推荐：GLM-4-Flash 系列 永久免费·不限量）",
        "register": "https://open.bigmodel.cn",
        "key_url": "https://open.bigmodel.cn/usercenter/apikeys",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash-250414",
        "model_alts": ["glm-4.5-flash", "glm-4.7-flash"],
    },
    "siliconflow": {
        "name": "硅基流动 SiliconFlow（注册送14元 + 免费小模型）",
        "register": "https://cloud.siliconflow.cn",
        "key_url": "https://cloud.siliconflow.cn/account/ak",
        "base_url": "https://api.siliconflow.cn/v1",
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "model_alts": ["THUDM/GLM-4-9B-Chat", "deepseek-ai/DeepSeek-V2.5"],
    },
    "modelscope": {
        "name": "魔搭 ModelScope（每日2000次免费，需绑阿里云账号）",
        "register": "https://www.modelscope.cn",
        "key_url": "https://www.modelscope.cn/my/myaccesstoken",
        "base_url": "https://api-inference.modelscope.cn/v1",
        "model": "ZhipuAI/GLM-4.6",
        "model_alts": ["Qwen/Qwen2.5-7B-Instruct"],
    },
    "custom": {
        "name": "自定义（任意 OpenAI 兼容厂商）",
        "register": "",
        "key_url": "",
        "base_url": "",
        "model": "",
        "model_alts": [],
    },
}


def _input(prompt, default=""):
    try:
        v = input(prompt).strip()
        return v or default
    except (EOFError, KeyboardInterrupt):
        print("\n已取消")
        sys.exit(1)


def pick_provider(args):
    if args.provider:
        if args.provider not in PROVIDERS:
            print(f"❌ 未知供应商: {args.provider}（可选: {'/'.join(PROVIDERS)}）")
            sys.exit(1)
        return args.provider, PROVIDERS[args.provider]
    print("=" * 64)
    print("  FundOS 免费大模型接入向导")
    print("=" * 64)
    print("\n  可选免费供应商:")
    for k, p in PROVIDERS.items():
        print(f"    [{k}] {p['name']}")
        if p["register"]:
            print(f"        注册/取Key: {p['key_url'] or p['register']}")
    choice = _input("\n  选择供应商 [bigmodel]: ", "bigmodel")
    if choice not in PROVIDERS:
        print(f"❌ 无效选择: {choice}")
        sys.exit(1)
    return choice, PROVIDERS[choice]


def main():
    parser = argparse.ArgumentParser(description="FundOS 免费大模型一键接入")
    parser.add_argument("--provider", choices=list(PROVIDERS), default=None)
    parser.add_argument("--key", default=None, help="API 密钥")
    parser.add_argument("--model", default=None)
    parser.add_argument("--base-url", dest="base_url", default=None)
    parser.add_argument("--test", action="store_true", help="只测试当前配置")
    parser.add_argument("--status", action="store_true", help="查看当前配置")
    args = parser.parse_args()

    if args.status:
        print("当前配置:", fundos_llm.status())
        return
    if args.test:
        key, base, model = fundos_llm._effective()
        if not key:
            print("❌ 尚未配置。运行 python setup_llm.py 开始接入。")
            return 1
        print(f"测试中… ({model} @ {base})")
        ok, msg = fundos_llm.test_call(key, base, model)
        print(("✅ " if ok else "❌ ") + msg)
        return 0 if ok else 1

    provider_id, p = pick_provider(args)
    base_url = args.base_url or p["base_url"]
    model = args.model or p["model"]

    if not args.key:
        if p["register"]:
            print(f"\n  即将打开注册页: {p['key_url'] or p['register']}")
            print("  注册后在控制台创建/复制 API 密钥，然后粘贴到这里。")
            if _input("  现在打开浏览器? [Y/n]: ", "y").lower() in ("", "y", "yes"):
                webbrowser.open(p["key_url"] or p["register"])
        api_key = _input(f"\n  粘贴 {provider_id} 的 API 密钥: ")
        if not api_key:
            print("❌ 未输入密钥，已取消")
            return 1
        if provider_id == "custom":
            base_url = _input("  Base URL (OpenAI兼容, 含/v1): ")
            model = _input("  模型名: ")
    else:
        api_key = args.key

    print(f"\n  正在验证… ({model} @ {base_url})")
    ok, msg = fundos_llm.test_call(api_key, base_url, model)
    print(("  ✅ " if ok else "  ❌ ") + msg)
    if not ok:
        print("\n  排查提示: 密钥是否复制完整? 模型名是否可用? 免费模型列表见平台文档。")
        return 1

    fundos_llm.save_config(api_key, base_url, model)
    print("\n" + "=" * 64)
    print("  ✅ 接入完成！配置已保存到 data/llm/config.json（仅本机，已排除 git）")
    print("  下一步: 打开看板 http://127.0.0.1:8899 → AI 总裁研判 → 点击『生成/刷新 AI 研判』")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
