"""第1回：Geminiへの質問・連続会話・性能計測。"""

import argparse
import time

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(question: str) -> str:
    """従来の1回だけ質問する機能。"""
    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(
        model=MODEL, contents=question
    )
    return response.text


def show_stats(response, seconds: float) -> None:
    """応答時間とAPIが返したトークン数を表示する。"""
    print(f"[応答時間] {seconds:.2f}秒")

    usage = getattr(response, "usage_metadata", None)
    if usage is None:
        print("[トークン数] 取得できませんでした")
        return

    print(
        f"[トークン数] "
        f"入力={usage.prompt_token_count} "
        f"出力={usage.candidates_token_count} "
        f"合計={usage.total_token_count}"
    )


def ask_with_stats(question: str) -> None:
    """1回の質問を計測する。"""
    client = genai.Client(api_key=get_api_key())

    start = time.perf_counter()
    response = client.models.generate_content(
        model=MODEL, contents=question
    )
    seconds = time.perf_counter() - start

    print(response.text)
    show_stats(response, seconds)


def chat_loop() -> None:
    """会話履歴を保持して質問を続ける。"""
    client = genai.Client(api_key=get_api_key())
    chat = client.chats.create(model=MODEL)

    print(f"[会話モード] {MODEL}")
    print("前の会話を保持します。終了するには exit と入力してください。")

    while True:
        try:
            question = input("\nあなた> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n会話を終了しました。")
            break

        if question.lower() in ("exit", "quit"):
            print("会話を終了しました。")
            break

        if not question:
            continue

        try:
            start = time.perf_counter()
            response = chat.send_message(question)
            seconds = time.perf_counter() - start

            print(f"\nGemini> {response.text}")
            show_stats(response, seconds)

        except errors.APIError as e:
            print(api_error_message(e.code, e.message))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Geminiへの質問・会話・性能計測"
    )
    parser.add_argument(
        "question", nargs="?", default=DEFAULT_QUESTION
    )
    parser.add_argument(
        "--chat", action="store_true",
        help="会話履歴を保持する"
    )
    parser.add_argument(
        "--stats", action="store_true",
        help="応答時間とトークン数を計測する"
    )
    args = parser.parse_args()

    try:
        if args.chat:
            chat_loop()
            return

        print(f"[model] {MODEL}")
        print(f"[質問] {args.question}\n")

        if args.stats:
            ask_with_stats(args.question)
        else:
            print(ask(args.question))

    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
