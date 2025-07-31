#!/usr/bin/env python3
"""
全画面アプリでのウィンドウ表示テスト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from AppKit import NSPanel, NSMakeRect, NSColor, NSWindowCollectionBehaviorCanJoinAllSpaces, NSWindowCollectionBehaviorFullScreenAuxiliary, NSWindowCollectionBehaviorFullScreenPrimary
    from Foundation import NSRect
    
    print("=== 全画面アプリウィンドウテスト ===")
    
    # テストパネルを作成
    test_panel = NSPanel.alloc().init()
    test_panel.setFrame_display_(NSMakeRect(100, 100, 300, 150), False)
    
    # ウィンドウレベルを設定
    try:
        from Quartz import kCGMaximumWindowLevelKey
        test_panel.setLevel_(kCGMaximumWindowLevelKey)
        print("✅ CGWindow最大レベルを設定")
    except ImportError:
        test_panel.setLevel_(1000000)
        print("✅ 高レベル（1000000）を設定")
    
    # Collection Behaviorを設定
    test_panel.setCollectionBehavior_(
        NSWindowCollectionBehaviorCanJoinAllSpaces |
        NSWindowCollectionBehaviorFullScreenAuxiliary |
        NSWindowCollectionBehaviorFullScreenPrimary |
        0x00000040  # NSWindowCollectionBehaviorTransient
    )
    
    # 背景色設定（目立つ赤色）
    test_panel.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.0, 0.0, 0.9))
    test_panel.setOpaque_(False)
    test_panel.setHasShadow_(True)
    
    # フレームレス設定
    test_panel.setStyleMask_(0)
    
    # 強制表示設定
    test_panel.setHidesOnDeactivate_(False)
    test_panel.setCanHide_(False)
    
    print("テストウィンドウを表示します...")
    print("全画面アプリ（YouTube、Netflix等）を開いて、この赤いウィンドウが上に表示されるかテストしてください")
    
    # ウィンドウを表示
    test_panel.makeKeyAndOrderFront_(None)
    test_panel.orderFrontRegardless()
    test_panel.display()
    
    print("✅ テストウィンドウが表示されました")
    print("全画面アプリを開いて、この赤いウィンドウが上に表示されるか確認してください")
    print("Enterキーを押すとテストウィンドウを閉じます...")
    
    input()
    test_panel.close()
    
except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()

print("テスト完了") 