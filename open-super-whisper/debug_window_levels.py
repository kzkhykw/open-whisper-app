#!/usr/bin/env python3
"""
ウィンドウレベルと表示の問題を詳細にデバッグ
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from AppKit import NSPanel, NSMakeRect, NSColor, NSApplication, NSApp
    from Foundation import NSRect
    
    print("=== ウィンドウレベルデバッグ ===")
    
    # NSApplicationを初期化
    app = NSApplication.sharedApplication()
    
    # 複数のウィンドウレベルをテスト
    test_levels = [
        ("Normal", 0),
        ("Floating", 3),
        ("TornOffMenu", 3),
        ("MainMenu", 24),
        ("ModalPanel", 8),
        ("PopUpMenu", 101),
        ("ScreenSaver", 1000),
        ("Maximum", 2147483647),
        ("High", 1000000),
        ("VeryHigh", 10000000)
    ]
    
    panels = []
    
    for name, level in test_levels:
        try:
            print(f"\n--- {name} (Level: {level}) ---")
            
            # パネルを作成
            panel = NSPanel.alloc().init()
            panel.setFrame_display_(NSMakeRect(100 + (len(panels) * 50), 100 + (len(panels) * 50), 200, 100), False)
            
            # レベルを設定
            panel.setLevel_(level)
            
            # 背景色設定（レベルごとに異なる色）
            colors = [
                (1.0, 0.0, 0.0, 0.8),  # 赤
                (0.0, 1.0, 0.0, 0.8),  # 緑
                (0.0, 0.0, 1.0, 0.8),  # 青
                (1.0, 1.0, 0.0, 0.8),  # 黄
                (1.0, 0.0, 1.0, 0.8),  # マゼンタ
                (0.0, 1.0, 1.0, 0.8),  # シアン
                (1.0, 0.5, 0.0, 0.8),  # オレンジ
                (0.5, 0.0, 1.0, 0.8),  # 紫
                (0.0, 0.5, 0.0, 0.8),  # 深緑
                (0.5, 0.5, 0.5, 0.8),  # グレー
            ]
            
            color = colors[len(panels) % len(colors)]
            panel.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(*color))
            panel.setOpaque_(False)
            panel.setHasShadow_(True)
            
            # フレームレス設定
            panel.setStyleMask_(0)
            
            # Collection Behaviorを設定
            panel.setCollectionBehavior_(0x00000002 | 0x00000020)  # CanJoinAllSpaces | FullScreenAuxiliary
            
            # 表示
            panel.makeKeyAndOrderFront_(None)
            panel.orderFrontRegardless()
            
            # 実際のレベルを確認
            actual_level = panel.level()
            print(f"設定レベル: {level}, 実際のレベル: {actual_level}")
            print(f"ウィンドウID: {panel.windowNumber()}")
            
            panels.append(panel)
            
        except Exception as e:
            print(f"エラー: {e}")
    
    print(f"\n=== {len(panels)}個のテストウィンドウを表示しました ===")
    print("どのウィンドウが表示されているか確認してください")
    print("全画面アプリを開いて、どのウィンドウが上に表示されるかテストしてください")
    print("Enterキーを押すとすべてのウィンドウを閉じます...")
    
    input()
    
    # すべてのウィンドウを閉じる
    for panel in panels:
        try:
            panel.close()
        except:
            pass
    
except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()

print("デバッグ完了") 