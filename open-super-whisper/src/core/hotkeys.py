"""
macOS用グローバルホットキー管理モジュール（pyobjc + Quartz版, 安全な1回生成型）

アプリケーション全体で使用するグローバルホットキーの登録・管理機能を提供します。
PyQt6アプリと併用可能で、バックグラウンドでもホットキーが反応します。
"""

import sys

from typing import Callable, Dict
from PyQt6.QtCore import QObject
import threading
import sys
import time

from AppKit import NSApplication
from Quartz import (
    CGEventTapCreate, kCGHIDEventTap, kCGHeadInsertEventTap,
    kCGEventKeyDown, CGEventTapEnable, CGEventTapIsEnabled,
    kCGEventFlagMaskShift, kCGEventFlagMaskControl, kCGEventFlagMaskAlternate, kCGEventFlagMaskCommand,
    CGEventMaskBit, CFRunLoopAddSource, CFRunLoopGetCurrent,
    CFMachPortCreateRunLoopSource, CFRunLoopRunInMode, kCFRunLoopDefaultMode,
    CGEventGetFlags, CGEventGetIntegerValueField, kCGKeyboardEventKeycode
)
import Quartz
import time

# macOSのキーコードと修飾キーのマッピング
KEY_MAP = {
    'a': 0, 's': 1, 'd': 2, 'f': 3, 'h': 4, 'g': 5, 'z': 6, 'x': 7, 'c': 8, 'v': 9,
    'b': 11, 'q': 12, 'w': 13, 'e': 14, 'r': 15, 'y': 16, 't': 17, '1': 18, '2': 19, '3': 20, '4': 21, '6': 22, '5': 23,
    '=': 24, '9': 25, '7': 26, '-': 27, '8': 28, '0': 29, ']': 30, 'o': 31, 'u': 32, '[': 33, 'i': 34, 'p': 35, 'l': 37,
    'j': 38, '\\': 42, 'k': 40, ';': 41, ',': 43, '/': 44, 'n': 45, 'm': 46, '.': 47, ' ': 49
}
MODIFIER_MAP = {
    'shift': 2,
    'ctrl': 1,
    'control': 1,
    'alt': 4,
    'option': 4,
    'cmd': 8,
    'command': 8,
}

def parse_hotkey(hotkey_str):
    """
    例: 'ctrl+shift+r' → (keycode, modifier_mask)
    """
    parts = hotkey_str.lower().split('+')
    key = parts[-1]
    mods = parts[:-1]
    keycode = KEY_MAP.get(key)
    if keycode is None:
        raise ValueError(f"未対応キー: {key}")
    mask = 0
    for m in mods:
        mask |= MODIFIER_MAP.get(m, 0)
    return keycode, mask

class HotkeyManager(QObject):
    """
    グローバルホットキーの登録と管理を行うクラス（pyobjc + Quartz版, 安全な1回生成型）
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hotkeys: Dict[tuple, Callable[[], None]] = {}
        self._listener_thread = None
        self._stop_event = threading.Event()
        self._event_tap = None
        self._listener_lock = threading.Lock()
        # 重複実行防止のための変数
        self._last_executed_hotkey = None
        self._last_execution_time = 0
        self._debounce_time = 0.5  # 0.5秒間の重複実行を防ぐ
        self._start_listener()

    def print_registered_hotkeys(self):
        pass  # デバッグログを無効化

    def register_hotkey(self, hotkey_str: str, callback: Callable[[], None]) -> bool:
        """
        ホットキーとコールバックを登録する
        """
        try:
            keycode, mask = parse_hotkey(hotkey_str)
            self.hotkeys[(keycode, mask)] = callback
            print(f"[HotkeyManager] ホットキー登録: {hotkey_str}")
            return True
        except Exception as e:
            print(f"[HotkeyManager] register_hotkey失敗: {e}")
            return False

    def unregister_hotkey(self, hotkey_str: str) -> bool:
        try:
            keycode, mask = parse_hotkey(hotkey_str)
            if (keycode, mask) in self.hotkeys:
                del self.hotkeys[(keycode, mask)]
                print(f"[HotkeyManager] ホットキー解除: {hotkey_str}")
                return True
            print(f"[HotkeyManager] ホットキー解除失敗: {hotkey_str} (未登録)")
            return False
        except Exception as e:
            print(f"[HotkeyManager] unregister_hotkey失敗: {e}")
            return False

    def clear_all_hotkeys(self) -> bool:
        self.hotkeys.clear()
        print("[HotkeyManager] すべてのホットキー解除")
        return True

    def _start_listener(self):
        with self._listener_lock:
            if self._listener_thread is not None and self._listener_thread.is_alive():
                return
            self._stop_event.clear()
            self._listener_thread = threading.Thread(target=self._event_loop, daemon=True)
            self._listener_thread.start()

    def _stop_listener(self):
        with self._listener_lock:
            if self._listener_thread is not None and self._listener_thread.is_alive():
                self._stop_event.set()
                self._listener_thread.join(timeout=1.0)
                self._listener_thread = None
            if self._event_tap:
                try:
                    CGEventTapEnable(self._event_tap, False)
                except Exception:
                    pass
                self._event_tap = None

    def _event_loop(self):
        def callback(proxy, type_, event, refcon):
            if type_ == kCGEventKeyDown:
                keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
                flags = CGEventGetFlags(event)
                flags16 = flags & 0xffff
                mod_part = flags16 & 0x00ff
                for (kc, mask), cb in list(self.hotkeys.items()):
                    if keycode == kc and mod_part == mask:
                        # 重複実行防止チェック
                        current_time = time.time()
                        hotkey_id = (kc, mask)
                        
                        # 同じホットキーが短時間で複数回実行されるのを防ぐ
                        if (self._last_executed_hotkey == hotkey_id and 
                            current_time - self._last_execution_time < self._debounce_time):
                            print(f"[HotkeyManager] 重複実行を防止: {hotkey_id}")
                            return event
                        
                        # 実行時刻を記録
                        self._last_executed_hotkey = hotkey_id
                        self._last_execution_time = current_time
                        
                        print(f"[HotkeyManager] ホットキー実行: {hotkey_id}")
                        cb()
            return event
        mask = CGEventMaskBit(kCGEventKeyDown)
        self._event_tap = CGEventTapCreate(
            kCGHIDEventTap,
            kCGHeadInsertEventTap,
            0,
            mask,
            callback,
            None
        )
        if not self._event_tap:
            print("[HotkeyManager] イベントタップ作成失敗")
            return
        runLoopSource = CFMachPortCreateRunLoopSource(None, self._event_tap, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), runLoopSource, kCFRunLoopDefaultMode)
        CGEventTapEnable(self._event_tap, True)
        while not self._stop_event.is_set():
            CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.1, False)

    def stop(self):
        self._stop_listener()
        print("[HotkeyManager] リスナー停止")

    def stop_listener(self):
        """
        グローバルホットキーリスナーを停止するpublicメソッド
        """
        self._stop_listener()

    @staticmethod
    def is_valid_hotkey(hotkey_str: str) -> bool:
        try:
            keycode, mask = parse_hotkey(hotkey_str)
            return keycode is not None
        except Exception:
            return False

    @staticmethod
    def contains_modifier(hotkey_str: str) -> bool:
        if not hotkey_str:
            return False
        hotkey_str = hotkey_str.lower()
        parts = hotkey_str.split('+')
        modifiers = ['ctrl', 'control', 'alt', 'option', 'shift', 'cmd', 'command']
        return any(part in modifiers for part in parts) 