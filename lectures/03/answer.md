# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：
- `--trace` で見えたツール呼び出し（ツール名と引数）：
- 1つの質問での LLM 呼び出し回数（`requests`）：
- 追加したツールと、docstring に書いた説明：

## 宿題

- 取り組んだレベル：実装
- やったこと：
  - `app/tools.py` に `save_learning_log(topic, content)` を追加し、学習記録を `learning_log/` にMarkdownファイルとして保存する機能を実装した。
  - `app/agent.py` で `requires_approval=True` を指定して保存ツールを登録した。
  - `DeferredToolRequests` で保存処理を保留し、CLIで利用者に承認を求め、`DeferredToolResults` を渡して処理を再開するようにした。
  - `tests/test_learning_log_approval.py` に承認・拒否の自動テスト4件を追加した。既存テストも承認付きツールに対応させた。
- 結果：
  - 保存ツールが承認待ちになることを確認した。
  - 拒否時は保存0件、承認時は保存1件になることを確認した。
  - CLIから `n` を入力すると保存されず、`y` を入力すると保存されることを確認した。
  - `uv run pytest -q` の実行結果は `15 passed in 3.95s` だった。
  - テストにはPydantic AIの `TestModel` を使用した。Google APIを用いた実モデルでの確認は行っていない。
- 気づき・疑問：
  - ファイル保存のように外部へ影響する操作では、AIの判断だけで即実行させず、利用者の承認を挟む必要があると分かった。
  - 承認付きツールは呼び出し後すぐに実行結果を返すとは限らないため、既存テストも承認待ちを考慮した設計にする必要があった。
