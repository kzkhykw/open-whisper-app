#!/usr/bin/env python3
"""
基本的なNSWindowを使用したウィンドウ表示テスト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from AppKit import NSWindow, NSMakeRect, NSColor, NSApplication, NSApp, NSWindowCollectionBehaviorCanJoinAllSpaces, NSWindowCollectionBehaviorFullScreenAuxiliary
    from Foundation import NSRect
    
    print("=== 基本的なウィンドウ表示テスト ===")
    
    # NSApplicationを初期化
    app = NSApplication.sharedApplication()
    
    # 通常のNSWindowを作成
    test_window = NSWindow.alloc().init()
    test_window.setFrame_display_(NSMakeRect(200, 200, 300, 200), False)
    
    # ウィンドウレベルを設定
    test_window.setLevel_(1000)  # ScreenSaver level
    
    # Collection Behaviorを設定
    test_window.setCollectionBehavior_(
        NSWindowCollectionBehaviorCanJoinAllSpaces |
        NSWindowCollectionBehaviorFullScreenAuxiliary
    )
    
    # 背景色設定（目立つ赤色）
    test_window.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.0, 0.0, 0.9))
    test_window.setOpaque_(False)
    test_window.setHasShadow_(True)
    
    # タイトル設定
    test_window.setTitle_("テストウィンドウ")
    
    print("基本的なウィンドウを表示します...")
    print("この赤いウィンドウが表示されるか確認してください")
    
    # ウィンドウを表示
    test_window.makeKeyAndOrderFront_(None)
    test_window.orderFrontRegardless()
    
    print("✅ 基本的なウィンドウが表示されました")
    print("このウィンドウが見えますか？")
    print("Enterキーを押すとウィンドウを閉じます...")
    
    input()
    test_window.close()
    
except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()

print("テスト完了") 