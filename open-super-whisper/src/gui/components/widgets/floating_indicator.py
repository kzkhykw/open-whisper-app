import sys
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QCursor
from ...resources.styles import AppStyles
from ...resources.labels import AppLabels
from ...utils.resource_helper import getResourcePath

# pyobjcのインポート（オプション）
try:
    import objc
    from AppKit import NSPanel, NSWindow, NSApplication, NSRect
    from AppKit import NSWindowCollectionBehaviorCanJoinAllSpaces
    from AppKit import NSWindowCollectionBehaviorFullScreenAuxiliary
    from AppKit import NSView, NSColor, NSFont, NSButton
    from AppKit import NSMakeRect, NSMakeSize, NSScreen
    from AppKit import NSTextField # 追加
    NATIVE_API_AVAILABLE = True
except ImportError:
    NATIVE_API_AVAILABLE = False
    print("[INFO] pyobjc not available, using PyQt6 only")

class FloatingIndicator(QWidget):
    """
    スクリーン中央下固定型フローティングウィンドウ
    
    録音中にスクリーンの中央下に固定表示され、
    録音状態、録音時間、クイックアクションを提供します。
    
    ネイティブAPI対応版も含まれ、他アプリ（全画面アプリ含む）でも表示可能です。
    """
    
    # カスタムシグナル
    stop_recording_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    
    def __init__(self, parent=None, use_native_api=False):
        super().__init__(parent)
        
        # ネイティブAPI使用フラグ
        self.use_native_api = use_native_api and NATIVE_API_AVAILABLE
        
        if self.use_native_api:
            self.init_native_window()
        else:
            self.init_pyqt_window()
        
        # 録音時間
        self.recording_start_time = None
        self.recording_time = 0
        
        # 録音時間更新タイマー
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_recording_time)
        self.time_timer.start(1000)  # 1秒間隔で更新
        
        # 初期状態は非表示
        self.hide()
    
    def init_pyqt_window(self):
        """PyQt6ベースのウィンドウ初期化"""
        # ウィンドウ設定（より強力な設定）
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |  # 枠なし
            Qt.WindowType.Tool |                 # ツールウィンドウ
            Qt.WindowType.WindowStaysOnTopHint | # 常に最前面
            Qt.WindowType.WindowDoesNotAcceptFocus  # フォーカスを受け取らない
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # アクティブ化せずに表示
        
        # サイズ設定
        self.setFixedSize(200, 80)
        
        # UI初期化
        self.init_ui()
    
    def init_native_window(self):
        """ネイティブAPIベースのウィンドウ初期化"""
        try:
            # NSApplicationを確実に初期化
            from AppKit import NSApplication
            app = NSApplication.sharedApplication()
            
            # NSPanelを作成
            self.native_panel = NSPanel.alloc().init()
            
            # 最上位レベルに設定（全画面アプリでも表示）
            # macOS 15.5での推奨レベル設定
            try:
                from AppKit import NSFloatingWindowLevel, NSPopUpMenuWindowLevel
                # フローティングウィンドウレベルを使用
                self.native_panel.setLevel_(NSFloatingWindowLevel)
                print(f"[DEBUG] NSFloatingWindowLevel（{NSFloatingWindowLevel}）を設定しました")
            except:
                try:
                    # 代替としてポップアップメニューレベル
                    self.native_panel.setLevel_(NSPopUpMenuWindowLevel)
                    print(f"[DEBUG] NSPopUpMenuWindowLevel（{NSPopUpMenuWindowLevel}）を設定しました")
                except:
                    # 最後の手段として高レベル
                    self.native_panel.setLevel_(3)  # NSFloatingWindowLevel = 3
                    print("[DEBUG] フローティングレベル（3）を設定しました")
            
            # 全画面アプリでも表示されるように設定
            # macOS 15.5での正しい設定
            self.native_panel.setCollectionBehavior_(
                NSWindowCollectionBehaviorCanJoinAllSpaces |  # すべてのスペースに表示
                NSWindowCollectionBehaviorFullScreenAuxiliary |  # 全画面アプリの補助ウィンドウ
                NSWindowCollectionBehaviorStationary |  # 固定位置
                NSWindowCollectionBehaviorIgnoresCycle  # Mission Controlで無視
            )
            
            # 全画面アプリのスペースでも表示されるように追加設定
            self.native_panel.setSharingType_(1)  # NSWindowSharingNone = 0, NSWindowSharingReadOnly = 1, NSWindowSharingReadWrite = 2
            
            # すべてのスペースで表示されるように追加設定
            try:
                # ウィンドウをすべてのスペースに表示
                self.native_panel.setCollectionBehavior_(
                    NSWindowCollectionBehaviorCanJoinAllSpaces |
                    NSWindowCollectionBehaviorFullScreenAuxiliary |
                    NSWindowCollectionBehaviorStationary |
                    NSWindowCollectionBehaviorIgnoresCycle
                )
                
                # ウィンドウレベルを再設定して確実に表示
                try:
                    from AppKit import NSFloatingWindowLevel
                    self.native_panel.setLevel_(NSFloatingWindowLevel)
                except:
                    self.native_panel.setLevel_(3)  # NSFloatingWindowLevel = 3
                
                print("[DEBUG] 全スペース表示設定完了")
                
            except Exception as e:
                print(f"[DEBUG] 全スペース表示設定エラー: {e}")
            
            # 全画面アプリの上に表示するための追加設定
            self.native_panel.setIgnoresMouseEvents_(False)  # マウスイベントを有効化
            self.native_panel.setMovableByWindowBackground_(True)  # ドラッグ可能に設定
            
            # 強制的に最前面に表示する設定
            self.native_panel.setHidesOnDeactivate_(False)  # 非アクティブでも非表示にしない
            self.native_panel.setCanHide_(False)  # 非表示にできないようにする
            
            # 全画面アプリ切り替え時の再表示設定
            self.native_panel.setReleasedWhenClosed_(False)  # 閉じてもリリースしない
            self.native_panel.setDisplaysWhenScreenProfileChanges_(True)  # スクリーンプロファイル変更時に表示
            
            # macOS 15.5での追加設定
            self.native_panel.setAnimationBehavior_(2)  # NSWindowAnimationBehaviorNone
            self.native_panel.setWorksWhenModal_(True)  # モーダル時も動作
            
            # フレームレス設定
            self.native_panel.setStyleMask_(0)  # 枠なし
            
            # 背景色設定（より目立つ色）
            self.native_panel.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(
                0.2, 0.2, 0.2, 0.95  # より濃いグレー
            ))
            
            # 角丸設定
            self.native_panel.setOpaque_(False)
            self.native_panel.setHasShadow_(True)
            
            # サイズ設定
            self.native_panel.setFrame_display_(NSMakeRect(0, 0, 200, 80), False)
            
            # ネイティブUI初期化
            self.init_native_ui()
            
            # 全画面アプリ切り替え検知の設定
            try:
                from AppKit import NSNotificationCenter, NSApplication
                notification_center = NSNotificationCenter.defaultCenter()
                
                # アプリケーション切り替え通知を監視
                notification_center.addObserver_selector_name_object_(
                    self.native_panel,
                    "applicationDidBecomeActive:",
                    "NSApplicationDidBecomeActiveNotification",
                    None
                )
                
                # スペース切り替え通知を監視
                notification_center.addObserver_selector_name_object_(
                    self.native_panel,
                    "workspaceDidChange:",
                    "NSWorkspaceDidWakeNotification",
                    None
                )
                
                print("[DEBUG] 全画面アプリ・スペース切り替え検知を設定しました")
                
            except Exception as e:
                print(f"[DEBUG] 切り替え検知設定エラー: {e}")
            
            print("[INFO] ネイティブAPI版フローティングウィンドウを初期化しました")
            
        except Exception as e:
            print(f"[ERROR] ネイティブAPI初期化エラー: {e}")
            # フォールバック: PyQt6版を使用
            self.use_native_api = False
            self.init_pyqt_window()
    
    def init_native_ui(self):
        """ネイティブAPI版のUI初期化"""
        try:
            # コンテンツビュー
            content_view = self.native_panel.contentView()
            
            # 背景色を設定
            content_view.setWantsLayer_(True)
            content_view.layer().setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(
                0.157, 0.173, 0.204, 0.95  # rgba(40, 44, 52, 0.95)
            ).CGColor())
            
            # 録音状態ラベル（NSTextFieldを使用）
            self.native_status_label = NSTextField.alloc().init()
            self.native_status_label.setFrame_(NSMakeRect(10, 45, 180, 20))
            self.native_status_label.setStringValue_("⏸️ 待機中")
            self.native_status_label.setEditable_(False)
            self.native_status_label.setBordered_(False)
            self.native_status_label.setBackgroundColor_(NSColor.clearColor())
            self.native_status_label.setTextColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(0.8, 0.8, 0.8, 1.0))
            
            # 録音時間ラベル（NSTextFieldを使用）
            self.native_time_label = NSTextField.alloc().init()
            self.native_time_label.setFrame_(NSMakeRect(10, 25, 180, 20))
            self.native_time_label.setStringValue_("00:00")
            self.native_time_label.setEditable_(False)
            self.native_time_label.setBordered_(False)
            self.native_time_label.setBackgroundColor_(NSColor.clearColor())
            self.native_time_label.setTextColor_(NSColor.whiteColor())
            
            # 停止ボタン
            self.native_stop_button = NSButton.alloc().init()
            self.native_stop_button.setFrame_(NSMakeRect(10, 5, 60, 20))
            self.native_stop_button.setTitle_("停止")
            self.native_stop_button.setBezelStyle_(1)  # NSRoundedBezelStyle = 1
            
            # コンテンツビューに追加
            content_view.addSubview_(self.native_status_label)
            content_view.addSubview_(self.native_time_label)
            content_view.addSubview_(self.native_stop_button)
            
            print("[INFO] ネイティブUIを初期化しました")
            
        except Exception as e:
            print(f"[ERROR] ネイティブUI初期化エラー: {e}")
    
    def init_ui(self):
        """UIの初期化（PyQt6版）"""
        # メインレイアウト
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        
        # 背景フレーム
        self.background_frame = QFrame()
        self.background_frame.setObjectName("floatingBackground")
        self.background_frame.setStyleSheet(AppStyles.FLOATING_INDICATOR_STYLE)
        
        frame_layout = QVBoxLayout(self.background_frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        frame_layout.setSpacing(8)
        
        # 上部: 録音状態と時間
        top_layout = QHBoxLayout()
        
        # 録音状態インジケータ
        self.status_label = QLabel("⏸️ 待機中")
        self.status_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #cccccc;")
        
        # 録音時間
        self.time_label = QLabel("00:00")
        self.time_label.setFont(QFont("Arial", 10))
        self.time_label.setStyleSheet("color: #ffffff;")
        
        top_layout.addWidget(self.status_label)
        top_layout.addStretch()
        top_layout.addWidget(self.time_label)
        
        # 下部: ボタン
        button_layout = QHBoxLayout()
        
        # 停止ボタン
        self.stop_button = QPushButton("停止")
        self.stop_button.setFixedSize(60, 25)
        self.stop_button.setStyleSheet(AppStyles.FLOATING_STOP_BUTTON_STYLE)
        self.stop_button.clicked.connect(self.stop_recording_requested.emit)
        
        # 設定ボタン
        self.settings_button = QPushButton("⚙️")
        self.settings_button.setFixedSize(30, 25)
        self.settings_button.setStyleSheet(AppStyles.FLOATING_SETTINGS_BUTTON_STYLE)
        self.settings_button.clicked.connect(self.settings_requested.emit)
        
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        button_layout.addWidget(self.settings_button)
        
        # レイアウトを組み立て
        frame_layout.addLayout(top_layout)
        frame_layout.addLayout(button_layout)
        
        main_layout.addWidget(self.background_frame)
        self.setLayout(main_layout)
    
    def position_to_center_bottom(self):
        """スクリーンの中央下に配置"""
        if self.use_native_api:
            self.position_native_to_center_bottom()
        else:
            self.position_pyqt_to_center_bottom()
    
    def position_pyqt_to_center_bottom(self):
        """PyQt6版の中央下配置"""
        screen = QApplication.primaryScreen().geometry()
        window_width = self.width()
        window_height = self.height()
        
        # 中央下の位置を計算
        x = (screen.width() - window_width) // 2
        y = screen.height() - window_height - 50  # 下から50pxの位置
        
        self.move(x, y)
    
    def position_native_to_center_bottom(self):
        """ネイティブAPI版の中央下配置"""
        try:
            # メインスクリーンのサイズを取得
            main_screen = NSScreen.mainScreen()
            screen_frame = main_screen.frame()
            
            # ウィンドウサイズ
            window_width = 200
            window_height = 80
            
            # 中央下の位置を計算
            x = (screen_frame.size.width - window_width) / 2
            y = screen_frame.size.height - window_height - 50  # 下から50px
            
            # 位置を設定
            new_frame = NSMakeRect(x, y, window_width, window_height)
            self.native_panel.setFrame_display_(new_frame, True)
            
            print(f"[DEBUG] ネイティブウィンドウ位置: ({x}, {y})")
            
        except Exception as e:
            print(f"[ERROR] ネイティブ位置設定エラー: {e}")
    
    def start_recording(self):
        """録音開始"""
        self.recording_start_time = time.time()
        self.recording_time = 0
        
        if self.use_native_api:
            self.start_native_recording()
        else:
            self.start_pyqt_recording()
    
    def start_pyqt_recording(self):
        """PyQt6版の録音開始"""
        self.time_label.setText("00:00")
        self.status_label.setText("🔴 録音中")
        self.status_label.setStyleSheet("color: #ff4444;")
        
        # スクリーンの中央下に配置してから表示
        self.position_to_center_bottom()
        self.show()
    
    def start_native_recording(self):
        """ネイティブAPI版の録音開始"""
        try:
            # ネイティブUIの更新
            if hasattr(self, 'native_status_label'):
                # 録音状態を表示
                self.native_status_label.setStringValue_("🔴 録音中")
                self.native_status_label.setTextColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.27, 0.27, 1.0))
                self.native_status_label.setNeedsDisplay_(True)
            
            # スクリーンの中央下に配置
            self.position_to_center_bottom()
            
            # ウィンドウを表示（全画面アプリの上にも表示）
            self.native_panel.makeKeyAndOrderFront_(None)
            self.native_panel.orderFrontRegardless()  # 強制的に最前面に表示
            
            # 全画面アプリ切り替え時の再表示を確実にする
            try:
                # ウィンドウを全画面アプリのスペースにも表示
                self.native_panel.setCollectionBehavior_(
                    NSWindowCollectionBehaviorCanJoinAllSpaces |
                    NSWindowCollectionBehaviorFullScreenAuxiliary |
                    0x00000040  # NSWindowCollectionBehaviorTransient
                )
                
                # 再度表示を強制
                self.native_panel.orderFrontRegardless()
                self.native_panel.display()
                
                print("[DEBUG] 全画面アプリ対応ウィンドウ表示完了")
                
            except Exception as e:
                print(f"[DEBUG] 全画面アプリ対応エラー: {e}")
            
            # 強制的に表示を更新
            self.native_panel.display()
            print("[DEBUG] ウィンドウ表示完了")
            
            print("[INFO] ネイティブ録音開始")
            
        except Exception as e:
            print(f"[ERROR] ネイティブ録音開始エラー: {e}")
            # フォールバック: PyQt6版を使用
            self.use_native_api = False
            self.start_pyqt_recording()
    
    def stop_recording(self):
        """録音停止"""
        self.recording_start_time = None
        self.recording_time = 0
        
        if self.use_native_api:
            self.stop_native_recording()
        else:
            self.stop_pyqt_recording()
    
    def stop_pyqt_recording(self):
        """PyQt6版の録音停止"""
        self.time_label.setText("00:00")
        self.status_label.setText("⏸️ 待機中")
        self.status_label.setStyleSheet("color: #cccccc;")
        self.hide()
    
    def stop_native_recording(self):
        """ネイティブAPI版の録音停止"""
        try:
            # ネイティブUIの更新
            if hasattr(self, 'native_status_label'):
                # 待機状態に戻す
                self.native_status_label.setStringValue_("⏸️ 待機中")
                self.native_status_label.setTextColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(0.8, 0.8, 0.8, 1.0))
                self.native_status_label.setNeedsDisplay_(True)
            
            if hasattr(self, 'native_time_label'):
                # 時間をリセット
                self.native_time_label.setStringValue_("00:00")
                self.native_time_label.setNeedsDisplay_(True)
            
            # ウィンドウを非表示
            self.native_panel.orderOut_(None)
            
            print("[INFO] ネイティブ録音停止")
            
        except Exception as e:
            print(f"[ERROR] ネイティブ録音停止エラー: {e}")
            # フォールバック: PyQt6版を使用
            self.use_native_api = False
            self.stop_pyqt_recording()
    
    def update_recording_time(self):
        """録音時間を更新"""
        if self.recording_start_time is None:
            return
        
        # 経過時間を計算
        elapsed_time = int(time.time() - self.recording_start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        if self.use_native_api:
            self.update_native_recording_time(time_str)
        else:
            self.time_label.setText(time_str)
    
    def update_native_recording_time(self, time_str):
        """ネイティブAPI版の録音時間更新"""
        try:
            if hasattr(self, 'native_time_label'):
                # ネイティブラベルの更新
                self.native_time_label.setStringValue_(time_str)
                print(f"[DEBUG] ネイティブ時間更新: {time_str}")
        except Exception as e:
            print(f"[ERROR] ネイティブ時間更新エラー: {e}")
    
    def mousePressEvent(self, event):
        """マウスドラッグ開始（PyQt6版のみ）"""
        if not self.use_native_api and event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """マウスドラッグ中（PyQt6版のみ）"""
        if not self.use_native_api and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        if self.use_native_api and hasattr(self, 'native_panel'):
            try:
                self.native_panel.close()
                self.native_panel = None
                print("[INFO] ネイティブウィンドウをクリーンアップしました")
            except Exception as e:
                print(f"[ERROR] ネイティブクリーンアップエラー: {e}")
    
    def is_native_api_available(self):
        """ネイティブAPIが利用可能かチェック"""
        return NATIVE_API_AVAILABLE 