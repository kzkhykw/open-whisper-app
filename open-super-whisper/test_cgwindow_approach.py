#!/usr/bin/env python3
"""
CGWindowを使用した直接的なアプローチでウィンドウ表示をテスト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from AppKit import NSWindow, NSMakeRect, NSColor, NSApplication, NSApp
    from Foundation import NSRect
    from Quartz import CGWindowLevelForKey, kCGMaximumWindowLevelKey, kCGMainMenuWindowLevelKey
    
    print("=== CGWindow直接アプローチテスト ===")
    
    # NSApplicationを初期化
    app = NSApplication.sharedApplication()
    
    # 通常のNSWindowを作成
    test_window = NSWindow.alloc().init()
    test_window.setFrame_display_(NSMakeRect(200, 200, 300, 200), False)
    
    # CGWindowレベルを直接設定
    try:
        # 最大レベルを取得
        max_level = CGWindowLevelForKey(kCGMaximumWindowLevelKey)
        print(f"最大ウィンドウレベル: {max_level}")
        
        # ウィンドウレベルを設定
        test_window.setLevel_(max_level)
        print("✅ CGWindow最大レベルを設定しました")
        
    except Exception as e:
        print(f"CGWindowレベル設定エラー: {e}")
        # 代替として非常に高いレベル
        test_window.setLevel_(1000000)
        print("✅ 高レベル（1000000）を設定しました")
    
    # Collection Behaviorを設定
    test_window.setCollectionBehavior_(0x00000002 | 0x00000020)  # CanJoinAllSpaces | FullScreenAuxiliary
    
    # 背景色設定（目立つ赤色）
    test_window.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.0, 0.0, 0.9))
    test_window.setOpaque_(False)
    test_window.setHasShadow_(True)
    
    # タイトル設定
    test_window.setTitle_("CGWindowテスト")
    
    # 強制表示設定
    test_window.setHidesOnDeactivate_(False)
    test_window.setCanHide_(False)
    
    print("CGWindowアプローチでウィンドウを表示します...")
    print("この赤いウィンドウが全画面アプリの上に表示されるかテストしてください")
    
    # ウィンドウを表示
    test_window.makeKeyAndOrderFront_(None)
    test_window.orderFrontRegardless()
    test_window.display()
    
    print("✅ CGWindowアプローチでウィンドウが表示されました")
    print("全画面アプリを開いて、この赤いウィンドウが上に表示されるか確認してください")
    print("Enterキーを押すとウィンドウを閉じます...")
    
    input()
    test_window.close()
    
except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()

print("テスト完了") 