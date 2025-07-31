# hotkeys.py importデバッグタスクリスト

- [ ] sys.pathの出力をprint直後にsys.exit(0)で強制表示し、どこに出力されるか確認
- [ ] hotkeys.pyのimport箇所を全て調査し、正しいパスでimportされているか確認
- [ ] hotkeys.pyのファイル名・パスの重複やtypoがないか再確認
- [ ] __pycache__や.pycファイルの再削除
- [ ] 標準出力がどこに出ているか（ターミナル/ログ/ファイル）を確認
- [ ] Qtアプリのprint出力が見えない場合、loggingやファイル出力で確認
- [ ] import hotkeys直後に例外raiseして、確実にimportされているか確認 