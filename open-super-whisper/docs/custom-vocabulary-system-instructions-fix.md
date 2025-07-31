# カスタム語彙・システムプロンプト保存問題の解決

## 問題の概要

カスタム語彙やシステムプロンプトが保存されない問題が発生していました。

## 原因

QSettingsでリスト型のデータを直接保存する際に、一部のプラットフォームで正しく保存されない問題がありました。

## 解決策

### 1. JSON形式での保存

QSettingsでリストを保存する際に、JSON形式に変換してから保存するように修正しました。

```python
# 修正前
self.settings.setValue("custom_vocabulary", vocabulary)

# 修正後
vocabulary_json = json.dumps(vocabulary, ensure_ascii=False)
self.settings.setValue("custom_vocabulary", vocabulary_json)
```

### 2. JSON形式での読み込み

保存されたJSONデータを正しく読み込むように修正しました。

```python
# 修正前
saved_vocabulary = self.settings.value("custom_vocabulary", [], type=list)

# 修正後
saved_vocabulary_json = self.settings.value("custom_vocabulary", "")
if saved_vocabulary_json:
    saved_vocabulary = json.loads(saved_vocabulary_json)
```

## 修正されたファイル

- `src/gui/windows/main_window.py`
  - `_save_vocabulary()` メソッド
  - `_save_system_instructions()` メソッド
  - `_load_saved_vocabulary()` メソッド
  - `_load_saved_system_instructions()` メソッド

## デバッグ機能

問題の特定と解決を支援するため、以下のデバッグ情報を追加しました：

- 保存時のデータ型と内容の確認
- 読み込み時のデータ型と内容の確認
- エラー発生時の詳細なスタックトレース
- 保存確認のための即座の読み込みテスト

## 使用方法

1. アプリケーションを起動
2. カスタム語彙またはシステム指示を設定
3. 設定を保存（ダイアログでOKを押す）
4. アプリケーションを再起動
5. 設定が正しく読み込まれることを確認

## 確認方法

### 設定ファイルの確認

macOSの場合：
```bash
plutil -p ~/Library/Preferences/com.opensuperwhisper.OpenSuperWhisper.plist
```

### デバッグログの確認

アプリケーション実行時にコンソールに出力されるデバッグ情報を確認：
- `[DEBUG] 保存するカスタム語彙: [...]`
- `[DEBUG] 保存確認 - 読み込まれた語彙: [...]`
- `[INFO] カスタム語彙を保存しました: X個`

## 今後の改善点

- 設定のバックアップ機能
- 設定のインポート/エクスポート機能
- 設定の検証機能
- より詳細なエラーハンドリング

## 注意事項

- 既存の設定ファイルは削除され、新しい形式で再作成されます
- 初回起動時は設定が空の状態になります
- 日本語などの非ASCII文字も正しく保存されます（`ensure_ascii=False`） 