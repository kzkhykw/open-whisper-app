# Open Super Whisper

グローバルホットキー制御による簡単な音声文字起こしデスクトップアプリケーション。

## クイックスタート - たった3ステップ！

1. **録音開始** - どのアプリケーションからでもグローバルホットキー（デフォルト：Ctrl+Shift+R）を押します
2. **録音停止** - 話し終わったら同じホットキーをもう一度押します
3. **テキスト貼り付け** - 文字起こし結果は自動的にクリップボードにコピーされるので、必要な場所に貼り付けるだけです

これだけです！作業の流れを中断することなく文字起こしが完了します。

## 特徴

- 🎙️ マイクから直接音声を録音
- 🌎 自動言語検出機能付きで100以上の言語をサポート
- 📝 文字起こし精度を向上させるカスタム語彙機能
- 🔧 文字起こしの動作をコントロールするシステム指示機能
- 📋 クリップボードに文字起こし内容をコピー
- 🔄 リアルタイムの録音状態表示とタイマー
- 🛎️ 文字起こし完了時にシステム通知でお知らせ（バックグラウンドでも見逃さない！）
- 🌙 **ダークモード対応**（OSのテーマに自動追従）
- 🍏 **macOS Sequoia 15.5 (24F74)で実装・動作確認済み**
- 🚀 **自動ペースト機能**（クリップボードコピー後、必要な場所に自動でペースト）
- 🖥️ **ネイティブAPI版フローティングウィンドウ**（他アプリ・全画面アプリでも表示可能）

## 新機能：ネイティブAPI版フローティングウィンドウ 🚀

### 他アプリでもスクリーン上にフローティング！

従来のPyQt6版に加えて、macOSのネイティブAPIを使用したフローティングウィンドウを追加しました。

#### 主な特徴
- **全画面アプリ対応**: YouTube、Netflix、ゲーム等の全画面アプリでも表示
- **最上位レベル表示**: 他のアプリの上に常に表示
- **macOS Space分離対応**: 全画面アプリの仮想デスクトップでも表示
- **パフォーマンス向上**: ネイティブAPIによる高速表示

#### 設定方法
1. **pyobjcパッケージのインストール**:
   ```bash
   pip install pyobjc-framework-Cocoa
   ```

2. **設定の有効化**:
   - システムトレイメニュー > 設定 > ネイティブAPI版フローティングウィンドウ
   - アプリケーションを再起動

3. **動作確認**:
   - 全画面アプリで録音開始
   - フローティングウィンドウが表示されることを確認

#### 技術仕様
- **ウィンドウレベル**: `NSWindow.Level.screenSaver`（最上位）
- **表示動作**: `NSWindowCollectionBehaviorCanJoinAllSpaces`
- **全画面対応**: `NSWindowCollectionBehaviorFullScreenAuxiliary`
- **依存関係**: `pyobjc-framework-Cocoa>=10.0`

## 利用可能なモデル

Open Super Whisperでは以下のローカルWhisperモデルを利用できます：

- **Whisper Large V3 Turbo** - 超高速度・高精度、809Mパラメータ（デフォルト）
- **Whisper Large V3** - 最高精度、1550Mパラメータ
- **Whisper Medium** - 高精度、769Mパラメータ
- **Whisper Small** - バランス良好、244Mパラメータ
- **Whisper Base** - 高速モデル、74Mパラメータ
- **Whisper Tiny** - 最速モデル、39Mパラメータ

## デモ

![Open Super Whisperの動作デモ](demo/demo.gif)

## ダウンロード

Windows用の最新の実行可能ファイル（.exe）は、[GitHub Releasesページ](https://github.com/TakanariShimbo/open-super-whisper/releases)からダウンロードできます。

## 必要条件

- WindowsまたはmacOSオペレーティングシステム
- インターネット接続（初回モデルダウンロード用）

## インストール方法

### UV を使用した方法

[UV](https://github.com/astral-sh/uv)は高速で効率的なPythonパッケージインストーラーおよび環境マネージャーです。

1. UVがインストールされているか確認：

```bash
uv --version
```

2. インストールされていない場合は、次のコマンドでインストールできます：

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. リポジトリをクローンまたはダウンロード

4. UVのsyncコマンドを使用してプロジェクトをセットアップ：

```bash
uv sync
```

5. 仮想環境をアクティベート：

```bash
# Windows (PowerShell)
.\.venv\Scripts\activate.ps1

# macOS/Linux の場合
source .venv/bin/activate
```

6. アプリケーションを実行：

```bash
python main.py
```

### アプリケーションのビルド方法

PyInstallerを使用してスタンドアロンの実行可能ファイルを作成できます：

```bash
# Windows (PowerShell)
python -m PyInstaller --onefile --windowed --icon assets/icon.ico --name "OpenSuperWhisper" --add-data "assets;assets" main.py

# macOS の場合
python -m PyInstaller --onefile --windowed --icon assets/icon.icns --name "OpenSuperWhisper" --add-data "assets:assets" main.py

# Linux の場合
python -m PyInstaller --onefile --windowed --icon assets/linux_pngs/icon_256.png --name "OpenSuperWhisper" --add-data "assets:assets" main.py
```

ビルドが完了すると、Windowsでは`dist`フォルダ内に`OpenSuperWhisper.exe`、macOSでは`dist`フォルダ内に`OpenSuperWhisper.app`が生成されます。

## 使用方法

（APIキー設定、録音、ホットキー、トレイ/メニューバー、言語・モデル選択、カスタム語彙、システム指示、結果管理、その他設定、コマンドラインオプションなど、従来通りの内容を簡潔に記載）

## このプロジェクトについて

本プロジェクトは [Open Super Whisper](https://github.com/TakanariShimbo/open-super-whisper)（MITライセンス）を元に開発されています。
元プロジェクトの著作権表示およびライセンス文は [LICENSE](./LICENSE) ファイルに記載しています。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細はLICENSEファイルをご覧ください。

---

## 原因の可能性

この症状は、**Whisperのモデルファイルや依存ライブラリが正しくバンドルされていない**場合や、**音声ファイルの読み込み・保存に失敗している**場合によく発生します。

特にPyInstallerで`torch`や`whisper`を使う場合、  
- モデルのダウンロード先やキャッシュパス
- `ffmpeg`の同梱
- `--hidden-import`の指定漏れ  
などが原因で、**正しく推論できず、デフォルトの短い文字列しか返さない**ことがあります。

---

## チェックリスト（Whisper-1/ローカル推論の場合）

- [ ] **PyInstallerのhidden-import指定**
  - `--hidden-import=whisper --hidden-import=torch` を追加してみてください。
- [ ] **ffmpegのパス**
  - ffmpegが実行ファイルからもパスが通っているか確認（`brew install ffmpeg`済みか）
- [ ] **Whisperモデルのキャッシュ**
  - Whisperは初回実行時に`~/.cache/whisper`や`~/.cache/torch`にモデルをダウンロードします。
  - スタンドアロン実行時にこのキャッシュにアクセスできているか？
- [ ] **音声ファイルの保存先**
  - 一時ファイルや録音ファイルの保存先が、PyInstaller実行時に正しく解決できているか（`sys._MEIPASS`考慮）

---

## 具体的な対策

### 1. PyInstallerコマンドの修正例

```bash
<code_block_to_apply_changes_from>
```

### 2. ffmpegの確認

ターミナルで  
```bash
ffmpeg -version
```
が通るか確認してください。

### 3. モデルキャッシュの確認

- スタンドアロン実行時に`~/.cache/whisper`や`~/.cache/torch`にアクセスできているか
- もしアクセスできない場合、`WHISPER_CACHE_DIR`や`TORCH_HOME`環境変数でキャッシュ先を明示する方法もあります

### 4. ログ・エラー出力の確認

- スタンドアロン実行時に、標準出力やログファイルにエラーが出ていないか確認してください
- もし何も出ていない場合、`main.py`の推論部分に`print`や`logging`でデバッグ出力を追加してみてください

---

## まとめ

1. `--hidden-import=whisper --hidden-import=torch` をPyInstallerコマンドに追加
2. ffmpegが使えるか確認
3. モデルキャッシュのパスを確認
4. エラーやログを確認

---

### もし上記で解決しない場合

- `main.py`や`whisper_api.py`の該当部分のコードを見せていただければ、さらに詳しく調査できます！
- 必要なら、**トラブルシューティング用のチェックリストmdファイル**も作成しますのでお知らせください😊

---

何か進展や追加情報があれば、また教えてください！
