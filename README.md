# OpenWhisper

OpenWhisperは、リアルタイム音声認識とAIアシスタント機能を提供するデスクトップアプリケーションです。

## 🚀 機能

- **リアルタイム音声認識**: マイクからの音声をリアルタイムでテキストに変換
- **AIアシスタント**: 認識されたテキストに対してAIが回答を生成
- **フローティングウィンドウ**: 常に最前面に表示される便利なウィンドウ
- **ホットキー対応**: キーボードショートカットで操作
- **カスタム語彙**: 専門用語や固有名詞の認識精度向上
- **システム指示**: AIの応答スタイルをカスタマイズ

## 📋 要件

- Python 3.8以上
- macOS 10.14以上
- マイクアクセス権限

## 🛠️ インストール

1. リポジトリをクローン
```bash
git clone https://github.com/yourusername/OpenWhisper.git
cd OpenWhisper
```

2. 依存関係をインストール
```bash
cd open-super-whisper
pip install -r requirements.txt
```

3. アプリケーションを実行
```bash
python main.py
```

## 🎯 使用方法

1. アプリケーションを起動
2. マイクアクセスを許可
3. ホットキー（デフォルト: Cmd+Shift+Space）で録音開始/停止
4. 音声がテキストに変換され、AIが回答を生成

## ⚙️ 設定

- **ホットキー**: 設定メニューから変更可能
- **カスタム語彙**: 専門用語を追加して認識精度を向上
- **システム指示**: AIの応答スタイルをカスタマイズ

## 📁 プロジェクト構造

```
open-super-whisper/
├── main.py                 # メインアプリケーション
├── src/
│   ├── core/              # コア機能
│   │   ├── audio_recorder.py
│   │   ├── hotkeys.py
│   │   └── whisper_api.py
│   ├── gui/               # GUIコンポーネント
│   │   ├── components/
│   │   ├── windows/
│   │   └── main.py
│   └── utils/             # ユーティリティ
├── assets/                # リソースファイル
└── docs/                  # ドキュメント
```

## 🤝 貢献

プルリクエストやイシューの報告を歓迎します！

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🙏 謝辞

- OpenAI Whisper API
- PyQt6
- その他のオープンソースライブラリ 