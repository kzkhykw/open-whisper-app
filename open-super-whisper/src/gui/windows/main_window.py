import os
import sys
import threading
import time
import platform
import json
try:
    import pyautogui
except ImportError:
    pyautogui = None

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QComboBox, QFileDialog,
    QCheckBox, QLineEdit, QListWidget, QMessageBox, QSplitter,
    QStatusBar, QToolBar, QDialog, QGridLayout, QFormLayout,
    QSystemTrayIcon, QMenu, QStyle, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSettings, QUrl
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

import platform
import sounddevice as sd

from PyQt6.QtWidgets import QMessageBox
from ..utils.mic_permission import has_microphone_permission, request_microphone_permission

def is_dark_mode():
    """
    OSのダークモードかどうかを判定（macOS/Windows対応、Linuxは常にFalse）
    """
    try:
        if platform.system() == "Darwin":
            # macOS: AppleInterfaceStyle=Dark ならダーク
            from AppKit import NSApplication, NSApp, NSAppearance, NSAppearanceNameDarkAqua
            import objc
            app = NSApplication.sharedApplication()
            appearance = app.effectiveAppearance()
            return appearance.name() == NSAppearanceNameDarkAqua
        elif platform.system() == "Windows":
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize") as key:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return value == 0
        else:
            return False
    except Exception:
        return False

from src.core.audio_recorder import AudioRecorder
from src.core.whisper_api import WhisperTranscriber
from src.core.hotkeys import HotkeyManager
from src.gui.resources.config import AppConfig
from src.gui.resources.labels import AppLabels
from src.gui.resources.styles import AppStyles

from src.gui.components.dialogs.vocabulary_dialog import VocabularyDialog
from src.gui.components.dialogs.system_instructions_dialog import SystemInstructionsDialog
from src.gui.components.dialogs.hotkey_dialog import HotkeyDialog
from src.gui.components.widgets.status_indicator import StatusIndicatorWindow
from src.gui.components.widgets.floating_indicator import FloatingIndicator
from src.gui.utils.resource_helper import getResourcePath

class MainWindow(QMainWindow):
    """
    アプリケーションのメインウィンドウ
    
    ユーザーインターフェース、音声録音機能、文字起こし機能を統合した
    アプリケーションの中心となるウィンドウです。
    """
    
    # カスタムシグナルの定義
    transcription_complete = pyqtSignal(str)
    recording_status_changed = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        
        # 設定の読み込み
        self.settings = QSettings(AppConfig.APP_ORGANIZATION, AppConfig.APP_NAME)
        
        # ホットキーとクリップボード設定
        self.hotkey = self.settings.value("hotkey", AppConfig.DEFAULT_HOTKEY)
        self.auto_copy = self.settings.value("auto_copy", AppConfig.DEFAULT_AUTO_COPY, type=bool)
        
        # ホットキーマネージャーの初期化
        self.hotkey_manager = HotkeyManager()
        
        # コアコンポーネントの初期化
        self.audio_recorder = None
        self.whisper_transcriber = None
        
        # 録音状態
        self.is_recording = False
        
        # サウンド設定
        self.enable_sound = self.settings.value("enable_sound", AppConfig.DEFAULT_ENABLE_SOUND, type=bool)
        
        # インジケータ表示設定（デフォルトON）
        self.show_indicator = self.settings.value("show_indicator", AppConfig.DEFAULT_SHOW_INDICATOR, type=bool)
        
        # サウンドプレーヤーの初期化
        self.setup_sound_players()
        
        # コンポーネントの初期化
        self.audio_recorder = AudioRecorder()
        
        # 状態表示ウィンドウ
        self.status_indicator_window = StatusIndicatorWindow()
        # 初期モードを録音中に設定
        self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_RECORDING)
        # 初期状態では表示しない - 録音開始時に表示する
        
        # フローティングインジケーター
        # ネイティブAPI使用の設定を読み込み（デフォルトはTrueに変更）
        use_native_api = self.settings.value("use_native_floating_api", False, type=bool)
        
        # デバッグ用：ネイティブAPI版を強制的に有効にする（開発時のみ）
        force_native_api = self.settings.value("force_native_api_debug", False, type=bool)
        if force_native_api:
            use_native_api = True
            print("[DEBUG] ネイティブAPI版を強制的に有効にします")
        
        # pyobjcの利用可能性をチェック
        try:
            import objc
            from AppKit import NSPanel, NSWindow
            pyobjc_available = True
            print("[INFO] pyobjcパッケージが利用可能です")
        except ImportError:
            pyobjc_available = False
            print("[WARNING] pyobjcパッケージがインストールされていません")
            print("[INFO] ネイティブAPI版を使用するには以下を実行してください:")
            print("    pip install pyobjc-framework-Cocoa")
        
        # ネイティブAPIが利用可能かチェック
        if use_native_api and pyobjc_available:
            print("[INFO] ネイティブAPI版フローティングウィンドウを使用します")
        else:
            if use_native_api and not pyobjc_available:
                print("[WARNING] ネイティブAPI版が設定されていますが、pyobjcが利用できません")
                print("[INFO] PyQt6版にフォールバックします")
            else:
                print("[INFO] PyQt6版フローティングウィンドウを使用します")
        
        self.floating_indicator = FloatingIndicator(use_native_api=use_native_api and pyobjc_available)
        self.floating_indicator.stop_recording_requested.connect(self.toggle_recording)
        self.floating_indicator.settings_requested.connect(self.show)
        
        try:
            self.whisper_transcriber = WhisperTranscriber()
            # 保存されたカスタム語彙を読み込み
            self._load_saved_vocabulary()
            # 保存されたシステム指示を読み込み
            self._load_saved_system_instructions()
        except Exception as e:
            print(f"[ERROR] Failed to initialize WhisperTranscriber: {e}")
            self.whisper_transcriber = None
            
        # アプリ起動時にフローティングインジケーターを表示（待機状態）
        print("[DEBUG] アプリ起動時にフローティングインジケーターを表示")
        # 初期状態では表示しない（録音開始時に表示）
        print(f"[DEBUG] 起動後フローティングインジケーター状態: visible={self.floating_indicator.isVisible()}")
        
        # ダークモード判定
        self.is_dark = is_dark_mode()
        
        # UIの設定
        self.init_ui()
        
        # シグナルの接続
        self.transcription_complete.connect(self.on_transcription_complete)
        self.recording_status_changed.connect(self.update_recording_status)
        
        # モデルの初期化確認
        if not self.whisper_transcriber:
            QMessageBox.warning(self, "モデル初期化エラー", "Whisperモデルの初期化に失敗しました。\nインターネット接続を確認し、アプリケーションを再起動してください。", QMessageBox.StandardButton.Ok)
            
        # 追加の接続設定
        self.setup_connections()
        
        # グローバルホットキーの設定
        self.setup_global_hotkey()
        
        # システムトレイの設定
        self.setup_system_tray()

        # マイク権限リクエスト（macOS用）
        try:
            request_microphone_permission()
        except Exception as e:
            print(f"[Permission] マイク権限リクエスト失敗: {e}")
        # マイク権限チェック
        if not has_microphone_permission():
            QMessageBox.warning(self, "マイク権限がありません", "このアプリを使うにはマイクへのアクセス許可が必要です。\nシステム設定→プライバシーとセキュリティ→マイク から許可してください。", QMessageBox.StandardButton.Ok)
    
    def init_ui(self):
        """
        ユーザーインターフェースを初期化する
        
        ウィンドウのサイズ、タイトル、スタイル、レイアウト、
        およびウィジェットの配置を設定します。
        """
        self.setWindowTitle(AppLabels.APP_TITLE)
        self.setMinimumSize(1200, 600)
        self.setFixedSize(1200, 600)  # ウィンドウサイズを固定
        
        # アプリケーションアイコンを設定
        icon_path = getResourcePath("assets/icon.ico")
        
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # アイコンファイルが見つからない場合は標準アイコンを使用
            self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            print(f"Warning: Icon file not found: {icon_path}")
            
        # アプリ全体のスタイルを設定
        # --- テーマ切り替え ---
        if hasattr(self, "is_dark") and self.is_dark:
            self.setStyleSheet(AppStyles.MAIN_WINDOW_STYLE_DARK)
        else:
            self.setStyleSheet(AppStyles.MAIN_WINDOW_STYLE)
        
        # 中央ウィジェットとメインレイアウトの作成
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # ツールバーの作成
        self.create_toolbar()
        
        # コントロールパネル
        control_panel = QWidget()
        control_panel.setObjectName("controlPanel")
        if hasattr(self, "is_dark") and self.is_dark:
            control_panel.setStyleSheet(AppStyles.CONTROL_PANEL_STYLE_DARK)
        else:
            control_panel.setStyleSheet(AppStyles.CONTROL_PANEL_STYLE)
        control_layout = QGridLayout()
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(12)
        
        # 録音コントロール
        self.record_button = QPushButton(AppLabels.RECORD_START_BUTTON)
        self.record_button.setObjectName("recordButton")
        self.record_button.setMinimumHeight(40)
        self.record_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.record_button.setStyleSheet(AppStyles.RECORD_BUTTON_STYLE)
        self.record_button.clicked.connect(self.toggle_recording)
        
        # コントロールフォーム
        control_form = QWidget()
        form_layout = QFormLayout(control_form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(10)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # 言語選択
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("languageCombo")
        
        # 言語オプションの追加
        self.language_combo.addItem(AppLabels.AUTO_DETECT, "")
        self.language_combo.addItem(AppLabels.LANGUAGE_ENGLISH, "en")
        self.language_combo.addItem(AppLabels.LANGUAGE_SPANISH, "es")
        self.language_combo.addItem(AppLabels.LANGUAGE_FRENCH, "fr")
        self.language_combo.addItem(AppLabels.LANGUAGE_GERMAN, "de")
        self.language_combo.addItem(AppLabels.LANGUAGE_ITALIAN, "it")
        self.language_combo.addItem(AppLabels.LANGUAGE_PORTUGUESE, "pt")
        self.language_combo.addItem(AppLabels.LANGUAGE_JAPANESE, "ja")
        self.language_combo.addItem(AppLabels.LANGUAGE_KOREAN, "ko")
        self.language_combo.addItem(AppLabels.LANGUAGE_CHINESE, "zh")
        self.language_combo.addItem(AppLabels.LANGUAGE_RUSSIAN, "ru")
        
        # モデル選択
        self.model_combo = QComboBox()
        self.model_combo.setObjectName("modelCombo")
        
        # モデルリストを取得してコンボボックスに追加
        for model in WhisperTranscriber.get_available_models():
            self.model_combo.addItem(model["name"], model["id"])
            # ツールチップを追加
            self.model_combo.setItemData(
                self.model_combo.count() - 1, 
                model["description"], 
                Qt.ItemDataRole.ToolTipRole
            )
        
        # 前回選択したモデルを設定
        last_model = self.settings.value("model", AppConfig.DEFAULT_MODEL)
        index = self.model_combo.findData(last_model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
            
        # フォームにフィールドを追加
        language_label = QLabel(AppLabels.LANGUAGE_LABEL)
        language_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        model_label = QLabel(AppLabels.MODEL_LABEL)
        model_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        form_layout.addRow(language_label, self.language_combo)
        form_layout.addRow(model_label, self.model_combo)
        
        # 録音デバイス選択
        self.device_combo = QComboBox()
        self.device_combo.setObjectName("deviceCombo")
        self.device_index_map = []  # index -> device_id
        devices = sd.query_devices()
        input_devices = [(i, d) for i, d in enumerate(devices) if d['max_input_channels'] > 0]
        for idx, dev in input_devices:
            label = f"{dev['name']} (id:{idx})"
            self.device_combo.addItem(label, idx)
            self.device_index_map.append(idx)
        # 前回選択したデバイスを復元
        last_device = self.settings.value("input_device", None)
        if last_device is not None:
            combo_idx = self.device_combo.findData(int(last_device))
            if combo_idx >= 0:
                self.device_combo.setCurrentIndex(combo_idx)
        self.device_combo.currentIndexChanged.connect(self.on_device_changed)
        device_label = QLabel("録音デバイス")
        device_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form_layout.insertRow(0, device_label, self.device_combo)
        
        # レイアウトに追加
        control_layout.addWidget(self.record_button, 0, 0, 2, 1)
        control_layout.addWidget(control_form, 0, 1, 2, 5)
        control_layout.setColumnStretch(0, 1)  # 録音ボタンの列
        control_layout.setColumnStretch(1, 3)  # フォームの列
        
        control_panel.setLayout(control_layout)
        main_layout.addWidget(control_panel)
        
        # 文字起こしパネル
        transcription_panel = QWidget()
        transcription_panel.setObjectName("transcriptionPanel")
        if hasattr(self, "is_dark") and self.is_dark:
            transcription_panel.setStyleSheet(AppStyles.CONTROL_PANEL_STYLE_DARK)
        else:
            transcription_panel.setStyleSheet(AppStyles.TRANSCRIPTION_PANEL_STYLE)
        
        transcription_layout = QVBoxLayout(transcription_panel)
        transcription_layout.setContentsMargins(15, 15, 15, 15)
        
        # タイトルラベル
        title_label = QLabel(AppLabels.TRANSCRIPTION_TITLE)
        title_label.setObjectName("sectionTitle")
        title_label.setStyleSheet(AppStyles.TRANSCRIPTION_TITLE_STYLE)
        transcription_layout.addWidget(title_label)
        
        # 文字起こし出力
        self.transcription_text = QTextEdit()
        self.transcription_text.setPlaceholderText(AppLabels.TRANSCRIPTION_PLACEHOLDER)
        self.transcription_text.setReadOnly(False)  # 編集できるように設定
        self.transcription_text.setMinimumHeight(250)
        if hasattr(self, "is_dark") and self.is_dark:
            self.transcription_text.setStyleSheet(AppStyles.TRANSCRIPTION_TEXT_STYLE_DARK)
        else:
            self.transcription_text.setStyleSheet(AppStyles.TRANSCRIPTION_TEXT_STYLE)
        
        transcription_layout.addWidget(self.transcription_text)
        main_layout.addWidget(transcription_panel, 1)
        
        # ステータスバー
        self.status_bar = self.statusBar()
        self.status_bar.showMessage(AppLabels.STATUS_READY)
        self.status_bar.setStyleSheet(AppStyles.STATUS_BAR_STYLE)
        # 録音デバイス名表示
        self.device_status_label = QLabel()
        self.status_bar.addPermanentWidget(self.device_status_label)
        self.update_device_status_label()
        
        # 録音インジケーター
        self.recording_indicator = QLabel("●")
        self.recording_indicator.setObjectName("recordingIndicator")
        self.recording_indicator.setStyleSheet(AppStyles.RECORDING_INDICATOR_NORMAL_STYLE)
        
        self.recording_timer_label = QLabel("00:00")
        self.recording_timer_label.setObjectName("recordingTimerLabel")
        self.recording_timer_label.setStyleSheet(AppStyles.RECORDING_TIMER_LABEL_STYLE)
        
        self.status_bar.addPermanentWidget(self.recording_indicator)
        self.status_bar.addPermanentWidget(self.recording_timer_label)
        
        # 録音タイマーのセットアップ
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_recording_time)
        self.recording_start_time = 0
        
        # 録音インジケーター点滅タイマーのセットアップ
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.blink_recording_indicator)
        self.blink_timer.setInterval(500)  # 0.5秒間隔で点滅
        self.is_blinking = False
        
        # レイアウトの完了
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def create_toolbar(self):
        """
        アクション付きツールバーを作成する
        
        アプリケーションの主要機能にアクセスするためのツールバーボタンを設定します。
        """
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        

        
        # カスタム語彙アクション
        vocabulary_action = QAction(AppLabels.CUSTOM_VOCABULARY, self)
        vocabulary_action.triggered.connect(self.show_vocabulary_dialog)
        toolbar.addAction(vocabulary_action)
        
        # システム指示アクション
        system_instructions_action = QAction(AppLabels.SYSTEM_INSTRUCTIONS, self)
        system_instructions_action.triggered.connect(self.show_system_instructions_dialog)
        toolbar.addAction(system_instructions_action)
        
        # クリップボードにコピーアクション
        copy_action = QAction(AppLabels.COPY_TO_CLIPBOARD, self)
        copy_action.triggered.connect(self.copy_to_clipboard)
        toolbar.addAction(copy_action)
        
        # セパレーター追加
        toolbar.addSeparator()
        
        # グローバルホットキー設定
        hotkey_action = QAction(AppLabels.HOTKEY_SETTINGS, self)
        hotkey_action.triggered.connect(self.show_hotkey_dialog)
        toolbar.addAction(hotkey_action)
        
        # 自動コピーオプション
        self.auto_copy_action = QAction(AppLabels.AUTO_COPY, self)
        self.auto_copy_action.setCheckable(True)
        self.auto_copy_action.setChecked(self.auto_copy)
        self.auto_copy_action.triggered.connect(self.toggle_auto_copy)
        toolbar.addAction(self.auto_copy_action)
        
        # サウンドオプション
        self.sound_action = QAction(AppLabels.SOUND_NOTIFICATION, self)
        self.sound_action.setCheckable(True)
        self.sound_action.setChecked(self.enable_sound)
        self.sound_action.triggered.connect(self.toggle_sound_option)
        toolbar.addAction(self.sound_action)
        
        # インジケータ表示オプション
        self.indicator_action = QAction(AppLabels.STATUS_INDICATOR, self)
        self.indicator_action.setCheckable(True)
        self.indicator_action.setChecked(self.show_indicator)
        self.indicator_action.triggered.connect(self.toggle_indicator_option)
        toolbar.addAction(self.indicator_action)
        
        # セパレーター追加
        toolbar.addSeparator()
        
        # 終了アクション
        exit_action = QAction(AppLabels.EXIT_APP, self)
        exit_action.triggered.connect(self.quit_application)
        exit_action.setShortcut("Alt+F4")  # 終了ショートカットを追加
        toolbar.addAction(exit_action)
    

    
    def show_vocabulary_dialog(self):
        """
        カスタム語彙管理ダイアログを表示する
        
        文字起こしの精度向上のためのカスタム語彙を管理するダイアログを表示します。
        """
        if not self.whisper_transcriber:
            QMessageBox.warning(self, AppLabels.ERROR_TITLE, "Whisperモデルが初期化されていません。")
            return
            
        vocabulary = self.whisper_transcriber.get_custom_vocabulary()
        dialog = VocabularyDialog(self, vocabulary)
        
        if dialog.exec():
            new_vocabulary = dialog.get_vocabulary()
            self.whisper_transcriber.clear_custom_vocabulary()
            self.whisper_transcriber.add_custom_vocabulary(new_vocabulary)
            # カスタム語彙を保存
            self._save_vocabulary()
            self.status_bar.showMessage(AppLabels.STATUS_VOCABULARY_ADDED.format(len(new_vocabulary)), 3000)
    
    def show_system_instructions_dialog(self):
        """システム指示を管理するダイアログを表示"""
        if not self.whisper_transcriber:
            QMessageBox.warning(self, AppLabels.ERROR_TITLE, "Whisperモデルが初期化されていません。")
            return
            
        instructions = self.whisper_transcriber.get_system_instructions()
        dialog = SystemInstructionsDialog(self, instructions)
        
        if dialog.exec():
            new_instructions = dialog.get_instructions()
            self.whisper_transcriber.clear_system_instructions()
            self.whisper_transcriber.add_system_instruction(new_instructions)
            # システム指示を保存
            self._save_system_instructions()
            self.status_bar.showMessage(AppLabels.STATUS_INSTRUCTIONS_SET.format(len(new_instructions)), 3000)
    
    def toggle_recording(self):
        """
        録音の開始/停止を切り替える
        
        現在の録音状態に応じて、録音を開始または停止します。
        """
        # GUIスレッドでの実行を保証するためQTimer.singleShotを使用
        QTimer.singleShot(0, self._toggle_recording_impl)
    
    def _toggle_recording_impl(self):
        """
        実際の録音切り替え処理の実装
        
        録音の状態を確認し、録音の開始または停止を行います。
        """
        if self.audio_recorder.is_recording():
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """
        録音を開始する
        
        音声録音を開始し、UIの状態を更新します。
        録音中は録音ボタンのテキストが「停止」に変更され、
        録音時間の表示が開始されます。
        """
        # 既に録音中の場合は処理をスキップ
        if self.is_recording:
            print("[Recording] 既に録音中のため、重複実行をスキップ")
            return
            
        try:
            # 録音デバイスの確認
            if not has_microphone_permission():
                QMessageBox.warning(self, "マイク権限がありません", 
                    "このアプリを使うにはマイクへのアクセス許可が必要です。\nシステム設定→プライバシーとセキュリティ→マイク から許可してください。", 
                    QMessageBox.StandardButton.Ok)
                return
            
            # 録音開始
            self.audio_recorder.start_recording()
            self.is_recording = True
            
            # UI更新
            self.record_button.setText(AppLabels.RECORD_STOP_BUTTON)
            self.record_button.setStyleSheet(AppStyles.RECORD_BUTTON_RECORDING_STYLE)
            
            # 録音時間の表示開始
            self.recording_timer.start(1000)
            
            # 録音インジケータの表示
            if self.show_indicator:
                self.status_indicator_window.show()
                self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_RECORDING)
            
            # フローティングインジケーターの表示
            self.floating_indicator.start_recording()
            
            # 音声フィードバック
            if self.enable_sound:
                self.play_start_sound()
            
            # メニューバーアイコンに通知
            if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
                self.tray_icon.showMessage(
                    "録音開始", 
                    "音声録音を開始しました", 
                    QSystemTrayIcon.MessageIcon.Information, 
                    2000
                )
            
            # シグナル発火
            self.recording_status_changed.emit(True)
            
            print("[Recording] 録音開始")
            
        except Exception as e:
            QMessageBox.critical(self, "録音エラー", f"録音の開始に失敗しました: {str(e)}")
            print(f"[Recording] 録音開始エラー: {e}")

    def stop_recording(self):
        """
        録音を停止する
        
        音声録音を停止し、UIの状態を更新します。
        録音停止後は録音ボタンのテキストが「開始」に変更され、
        録音時間の表示が停止されます。
        """
        try:
            # 録音停止
            audio_file = self.audio_recorder.stop_recording()
            self.is_recording = False
            
            # UI更新
            self.record_button.setText(AppLabels.RECORD_START_BUTTON)
            self.record_button.setStyleSheet(AppStyles.RECORD_BUTTON_STYLE)
            
            # 録音時間の表示停止
            self.recording_timer.stop()
            self.recording_timer_label.setText("00:00")
            
            # 録音インジケータの非表示
            if self.show_indicator:
                self.status_indicator_window.hide()
            
            # フローティングインジケーターの非表示
            self.floating_indicator.stop_recording()
            
            # 音声フィードバック
            if self.enable_sound:
                self.play_stop_sound()
            
            # メニューバーアイコンに通知
            if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
                self.tray_icon.showMessage(
                    "録音停止", 
                    "音声録音を停止しました", 
                    QSystemTrayIcon.MessageIcon.Information, 
                    2000
                )
            
            # シグナル発火
            self.recording_status_changed.emit(False)
            
            # 文字起こし開始
            if audio_file:
                self.start_transcription(audio_file)
            
            print("[Recording] 録音停止")
            
        except Exception as e:
            QMessageBox.critical(self, "録音エラー", f"録音の停止に失敗しました: {str(e)}")
            print(f"[Recording] 録音停止エラー: {e}")
    
    def update_recording_status(self, is_recording):
        """
        録音インジケーターの状態を更新する
        
        Parameters
        ----------
        is_recording : bool
            録音中かどうかのフラグ
        
        録音状態に応じてUIの録音インジケーターとボタンのスタイルを更新します。
        """
        if is_recording:
            self.recording_indicator.setStyleSheet(AppStyles.RECORDING_INDICATOR_ACTIVE_STYLE)
            
            # 録音ボタンのスタイルも変更
            self.record_button.setStyleSheet(AppStyles.RECORD_BUTTON_RECORDING_STYLE)
        else:
            # 点滅を停止して通常状態に戻す
            self.is_blinking = False
            self.blink_timer.stop()
            self.recording_indicator.setStyleSheet(AppStyles.RECORDING_INDICATOR_INACTIVE_STYLE)
            
            # 録音ボタンのスタイルを元に戻す
            self.record_button.setStyleSheet(AppStyles.RECORD_BUTTON_STYLE)
    
    def update_recording_time(self):
        """
        録音時間表示を更新する
        
        録音中の経過時間を計算し、タイマー表示を更新します。
        インジケーターウィンドウのタイマー表示も同時に更新します。
        """
        if self.audio_recorder.is_recording():
            elapsed = int(time.time() - self.recording_start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            self.recording_timer_label.setText(time_str)
    
    def blink_recording_indicator(self):
        """
        録音インジケーターの点滅効果を制御する
        
        録音中はインジケーターを点滅させて視覚的なフィードバックを提供します。
        """
        if self.is_blinking:
            # 点滅状態を切り替え
            if self.recording_indicator.styleSheet() == AppStyles.RECORDING_INDICATOR_ACTIVE_STYLE:
                self.recording_indicator.setStyleSheet("color: #5B7FDE; font-size: 18px; font-weight: bold; opacity: 0.6;")
            else:
                self.recording_indicator.setStyleSheet(AppStyles.RECORDING_INDICATOR_ACTIVE_STYLE)
    
    def start_transcription(self, audio_file=None):
        """
        文字起こしを開始する
        
        Parameters
        ----------
        audio_file : str, optional
            文字起こしを行う音声ファイルのパス
        
        録音した音声ファイルの文字起こしを開始し、UIの状態を更新します。
        """
        self.status_bar.showMessage(AppLabels.STATUS_TRANSCRIBING)
        
        # 文字起こし中状態の表示
        if self.show_indicator:
            # 念のため、一度ウィンドウを隠してリセット
            self.status_indicator_window.hide()
            self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_TRANSCRIBING)
            self.status_indicator_window.show()
        
        # 言語の選択
        selected_language = self.language_combo.currentData()
        
        # バックグラウンドスレッドで文字起こし処理を実行
        if audio_file:
            # 処理開始時間を記録
            self._transcription_start_time = time.time()
            
            transcription_thread = threading.Thread(
                target=self.perform_transcription,
                args=(audio_file, selected_language)
            )
            transcription_thread.daemon = True
            transcription_thread.start()
    
    def perform_transcription(self, audio_file, language=None):
        """
        バックグラウンドスレッドで文字起こし処理を実行する
        
        Parameters
        ----------
        audio_file : str
            文字起こしを行う音声ファイルのパス
        language : str, optional
            文字起こしの言語コード
        
        WhisperTranscriberを使用して実際の文字起こし処理を行い、結果を
        シグナルで通知します。エラー発生時も適切にハンドリングします。
        """
        try:
            # デバッグ: ファイルの存在とサイズをログに出力
            import os
            try:
                size = os.path.getsize(audio_file)
            except Exception as e:
                size = f"Error: {e}"
            with open("/tmp/recorder_debug.log", "a") as logf:
                logf.write(f"Transcribe input file: {audio_file}, size: {size}\n")
            
            # 音声を文字起こし
            result = self.whisper_transcriber.transcribe(audio_file, language)
            
            # 処理時間を計算
            processing_time = time.time() - self._transcription_start_time
            print(f"[INFO] Total transcription time: {processing_time:.2f} seconds")
            
            # 結果でシグナルを発信
            self.transcription_complete.emit(result)
            
        except Exception as e:
            # エラー処理
            processing_time = time.time() - self._transcription_start_time
            print(f"[ERROR] Transcription failed after {processing_time:.2f} seconds: {e}")
            self.transcription_complete.emit(AppLabels.ERROR_TRANSCRIPTION.format(str(e)))
    
    def on_transcription_complete(self, text):
        """
        文字起こし完了時の処理
        
        Parameters
        ----------
        text : str
            文字起こし結果のテキスト
        
        文字起こし結果をテキストウィジェットに表示し、設定に応じて
        クリップボードにコピーします。また、完了サウンドを再生します。
        """
        # 文字起こし結果でテキストウィジェットを更新
        self.transcription_text.setPlainText(text)
        
        # 使用したモデル名を取得
        model_id = self.model_combo.currentData()
        model_name = self.model_combo.currentText()
        
        # 処理時間を取得
        total_time = time.time() - self._transcription_start_time
        whisper_time = self.whisper_transcriber.get_last_transcription_time()
        
        # 文字起こし完了状態の表示
        if self.show_indicator:
            self.status_indicator_window.set_mode(StatusIndicatorWindow.MODE_TRANSCRIBED)
            self.status_indicator_window.show()
        
        # 有効な場合は自動でクリップボードにコピー＆ペースト
        if self.auto_copy and text:
            QApplication.clipboard().setText(text)
            status_message = f"{AppLabels.STATUS_TRANSCRIBED_COPIED} (使用モデル: {model_name}, 処理時間: {total_time:.1f}s)"
            self.status_bar.showMessage(status_message, 3000)
            # システム通知は表示しない
            # macOSで自動ペースト
            if platform.system() == "Darwin" and pyautogui is not None:
                try:
                    pyautogui.hotkey('command', 'v')
                except Exception as e:
                    print(f"[AutoPasteError] {e}")
        else:
            status_message = f"{AppLabels.STATUS_TRANSCRIBED} (使用モデル: {model_name}, 処理時間: {total_time:.1f}s)"
            self.status_bar.showMessage(status_message, 3000)
        
        # 完了音を再生
        self.play_complete_sound()
    
    def copy_to_clipboard(self):
        """
        文字起こし結果をクリップボードにコピーする
        
        現在のテキストウィジェットの内容をクリップボードにコピーし、
        ユーザーに通知します。
        """
        text = self.transcription_text.toPlainText()
        QApplication.clipboard().setText(text)
        self.status_bar.showMessage(AppLabels.STATUS_COPIED, 2000)
        
        # 手動コピー時はインジケータを表示しない
    
    def setup_connections(self):
        """追加の接続設定"""
        # モデル選択が変更されたときのイベント
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
    
    def on_model_changed(self, index):
        """モデルが変更されたときの処理"""
        model_id = self.model_combo.currentData()
        if model_id and self.whisper_transcriber:
            self.whisper_transcriber.set_model(model_id)
            self.settings.setValue("model", model_id)
            model_name = self.model_combo.currentText()
            self.status_bar.showMessage(AppLabels.STATUS_MODEL_CHANGED.format(model_name), 2000)

    def setup_global_hotkey(self):
        """
        グローバルホットキーを設定する
        
        Returns
        -------
        bool
            ホットキー設定の成功・失敗
        
        アプリケーション全体で使用するグローバルホットキーを設定します。
        エラーが発生しても、アプリケーションは引き続き動作します。
        """
        try:
            result = self.hotkey_manager.register_hotkey(self.hotkey, self.toggle_recording)
            
            if result:
                print(f"[DEBUG-TEST] HOTKEY SET: {self.hotkey}")
                return True
            else:
                raise ValueError(f"Failed to register hotkey: {self.hotkey}")
        except Exception as e:
            error_msg = f"Hotkey setup error: {e}"
            print(error_msg)
            # エラーメッセージをユーザーに表示
            self.status_bar.showMessage(AppLabels.ERROR_HOTKEY.format(str(e)), 5000)
            # エラーがあってもアプリは正常に動作するようにする
            return False
    
    def restart_app(self):
        """
        アプリケーションを自動再起動する
        """
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    def show_hotkey_dialog(self):
        """
        グローバルホットキー設定ダイアログを表示する
        
        ホットキーの設定を変更するためのダイアログを表示します。
        ダイアログ表示中は現在のホットキーを一時的に解除します。
        """
        # 現在のリスナーを一時的に停止
        self.hotkey_manager.stop_listener()
        
        dialog = HotkeyDialog(self, self.hotkey)
        if dialog.exec():
            new_hotkey = dialog.get_hotkey()
            if new_hotkey:
                self.hotkey = new_hotkey
                self.settings.setValue("hotkey", self.hotkey)
                self.settings.sync()
                self.setup_global_hotkey()
                self.status_bar.showMessage(AppLabels.STATUS_HOTKEY_SET.format(self.hotkey), 3000)
                self.restart_app()
        else:
            # ダイアログがキャンセルされた場合は元のホットキーを再設定
            self.setup_global_hotkey()
    
    def toggle_auto_copy(self):
        """
        自動コピー機能のオン/オフを切り替える
        
        文字起こし完了時の自動クリップボードコピー機能の有効/無効を
        切り替え、設定を保存します。
        """
        self.auto_copy = self.auto_copy_action.isChecked()
        self.settings.setValue("auto_copy", self.auto_copy)
        if self.auto_copy:
            self.status_bar.showMessage(AppLabels.STATUS_AUTO_COPY_ENABLED, 2000)
        else:
            self.status_bar.showMessage(AppLabels.STATUS_AUTO_COPY_DISABLED, 2000)
    
    def quit_application(self):
        """
        アプリケーションを完全に終了する
        
        ホットキーの登録解除、トレイアイコンの削除、
        およびアプリケーションの完全終了を行います。
        """
        try:
            # 録音中なら停止
            if self.is_recording:
                self.stop_recording()
            
            # フローティングインジケーターを非表示・クリーンアップ
            if hasattr(self, 'floating_indicator'):
                self.floating_indicator.hide()
                # ネイティブAPI版のクリーンアップ
                self.floating_indicator.cleanup()
            
            # カスタム語彙とシステム指示を保存
            self._save_vocabulary()
            self._save_system_instructions()
            
            # ホットキーの登録解除
            if self.hotkey_manager:
                self.hotkey_manager.unregister_hotkey()
            
            # トレイアイコンの削除
            if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
                self.tray_icon.hide()
            
            # アプリケーション終了
            QApplication.quit()
            
        except Exception as e:
            print(f"[Quit] アプリケーション終了エラー: {e}")
            QApplication.quit()
    
    def setup_sound_players(self):
        """サウンドプレーヤーの初期化"""
        # 録音開始用サウンドプレーヤー
        self.start_player = QMediaPlayer()
        self.start_audio_output = QAudioOutput()
        self.start_player.setAudioOutput(self.start_audio_output)
        
        # 録音終了用サウンドプレーヤー
        self.stop_player = QMediaPlayer()
        self.stop_audio_output = QAudioOutput()
        self.stop_player.setAudioOutput(self.stop_audio_output)
        
        # 文字起こし完了用サウンドプレーヤー
        self.complete_player = QMediaPlayer()
        self.complete_audio_output = QAudioOutput()
        self.complete_player.setAudioOutput(self.complete_audio_output)
    
    def play_start_sound(self):
        """
        録音開始サウンドを再生する
        
        enable_soundがTrueの場合のみ再生します
        """
        if not self.enable_sound:
            return
        
        # 既に再生中の場合は停止してから再生
        if self.start_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.start_player.stop()
            print("[Sound] 既存の開始音を停止してから再生")
        
        # assets内の音声ファイルを使用
        sound_path = getResourcePath(AppConfig.START_SOUND_PATH)
        self.start_player.setSource(QUrl.fromLocalFile(sound_path))
        self.start_audio_output.setVolume(0.5)
        self.start_player.play()
        print("[Sound] 録音開始音を再生")
    
    def play_stop_sound(self):
        """
        録音終了サウンドを再生する
        
        enable_soundがTrueの場合のみ再生します
        """
        if not self.enable_sound:
            return
        
        # 既に再生中の場合は停止してから再生
        if self.stop_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.stop_player.stop()
            print("[Sound] 既存の停止音を停止してから再生")
        
        # assets内の音声ファイルを使用
        sound_path = getResourcePath(AppConfig.STOP_SOUND_PATH)
        self.stop_player.setSource(QUrl.fromLocalFile(sound_path))
        self.stop_audio_output.setVolume(0.5)
        self.stop_player.play()
        print("[Sound] 録音停止音を再生")
    
    def play_complete_sound(self):
        """
        文字起こし完了サウンドを再生する
        
        enable_soundがTrueの場合のみ再生します
        """
        if not self.enable_sound:
            return
        
        # 既に再生中の場合は停止してから再生
        if self.complete_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.complete_player.stop()
            print("[Sound] 既存の完了音を停止してから再生")
        
        # assets内の音声ファイルを使用
        sound_path = getResourcePath(AppConfig.COMPLETE_SOUND_PATH)
        self.complete_player.setSource(QUrl.fromLocalFile(sound_path))
        self.complete_audio_output.setVolume(0.5)
        self.complete_player.play()
        print("[Sound] 文字起こし完了音を再生")

    def toggle_sound_option(self):
        """
        通知音のオン/オフを切り替える
        
        設定を保存し、状態をステータスバーに表示します
        """
        self.enable_sound = self.sound_action.isChecked()
        self.settings.setValue("enable_sound", self.enable_sound)
        if self.enable_sound:
            self.status_bar.showMessage(AppLabels.STATUS_SOUND_ENABLED, 2000)
        else:
            self.status_bar.showMessage(AppLabels.STATUS_SOUND_DISABLED, 2000)

    def toggle_indicator_option(self):
        """
        インジケータ表示のオン/オフを切り替える
        
        設定を保存し、状態をステータスバーに表示します
        """
        self.show_indicator = self.indicator_action.isChecked()
        self.settings.setValue("show_indicator", self.show_indicator)
        
        # インジケータが無効になったら非表示にする
        if not self.show_indicator:
            self.status_indicator_window.hide()
            
        if self.show_indicator:
            self.status_bar.showMessage(AppLabels.STATUS_INDICATOR_SHOWN, 2000)
        else:
            self.status_bar.showMessage(AppLabels.STATUS_INDICATOR_HIDDEN, 2000)

    def setup_system_tray(self):
        """
        システムトレイアイコンとメニューの設定
        """
        import platform
        # アイコンファイルのパスを取得（OSごとに切り替え）
        if platform.system() == "Darwin":
            icon_path = getResourcePath("assets/icon.icns")
        else:
            icon_path = getResourcePath("assets/icon.ico")
        if os.path.exists(icon_path):
            self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
        else:
            # アイコンファイルが見つからない場合は標準アイコンを使用
            self.tray_icon = QSystemTrayIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay), self)
        self.tray_icon.setToolTip(AppLabels.APP_TITLE)
        
        # トレイメニューをスタイル付きで作成
        menu = QMenu()
        menu.setStyleSheet(AppStyles.SYSTEM_TRAY_MENU_STYLE)
        
        # 表示/非表示アクションを追加
        show_action = QAction(AppLabels.TRAY_SHOW, self)
        show_action.triggered.connect(self.show)
        menu.addAction(show_action)
        
        # セパレーターを追加
        menu.addSeparator()
        
        # 録音アクションを追加（状態に応じてテキスト変更）
        self.record_action = QAction(AppLabels.TRAY_RECORD, self)
        self.record_action.triggered.connect(self.toggle_recording)
        menu.addAction(self.record_action)
        
        # 録音状態表示アクションを追加
        self.status_action = QAction("録音状態: 停止中", self)
        self.status_action.setEnabled(False)  # クリック不可
        menu.addAction(self.status_action)
        
        # セパレーターを追加
        menu.addSeparator()
        
        # 設定メニューを追加
        settings_menu = QMenu("設定", self)
        
        # 音声設定
        sound_action = QAction("音声フィードバック", self)
        sound_action.setCheckable(True)
        sound_action.setChecked(self.enable_sound)
        sound_action.triggered.connect(self.toggle_sound_option)
        settings_menu.addAction(sound_action)
        
        # インジケータ設定
        indicator_action = QAction("録音インジケータ", self)
        indicator_action.setCheckable(True)
        indicator_action.setChecked(self.show_indicator)
        indicator_action.triggered.connect(self.toggle_indicator_option)
        settings_menu.addAction(indicator_action)
        
        # 自動コピー設定
        auto_copy_action = QAction("自動クリップボードコピー", self)
        auto_copy_action.setCheckable(True)
        auto_copy_action.setChecked(self.auto_copy)
        auto_copy_action.triggered.connect(self.toggle_auto_copy)
        settings_menu.addAction(auto_copy_action)
        
        # ネイティブAPI版フローティングウィンドウ設定
        native_api_action = QAction("ネイティブAPI版フローティングウィンドウ", self)
        native_api_action.setCheckable(True)
        native_api_action.setChecked(self.settings.value("use_native_floating_api", True, type=bool))
        native_api_action.triggered.connect(self.toggle_native_api_option)
        settings_menu.addAction(native_api_action)
        
        # デバッグ用：ネイティブAPI版強制有効化
        force_native_api_action = QAction("🔧 デバッグ: ネイティブAPI版強制有効化", self)
        force_native_api_action.setCheckable(True)
        force_native_api_action.setChecked(self.settings.value("force_native_api_debug", False, type=bool))
        force_native_api_action.triggered.connect(self.toggle_force_native_api_option)
        settings_menu.addAction(force_native_api_action)
        
        menu.addMenu(settings_menu)
        
        # セパレーターを追加
        menu.addSeparator()
        
        # 終了アクションを追加
        exit_action = QAction(AppLabels.TRAY_EXIT, self)
        exit_action.triggered.connect(self.quit_application)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
        
        # 録音状態の変更を監視
        self.recording_status_changed.connect(self.update_tray_icon_status)

    def update_tray_icon_status(self, is_recording):
        """
        メニューバーアイコンの状態を更新
        
        Parameters
        ----------
        is_recording : bool
            録音中かどうか
        """
        if hasattr(self, 'record_action') and hasattr(self, 'status_action'):
            if is_recording:
                self.record_action.setText("録音停止")
                self.status_action.setText("録音状態: 録音中 🔴")
                # 録音中はアイコンを赤くする（macOSでは色変更は制限あり）
                self.tray_icon.setToolTip(f"{AppLabels.APP_TITLE} - 録音中")
                # 録音中の視覚的フィードバック
                self._set_recording_icon()
            else:
                self.record_action.setText("録音開始")
                self.status_action.setText("録音状態: 停止中")
                self.tray_icon.setToolTip(AppLabels.APP_TITLE)
                # 通常アイコンに戻す
                self._set_normal_icon()

    def _set_recording_icon(self):
        """
        録音中のアイコンを設定
        """
        import platform
        if platform.system() == "Darwin":
            # macOSでは色変更の制限があるため、ツールチップで状態を表示
            pass
        else:
            # Windows/Linuxでは赤いアイコンを使用
            recording_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)
            self.tray_icon.setIcon(recording_icon)

    def _set_normal_icon(self):
        """
        通常のアイコンを設定
        """
        import platform
        import os
        if platform.system() == "Darwin":
            icon_path = getResourcePath("assets/icon.icns")
        else:
            icon_path = getResourcePath("assets/icon.ico")
        
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # アイコンファイルが見つからない場合は標準アイコンを使用
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def tray_icon_activated(self, reason):
        """
        トレイアイコンがアクティブ化されたときの処理
        
        Parameters
        ----------
        reason : QSystemTrayIcon.ActivationReason
            アクティブ化の理由
        
        トレイアイコンがクリックされたときに、ウィンドウの表示/非表示を切り替えます。
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()

    def closeEvent(self, event):
        """
        ウィンドウの閉じるイベントを処理する
        
        Parameters
        ----------
        event : QCloseEvent
            閉じるイベント
        
        ウィンドウの閉じるボタンが押されたときの処理を行います。
        Alt+F4で完全終了、それ以外はトレイに最小化します。
        """
        # Alt+F4 またはシステムのクローズ要求によって呼ばれる
        
        # Alt キーが押されている場合は完全に終了
        if QApplication.keyboardModifiers() == Qt.KeyboardModifier.AltModifier:
            self.quit_application()
            event.accept()
        # 通常の閉じる操作ではトレイに最小化
        elif self.tray_icon.isVisible():
            QMessageBox.information(self, AppLabels.INFO_TITLE, 
                AppLabels.INFO_TRAY_MINIMIZED)
            self.hide()
            event.ignore()
        else:
            event.accept()

    def on_device_changed(self, combo_idx):
        device_id = self.device_combo.itemData(combo_idx)
        self.settings.setValue("input_device", device_id)
        self.update_device_status_label()

    def update_device_status_label(self):
        idx = self.device_combo.currentIndex()
        name = self.device_combo.itemText(idx)
        self.device_status_label.setText(f"🎤 {name}")

    def show_floating_indicator_for_test(self):
        """
        テスト用にフローティングインジケーターを強制表示
        """
        print("[DEBUG] show_floating_indicator_for_test() 呼び出し")
        print(f"[DEBUG] 現在のfloating_indicator.isVisible(): {self.floating_indicator.isVisible()}")
        if not self.floating_indicator.isVisible():
            print("[DEBUG] テスト用フローティングインジケーター表示")
            self.floating_indicator.start_recording()
            print(f"[DEBUG] 表示後 floating_indicator.isVisible(): {self.floating_indicator.isVisible()}  geometry: {self.floating_indicator.geometry()}")
        else:
            print("[DEBUG] 既にフローティングインジケーターは表示中")

    def _load_saved_vocabulary(self):
        """保存されたカスタム語彙を読み込む"""
        if self.whisper_transcriber:
            try:
                print(f"[DEBUG] カスタム語彙の読み込み開始")
                saved_vocabulary_json = self.settings.value("custom_vocabulary", "")
                if saved_vocabulary_json:
                    saved_vocabulary = json.loads(saved_vocabulary_json)
                    print(f"[DEBUG] 設定から読み込まれた語彙: {saved_vocabulary}")
                    print(f"[DEBUG] 語彙の型: {type(saved_vocabulary)}")
                    
                    if saved_vocabulary:
                        self.whisper_transcriber.clear_custom_vocabulary()
                        self.whisper_transcriber.add_custom_vocabulary(saved_vocabulary)
                        print(f"[INFO] 保存されたカスタム語彙を読み込みました: {len(saved_vocabulary)}個")
                    else:
                        print(f"[DEBUG] 保存されたカスタム語彙が見つかりません")
                else:
                    print(f"[DEBUG] 保存されたカスタム語彙が見つかりません")
            except Exception as e:
                print(f"[ERROR] カスタム語彙の読み込みに失敗: {e}")
                import traceback
                traceback.print_exc()
    
    def _save_vocabulary(self):
        """カスタム語彙を設定に保存する"""
        if self.whisper_transcriber:
            try:
                vocabulary = self.whisper_transcriber.get_custom_vocabulary()
                print(f"[DEBUG] 保存するカスタム語彙: {vocabulary}")
                print(f"[DEBUG] 語彙の型: {type(vocabulary)}")
                print(f"[DEBUG] 語彙の長さ: {len(vocabulary)}")
                
                # JSON形式で保存
                vocabulary_json = json.dumps(vocabulary, ensure_ascii=False)
                self.settings.setValue("custom_vocabulary", vocabulary_json)
                self.settings.sync()
                print(f"[INFO] カスタム語彙を保存しました: {len(vocabulary)}個")
                
                # 保存確認
                saved_vocabulary_json = self.settings.value("custom_vocabulary", "")
                if saved_vocabulary_json:
                    saved_vocabulary = json.loads(saved_vocabulary_json)
                    print(f"[DEBUG] 保存確認 - 読み込まれた語彙: {saved_vocabulary}")
                else:
                    print(f"[DEBUG] 保存確認 - 語彙が保存されていません")
                
            except Exception as e:
                print(f"[ERROR] カスタム語彙の保存に失敗: {e}")
                import traceback
                traceback.print_exc()
    
    def _load_saved_system_instructions(self):
        """保存されたシステム指示を読み込む"""
        if self.whisper_transcriber:
            try:
                print(f"[DEBUG] システム指示の読み込み開始")
                saved_instructions_json = self.settings.value("system_instructions", "")
                if saved_instructions_json:
                    saved_instructions = json.loads(saved_instructions_json)
                    print(f"[DEBUG] 設定から読み込まれた指示: {saved_instructions}")
                    print(f"[DEBUG] 指示の型: {type(saved_instructions)}")
                    
                    if saved_instructions:
                        self.whisper_transcriber.clear_system_instructions()
                        self.whisper_transcriber.add_system_instruction(saved_instructions)
                        print(f"[INFO] 保存されたシステム指示を読み込みました: {len(saved_instructions)}個")
                    else:
                        print(f"[DEBUG] 保存されたシステム指示が見つかりません")
                else:
                    print(f"[DEBUG] 保存されたシステム指示が見つかりません")
            except Exception as e:
                print(f"[ERROR] システム指示の読み込みに失敗: {e}")
                import traceback
                traceback.print_exc()
    
    def _save_system_instructions(self):
        """システム指示を設定に保存する"""
        if self.whisper_transcriber:
            try:
                instructions = self.whisper_transcriber.get_system_instructions()
                print(f"[DEBUG] 保存するシステム指示: {instructions}")
                print(f"[DEBUG] 指示の型: {type(instructions)}")
                print(f"[DEBUG] 指示の長さ: {len(instructions)}")
                
                # JSON形式で保存
                instructions_json = json.dumps(instructions, ensure_ascii=False)
                self.settings.setValue("system_instructions", instructions_json)
                self.settings.sync()
                print(f"[INFO] システム指示を保存しました: {len(instructions)}個")
                
                # 保存確認
                saved_instructions_json = self.settings.value("system_instructions", "")
                if saved_instructions_json:
                    saved_instructions = json.loads(saved_instructions_json)
                    print(f"[DEBUG] 保存確認 - 読み込まれた指示: {saved_instructions}")
                else:
                    print(f"[DEBUG] 保存確認 - 指示が保存されていません")
                
            except Exception as e:
                print(f"[ERROR] システム指示の保存に失敗: {e}")
                import traceback
                traceback.print_exc()

    def toggle_native_api_option(self):
        """
        ネイティブAPI版フローティングウィンドウのオン/オフを切り替える
        
        設定を保存し、アプリケーションの再起動が必要であることを通知します
        """
        use_native_api = self.sender().isChecked()
        self.settings.setValue("use_native_floating_api", use_native_api)
        
        if use_native_api:
            # ネイティブAPIが利用可能かチェック
            if hasattr(self.floating_indicator, 'is_native_api_available') and self.floating_indicator.is_native_api_available():
                self.status_bar.showMessage("ネイティブAPI版フローティングウィンドウを有効にしました。変更を適用するにはアプリケーションを再起動してください。", 5000)
            else:
                self.status_bar.showMessage("ネイティブAPIが利用できません。pyobjcパッケージをインストールしてください。", 5000)
                # チェックを元に戻す
                self.sender().setChecked(False)
                self.settings.setValue("use_native_floating_api", False)
        else:
            self.status_bar.showMessage("PyQt6版フローティングウィンドウを使用します。変更を適用するにはアプリケーションを再起動してください。", 5000)

    def toggle_force_native_api_option(self):
        """
        ネイティブAPI版フローティングウィンドウのオン/オフを切り替える
        
        設定を保存し、アプリケーションの再起動が必要であることを通知します
        """
        force_native_api = self.sender().isChecked()
        self.settings.setValue("force_native_api_debug", force_native_api)
        if force_native_api:
            self.status_bar.showMessage("ネイティブAPI版フローティングウィンドウを強制的に有効にしました。変更を適用するにはアプリケーションを再起動してください。", 5000)
        else:
            self.status_bar.showMessage("ネイティブAPI版フローティングウィンドウを無効にしました。", 2000)
