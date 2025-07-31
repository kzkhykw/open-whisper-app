"""
メニューバーインジケーター
全画面アプリでも常に表示される
"""

from PyQt6.QtCore import QTimer, QTime, pyqtSignal
from PyQt6.QtWidgets import QWidget
import platform

if platform.system() == "Darwin":
    try:
        from AppKit import NSStatusBar, NSStatusBarButton, NSMenu, NSMenuItem, NSApplication
        from Foundation import NSObject
        import objc
        MACOS_AVAILABLE = True
    except ImportError:
        MACOS_AVAILABLE = False
else:
    MACOS_AVAILABLE = False


class MenuBarIndicator(QWidget):
    """メニューバーに表示される録音インジケーター"""
    
    stop_recording_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_recording = False
        self.recording_time = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_recording_time)
        
        # macOSメニューバー設定
        if MACOS_AVAILABLE:
            self.init_menubar()
        else:
            print("[WARNING] メニューバーインジケーターはmacOSでのみ利用可能です")
    
    def init_menubar(self):
        """macOSメニューバーの初期化"""
        try:
            # ステータスバーアイテムを作成
            self.status_bar = NSStatusBar.systemStatusBar()
            self.status_item = self.status_bar.statusItemWithLength_(-1)  # NSVariableStatusItemLength
            
            # ボタンを設定
            self.status_button = self.status_item.button()
            self.update_status_text("⏸️")
            
            # メニューを作成
            self.menu = NSMenu.alloc().init()
            
            # メニューアイテムを追加
            self.recording_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "待機中", None, ""
            )
            self.recording_item.setEnabled_(False)
            self.menu.addItem_(self.recording_item)
            
            self.menu.addItem_(NSMenuItem.separatorItem())
            
            # 停止アイテム
            self.stop_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "録音停止", "stopRecording:", ""
            )
            self.stop_item.setEnabled_(False)
            self.menu.addItem_(self.stop_item)
            
            # メニューを設定
            self.status_item.setMenu_(self.menu)
            
            print("[INFO] メニューバーインジケーターを初期化しました")
            
        except Exception as e:
            print(f"[ERROR] メニューバー初期化エラー: {e}")
    
    def update_status_text(self, text):
        """ステータステキストを更新"""
        if MACOS_AVAILABLE and hasattr(self, 'status_button'):
            self.status_button.setTitle_(text)
    
    def start_recording(self):
        """録音開始"""
        self.is_recording = True
        self.recording_time = 0
        self.timer.start(1000)  # 1秒ごとに更新
        
        if MACOS_AVAILABLE:
            self.update_status_text("🔴")
            self.recording_item.setTitle_("🔴 録音中")
            self.stop_item.setEnabled_(True)
        
        print("[INFO] メニューバー録音開始")
    
    def stop_recording(self):
        """録音停止"""
        self.is_recording = False
        self.timer.stop()
        self.recording_time = 0
        
        if MACOS_AVAILABLE:
            self.update_status_text("⏸️")
            self.recording_item.setTitle_("⏸️ 待機中")
            self.stop_item.setEnabled_(False)
        
        print("[INFO] メニューバー録音停止")
    
    def update_recording_time(self):
        """録音時間を更新"""
        if self.is_recording:
            self.recording_time += 1
            time_str = QTime(0, 0).addSecs(self.recording_time).toString("mm:ss")
            
            if MACOS_AVAILABLE:
                self.recording_item.setTitle_(f"🔴 録音中 - {time_str}")
    
    def cleanup(self):
        """クリーンアップ"""
        if MACOS_AVAILABLE and hasattr(self, 'status_bar'):
            try:
                self.status_bar.removeStatusItem_(self.status_item)
            except:
                pass 