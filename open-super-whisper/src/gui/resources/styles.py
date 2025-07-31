"""
アプリケーションのスタイル定義モジュール

このモジュールには、アプリケーションのUI全体で使用されるスタイルシートが含まれています。
スタイルの一元管理により、見た目の一貫性とメンテナンスが容易になります。
"""

class AppStyles:
    """アプリケーション全体のスタイルシートを管理するクラス"""

    # 共通のカラーパレット
    COLOR_PRIMARY = "#5B7FDE"
    COLOR_PRIMARY_HOVER = "#4968C2"
    COLOR_PRIMARY_PRESSED = "#3A5CB8"
    COLOR_DANGER = "#E05252"
    COLOR_DANGER_HOVER = "#D03A3A"
    COLOR_DANGER_PRESSED = "#C02E2E"
    COLOR_BACKGROUND = "#F8F9FC"
    COLOR_SURFACE = "#FFFFFF"
    COLOR_BORDER = "#E2E6EC"
    COLOR_BORDER_HOVER = "#C5CFDC"
    COLOR_TEXT_PRIMARY = "#333333"
    COLOR_TEXT_SECONDARY = "#555555"
    COLOR_SELECTION = "#EBF0FF"

    # --- ダークモード用カラーパレット ---
    COLOR_DARK_PRIMARY = "#7CA7FF"
    COLOR_DARK_PRIMARY_HOVER = "#5B8BE0"
    COLOR_DARK_PRIMARY_PRESSED = "#3A5CB8"
    COLOR_DARK_DANGER = "#FF6B6B"
    COLOR_DARK_DANGER_HOVER = "#E05252"
    COLOR_DARK_DANGER_PRESSED = "#C02E2E"
    COLOR_DARK_BACKGROUND = "#23272E"
    COLOR_DARK_SURFACE = "#2C313A"
    COLOR_DARK_BORDER = "#3A3F4B"
    COLOR_DARK_BORDER_HOVER = "#4B5363"
    COLOR_DARK_TEXT_PRIMARY = "#F3F6FA"
    COLOR_DARK_TEXT_SECONDARY = "#B0B8C1"
    COLOR_DARK_SELECTION = "#2D3A5A"

    # APIキーダイアログのスタイル
    API_KEY_DIALOG_STYLE = """
        QDialog {
            background-color: #F8F9FC;
        }
        
        QLineEdit {
            border: 1px solid #E2E6EC;
            border-radius: 4px;
            padding: 8px;
            background-color: white;
        }
        
        QLineEdit:focus {
            border-color: #5B7FDE;
        }
        
        QPushButton {
            background-color: #5B7FDE;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #4968C2;
        }
        
        QPushButton:pressed {
            background-color: #3A5CB8;
        }
        
        QPushButton#cancelButton {
            background-color: #F2F4F8;
            color: #333333;
            border: 1px solid #E2E6EC;
        }
        
        QPushButton#cancelButton:hover {
            background-color: #E8ECF2;
        }
        
        QPushButton#cancelButton:pressed {
            background-color: #D8DDE8;
        }
    """

    # APIキー情報ラベルのスタイル
    API_KEY_INFO_LABEL_STYLE = "color: #555555; padding: 5px 0;"

    # カスタム語彙ダイアログのスタイル
    VOCABULARY_DIALOG_STYLE = """
        QDialog {
            background-color: #F8F9FC;
        }
        
        QListWidget {
            border: 1px solid #E2E6EC;
            border-radius: 4px;
            background-color: white;
            padding: 4px;
        }
        
        QListWidget::item {
            padding: 6px;
            border-bottom: 1px solid #F2F4F8;
        }
        
        QListWidget::item:selected {
            background-color: #EBF0FF;
            color: #5B7FDE;
            border-radius: 2px;
        }
        
        QLineEdit {
            border: 1px solid #E2E6EC;
            border-radius: 4px;
            padding: 8px 12px;
            background-color: white;
            font-size: 13px;
            min-height: 20px;
        }
        
        QLineEdit:focus {
            border-color: #5B7FDE;
        }
        
        QPushButton {
            background-color: #5B7FDE;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background-color: #4968C2;
        }
        
        QPushButton:pressed {
            background-color: #3A5CB8;
        }
        
        QPushButton.secondary {
            background-color: #F2F4F8;
            color: #333333;
            border: 1px solid #E2E6EC;
        }
        
        QPushButton.secondary:hover {
            background-color: #E8ECF2;
        }
        
        QPushButton.secondary:pressed {
            background-color: #D8DDE8;
        }
        
        QPushButton.danger {
            background-color: #E05252;
        }
        
        QPushButton.danger:hover {
            background-color: #D03A3A;
        }
        
        QPushButton.danger:pressed {
            background-color: #C02E2E;
        }
        
        QLabel {
            color: #333333;
            font-size: 13px;
        }
        
        QLabel.sectionTitle {
            font-weight: bold;
            font-size: 14px;
            color: #324275;
            padding: 5px 0;
        }
    """

    # システム指示ダイアログのスタイル
    SYSTEM_INSTRUCTIONS_DIALOG_STYLE = """
        QDialog {
            background-color: #F8F9FC;
        }
        
        QListWidget {
            border: 1px solid #E2E6EC;
            border-radius: 4px;
            background-color: white;
            padding: 4px;
        }
        
        QListWidget::item {
            padding: 6px;
            border-bottom: 1px solid #F2F4F8;
        }
        
        QListWidget::item:selected {
            background-color: #EBF0FF;
            color: #5B7FDE;
            border-radius: 2px;
        }
        
        QLineEdit {
            border: 1px solid #E2E6EC;
            border-radius: 4px;
            padding: 8px 12px;
            background-color: white;
            font-size: 13px;
            min-height: 20px;
        }
        
        QLineEdit:focus {
            border-color: #5B7FDE;
        }
        
        QPushButton {
            background-color: #5B7FDE;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background-color: #4968C2;
        }
        
        QPushButton:pressed {
            background-color: #3A5CB8;
        }
        
        QPushButton.secondary {
            background-color: #F2F4F8;
            color: #333333;
            border: 1px solid #E2E6EC;
        }
        
        QPushButton.secondary:hover {
            background-color: #E8ECF2;
        }
        
        QPushButton.secondary:pressed {
            background-color: #D8DDE8;
        }
        
        QPushButton.danger {
            background-color: #E05252;
        }
        
        QPushButton.danger:hover {
            background-color: #D03A3A;
        }
        
        QPushButton.danger:pressed {
            background-color: #C02E2E;
        }
        
        QLabel {
            color: #333333;
            font-size: 13px;
        }
        
        QLabel.sectionTitle {
            font-weight: bold;
            font-size: 14px;
            color: #324275;
            padding: 5px 0;
        }
        
        QLabel.info {
            color: #555555;
            padding-bottom: 10px;
            line-height: 1.4;
        }
    """

    # 状態表示インジケーターウィンドウのスタイル
    STATUS_INDICATOR_STYLE = """
        #statusFrame {
            border-radius: 12px;
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                     stop:0 rgba(90, 100, 120, 220), 
                                     stop:1 rgba(70, 78, 94, 220));
            border: 1px solid rgba(255, 255, 255, 60);
        }
        
        #statusLabel {
            color: white;
            font-weight: bold;
            font-size: 15px;
            font-family: "Segoe UI", Arial, sans-serif;
            margin-top: 2px;
            padding: 2px;
        }
        
        #timerLabel {
            color: white;
            font-size: 20px;
            font-family: "Segoe UI", Arial, sans-serif;
            font-weight: 500;
            padding: 2px;
        }
    """

    # 録音モードのインジケーターフレームスタイル
    RECORDING_INDICATOR_FRAME_STYLE = """
        #statusFrame {
            border-radius: 12px;
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 rgba(224, 82, 82, 220), 
                                    stop:1 rgba(200, 60, 60, 220));
            border: 1px solid rgba(255, 255, 255, 60);
        }
    """

    # 文字起こしモードのインジケーターフレームスタイル
    TRANSCRIBING_INDICATOR_FRAME_STYLE = """
        #statusFrame {
            border-radius: 12px;
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 rgba(120, 120, 120, 220), 
                                    stop:1 rgba(90, 90, 90, 220));
            border: 1px solid rgba(255, 255, 255, 60);
        }
    """

    # 文字起こし完了モードのインジケーターフレームスタイル
    TRANSCRIBED_INDICATOR_FRAME_STYLE = """
        #statusFrame {
            border-radius: 12px;
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 rgba(65, 105, 225, 220), 
                                    stop:1 rgba(45, 85, 205, 220));
            border: 1px solid rgba(255, 255, 255, 60);
        }
    """

    # ホットキーダイアログのスタイル
    HOTKEY_DIALOG_STYLE = """
        QDialog {
            background-color: #F8F9FC;
        }
        
        QLineEdit {
            border: 1px solid #E2E6EC;
            border-radius: 4px;
            padding: 8px;
            background-color: white;
            font-size: 13px;
        }
        
        QLineEdit:focus {
            border-color: #5B7FDE;
        }
        
        QPushButton {
            background-color: #5B7FDE;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #4968C2;
        }
        
        QPushButton:pressed {
            background-color: #3A5CB8;
        }
        
        QPushButton#cancelButton {
            background-color: #F2F4F8;
            color: #333333;
            border: 1px solid #E2E6EC;
        }
        
        QPushButton#cancelButton:hover {
            background-color: #E8ECF2;
        }
        
        QPushButton#cancelButton:pressed {
            background-color: #D8DDE8;
        }
    """

    # メインウィンドウのスタイル
    MAIN_WINDOW_STYLE = """
        * {
            font-family: "Segoe UI", Arial, sans-serif;
            font-size: 13px;
        }
        
        QMainWindow {
            background-color: #F8F9FC;
        }
        
        QToolBar {
            background-color: #FFFFFF;
            border-bottom: 1px solid #E8ECF2;
            spacing: 5px;
            padding: 5px;
            font-size: 13px;
        }
        
        QToolBar QAction {
            padding: 4px 8px;
        }
        
        /* メニュー選択時の色を変更 */
        QMenu {
            background-color: #FFFFFF;
            border: 1px solid #E2E6EC;
            padding: 2px;
        }
        
        QMenu::item:selected {
            background-color: #4968C2;
            color: white;
            border-radius: 3px;
            padding: 3px 6px;
        }
        
        QMenu::item {
            padding: 3px 6px;
            margin: 1px 3px;
        }
        
        QMenu::separator {
            height: 1px;
            background-color: #E2E6EC;
            margin: 4px 8px;
        }
        
        /* ツールバーの選択色 */
        QToolBar QAction:checked {
            background-color: #5B7FDE;
            color: white;
            border-radius: 3px;
        }
        
        QToolBar QAction:hover {
            background-color: #EBF0FF;
            border-radius: 3px;
        }
        
        /* ツールバーのボタン */
        QToolButton {
            padding: 5px 8px;
            border-radius: 3px;
            margin: 1px;
        }
        
        QToolButton:checked {
            background-color: #5B7FDE;
            color: white;
            font-weight: bold;
        }
        
        QToolButton:hover {
            background-color: #EBF0FF;
        }
        
        QToolButton:checked:hover {
            background-color: #4968C2;
        }
        
        QToolButton:pressed {
            background-color: #4968C2;
            color: white;
        }
        
        QPushButton {
            background-color: #5B7FDE;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 13px;
        }
        
        QPushButton:hover {
            background-color: #4968C2;
        }
        
        QPushButton:pressed {
            background-color: #3A5CB8;
        }
        
        QTextEdit {
            border: 1px solid #E2E6EC;
            border-radius: 4px;
            background-color: white;
            padding: 8px;
            font-size: 14px;
        }
        
        QComboBox {
            border: 1px solid #E2E6EC;
            border-radius: 4px;
            padding: 6px 12px;
            background-color: white;
            min-width: 150px;
        }
        
        QComboBox:hover {
            border-color: #C5CFDC;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: center right;
            width: 20px;
            border-left: none;
        }
        
        /* コンボボックスのドロップダウンメニュー */
        QComboBox QAbstractItemView {
            background-color: white;
            border: 1px solid #E2E6EC;
            selection-background-color: #5B7FDE;
            selection-color: white;
        }
        
        QStatusBar {
            background-color: #FFFFFF;
            color: #555555;
            border-top: 1px solid #E8ECF2;
            font-size: 13px;
        }
        
        QLabel {
            color: #333333;
            font-size: 13px;
        }
    """

    # --- ダークモード用スタイル例（メインウィンドウ）---
    MAIN_WINDOW_STYLE_DARK = """
        * {
            font-family: \"Segoe UI\", Arial, sans-serif;
            font-size: 13px;
        }
        QMainWindow {
            background-color: #23272E;
        }
        QToolBar {
            background-color: #2C313A;
            border-bottom: 1px solid #3A3F4B;
            spacing: 5px;
            padding: 5px;
            font-size: 13px;
        }
        QToolBar QAction {
            padding: 4px 8px;
        }
        QMenu {
            background-color: #2C313A;
            border: 1px solid #3A3F4B;
            padding: 2px;
        }
        QMenu::item:selected {
            background-color: #5B8BE0;
            color: #F3F6FA;
            border-radius: 3px;
            padding: 3px 6px;
        }
        QMenu::item {
            padding: 3px 6px;
            margin: 1px 3px;
        }
        QMenu::separator {
            height: 1px;
            background-color: #3A3F4B;
            margin: 4px 8px;
        }
        QToolBar QAction:checked {
            background-color: #7CA7FF;
            color: #23272E;
            border-radius: 3px;
        }
        QToolBar QAction:hover {
            background-color: #2D3A5A;
            border-radius: 3px;
        }
        QToolButton {
            padding: 5px 8px;
            border-radius: 3px;
            margin: 1px;
        }
        QToolButton:checked {
            background-color: #7CA7FF;
            color: #23272E;
            font-weight: bold;
        }
        QToolButton:hover {
            background-color: #2D3A5A;
        }
        QToolButton:checked:hover {
            background-color: #5B8BE0;
        }
        QToolButton:pressed {
            background-color: #5B8BE0;
            color: #F3F6FA;
        }
        QPushButton {
            background-color: #7CA7FF;
            color: #23272E;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #5B8BE0;
        }
        QPushButton:pressed {
            background-color: #3A5CB8;
        }
        QTextEdit {
            border: 1px solid #3A3F4B;
            border-radius: 4px;
            background-color: #2C313A;
            color: #F3F6FA;
            padding: 8px;
            font-size: 14px;
        }
        QComboBox {
            border: 1px solid #3A3F4B;
            border-radius: 4px;
            padding: 6px 12px;
            background-color: #2C313A;
            color: #F3F6FA;
            min-width: 150px;
        }
        QComboBox:hover {
            border-color: #4B5363;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: center right;
            width: 20px;
            border-left: none;
        }
        QComboBox QAbstractItemView {
            background-color: #23272E;
            border: 1px solid #3A3F4B;
            selection-background-color: #5B8BE0;
            selection-color: #F3F6FA;
        }
        QStatusBar {
            background-color: #2C313A;
            color: #B0B8C1;
            border-top: 1px solid #3A3F4B;
            font-size: 13px;
        }
        QLabel {
            color: #F3F6FA;
            font-size: 13px;
        }
    """

    # コントロールパネルのスタイル
    CONTROL_PANEL_STYLE = """
        #controlPanel {
            background-color: white;
            border-radius: 8px;
            border: 1px solid #E2E6EC;
        }
    """

    # 録音ボタンのスタイル
    RECORD_BUTTON_STYLE = """
        #recordButton {
            background-color: #5B7FDE;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 20px;
            font-weight: bold;
            font-size: 14px;
        }
        
        #recordButton:hover {
            background-color: #4968C2;
        }
        
        #recordButton:pressed {
            background-color: #3A5CB8;
        }
    """

    # 録音ボタン（録音中）のスタイル
    RECORD_BUTTON_RECORDING_STYLE = """
        #recordButton {
            background-color: #E05252;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 20px;
            font-weight: bold;
            font-size: 14px;
        }
        
        #recordButton:hover {
            background-color: #D03A3A;
        }
        
        #recordButton:pressed {
            background-color: #C02E2E;
        }
    """

    # 文字起こしパネルのスタイル
    TRANSCRIPTION_PANEL_STYLE = """
        #transcriptionPanel {
            background-color: white;
            border-radius: 8px;
            border: 1px solid #E2E6EC;
        }
    """

    # 文字起こしタイトルのスタイル 
    TRANSCRIPTION_TITLE_STYLE = """
        color: #324275;
        font-weight: bold;
        font-size: 15px;
        border-bottom: 1px solid #EBF0FF;
        padding-bottom: 8px;
        margin-bottom: 5px;
    """

    # 文字起こしテキストエリアのスタイル
    TRANSCRIPTION_TEXT_STYLE = """
        border: none;
        background-color: white;
        font-size: 14px;
        line-height: 1.5;
    """

    # ステータスバーのスタイル
    STATUS_BAR_STYLE = """
        color: #555555;
        font-size: 13px;
    """

    # 通常の録音インジケーターのスタイル
    RECORDING_INDICATOR_NORMAL_STYLE = "color: gray; font-size: 16px;"

    # 録音中の録音インジケーターのスタイル
    RECORDING_INDICATOR_ACTIVE_STYLE = """
        color: #5B7FDE;
        font-size: 18px;
        font-weight: bold;
    """

    # 録音タイマーラベルのスタイル
    RECORDING_TIMER_LABEL_STYLE = "color: #444; font-family: 'Roboto Mono', monospace; font-weight: bold;"

    # 録音終了後の録音インジケーターのスタイル
    RECORDING_INDICATOR_INACTIVE_STYLE = "color: #C5CFDC; font-size: 16px;"

    # システムトレイメニューのスタイル
    SYSTEM_TRAY_MENU_STYLE = """
        QMenu {
            background-color: #FFFFFF;
            border: 1px solid #E2E6EC;
            padding: 2px;
        }
        
        QMenu::item {
            padding: 6px 24px;
            margin: 2px 4px;
        }
        
        QMenu::item:selected {
            background-color: #5B7FDE;
            color: white;
            border-radius: 3px;
        }
        
        QMenu::separator {
            height: 1px;
            background-color: #E2E6EC;
            margin: 3px 8px;
        }
    """ 

    # フローティングインジケーターのスタイル
    FLOATING_INDICATOR_STYLE = """
        #floatingBackground {
            background-color: rgba(40, 44, 52, 0.95);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    """

    # フローティング停止ボタンのスタイル
    FLOATING_STOP_BUTTON_STYLE = """
        QPushButton {
            background-color: #E05252;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            font-weight: bold;
            font-size: 11px;
        }
        
        QPushButton:hover {
            background-color: #D03A3A;
        }
        
        QPushButton:pressed {
            background-color: #C02E2E;
        }
    """

    # フローティング設定ボタンのスタイル
    FLOATING_SETTINGS_BUTTON_STYLE = """
        QPushButton {
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            padding: 4px;
            font-size: 12px;
        }
        
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.3);
        }
        
        QPushButton:pressed {
            background-color: rgba(255, 255, 255, 0.15);
        }
    """

    # --- ダークモード用コントロールパネルスタイル ---
    CONTROL_PANEL_STYLE_DARK = """
        #controlPanel {
            background-color: #2C313A;
            border-radius: 8px;
            border: 1px solid #3A3F4B;
        }
    """
    # --- ダークモード用テキストエリア ---
    TRANSCRIPTION_TEXT_STYLE_DARK = """
        border: none;
        background-color: #2C313A;
        color: #F3F6FA;
        font-size: 14px;
        line-height: 1.5;
    """
    # --- ダークモード用ダイアログ ---
    API_KEY_DIALOG_STYLE_DARK = """
        QDialog {
            background-color: #23272E;
        }
        QLineEdit {
            border: 1px solid #3A3F4B;
            border-radius: 4px;
            padding: 8px;
            background-color: #2C313A;
            color: #F3F6FA;
        }
        QLineEdit:focus {
            border-color: #7CA7FF;
        }
        QPushButton {
            background-color: #7CA7FF;
            color: #23272E;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #5B8BE0;
        }
        QPushButton:pressed {
            background-color: #3A5CB8;
        }
        QPushButton#cancelButton {
            background-color: #2C313A;
            color: #F3F6FA;
            border: 1px solid #3A3F4B;
        }
        QPushButton#cancelButton:hover {
            background-color: #3A3F4B;
        }
        QPushButton#cancelButton:pressed {
            background-color: #23272E;
        }
    """
    # --- ダークモード用カスタム語彙ダイアログ ---
    VOCABULARY_DIALOG_STYLE_DARK = """
        QDialog {
            background-color: #23272E;
        }
        QListWidget {
            border: 1px solid #3A3F4B;
            border-radius: 4px;
            background-color: #2C313A;
            color: #F3F6FA;
            padding: 4px;
        }
        QListWidget::item {
            padding: 6px;
            border-bottom: 1px solid #23272E;
        }
        QListWidget::item:selected {
            background-color: #2D3A5A;
            color: #7CA7FF;
            border-radius: 2px;
        }
        QLineEdit {
            border: 1px solid #3A3F4B;
            border-radius: 4px;
            padding: 8px 12px;
            background-color: #2C313A;
            color: #F3F6FA;
            font-size: 13px;
            min-height: 20px;
        }
        QLineEdit:focus {
            border-color: #7CA7FF;
        }
        QPushButton {
            background-color: #7CA7FF;
            color: #23272E;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 20px;
        }
        QPushButton:hover {
            background-color: #5B8BE0;
        }
        QPushButton:pressed {
            background-color: #3A5CB8;
        }
        QPushButton.secondary {
            background-color: #2C313A;
            color: #F3F6FA;
            border: 1px solid #3A3F4B;
        }
        QPushButton.secondary:hover {
            background-color: #3A3F4B;
        }
        QPushButton.secondary:pressed {
            background-color: #23272E;
        }
        QPushButton.danger {
            background-color: #FF6B6B;
        }
        QPushButton.danger:hover {
            background-color: #E05252;
        }
        QPushButton.danger:pressed {
            background-color: #C02E2E;
        }
        QLabel {
            color: #F3F6FA;
            font-size: 13px;
        }
        QLabel.sectionTitle {
            font-weight: bold;
            font-size: 14px;
            color: #7CA7FF;
            padding: 5px 0;
        }
    """
    # --- ダークモード用システム指示ダイアログ ---
    SYSTEM_INSTRUCTIONS_DIALOG_STYLE_DARK = """
        QDialog {
            background-color: #23272E;
        }
        QListWidget {
            border: 1px solid #3A3F4B;
            border-radius: 4px;
            background-color: #2C313A;
            color: #F3F6FA;
            padding: 4px;
        }
        QListWidget::item {
            padding: 6px;
            border-bottom: 1px solid #23272E;
        }
        QListWidget::item:selected {
            background-color: #2D3A5A;
            color: #7CA7FF;
            border-radius: 2px;
        }
        QLineEdit {
            border: 1px solid #3A3F4B;
            border-radius: 4px;
            padding: 8px 12px;
            background-color: #2C313A;
            color: #F3F6FA;
            font-size: 13px;
            min-height: 20px;
        }
        QLineEdit:focus {
            border-color: #7CA7FF;
        }
        QPushButton {
            background-color: #7CA7FF;
            color: #23272E;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 20px;
        }
        QPushButton:hover {
            background-color: #5B8BE0;
        }
        QPushButton:pressed {
            background-color: #3A5CB8;
        }
        QPushButton.secondary {
            background-color: #2C313A;
            color: #F3F6FA;
            border: 1px solid #3A3F4B;
        }
        QPushButton.secondary:hover {
            background-color: #3A3F4B;
        }
        QPushButton.secondary:pressed {
            background-color: #23272E;
        }
        QPushButton.danger {
            background-color: #FF6B6B;
        }
        QPushButton.danger:hover {
            background-color: #E05252;
        }
        QPushButton.danger:pressed {
            background-color: #C02E2E;
        }
        QLabel {
            color: #F3F6FA;
            font-size: 13px;
        }
        QLabel.sectionTitle {
            font-weight: bold;
            font-size: 14px;
            color: #7CA7FF;
            padding: 5px 0;
        }
        QLabel.info {
            color: #B0B8C1;
            padding-bottom: 10px;
            line-height: 1.4;
        }
    """ 