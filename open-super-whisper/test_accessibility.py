#!/usr/bin/env python3
"""
アクセシビリティ権限テストスクリプト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from AppKit import NSWorkspace, NSApplication, NSApp
    from Foundation import NSBundle
    
    print("=== アクセシビリティ権限テスト ===")
    
    # アプリケーション情報を取得
    app = NSApplication.sharedApplication()
    bundle = NSBundle.mainBundle()
    
    print(f"アプリケーション名: {bundle.infoDictionary().get('CFBundleName', 'Unknown')}")
    print(f"バンドルID: {bundle.bundleIdentifier()}")
    
    # アクセシビリティ権限の確認
    try:
        # システム権限の確認
        from AppKit import AXIsProcessTrusted
        is_trusted = AXIsProcessTrusted()
        print(f"アクセシビリティ権限: {'✅ 許可済み' if is_trusted else '❌ 未許可'}")
        
        if not is_trusted:
            print("\n⚠️  アクセシビリティ権限が必要です！")
            print("システム設定 → プライバシーとセキュリティ → アクセシビリティ")
            print("で「OpenSuperWhisper」を追加して権限を許可してください。")
        else:
            print("✅ 権限は正常に設定されています")
            
    except Exception as e:
        print(f"権限確認エラー: {e}")
    
    # ウィンドウレベルテスト
    try:
        from AppKit import NSPanel, NSMakeRect, NSColor
        from Foundation import NSRect
        
        print("\n=== ウィンドウレベルテスト ===")
        
        # テストパネルを作成
        test_panel = NSPanel.alloc().init()
        test_panel.setFrame_display_(NSMakeRect(100, 100, 200, 100), False)
        test_panel.setLevel_(2147483647)  # 最大レベル
        test_panel.setCollectionBehavior_(0x00000002 | 0x00000020)  # CanJoinAllSpaces | FullScreenAuxiliary
        
        # 背景色設定
        test_panel.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.0, 0.0, 0.8))
        test_panel.setOpaque_(False)
        
        print("テストウィンドウを表示します...")
        test_panel.makeKeyAndOrderFront_(None)
        test_panel.orderFrontRegardless()
        
        print("✅ テストウィンドウが表示されました")
        print("全画面アプリを開いて、この赤いウィンドウが上に表示されるかテストしてください")
        
        input("Enterキーを押すとテストウィンドウを閉じます...")
        test_panel.close()
        
    except Exception as e:
        print(f"ウィンドウテストエラー: {e}")
    
except ImportError as e:
    print(f"AppKitのインポートエラー: {e}")
    print("pyobjc-framework-Cocoaがインストールされているか確認してください")
except Exception as e:
    print(f"予期しないエラー: {e}")

print("\nテスト完了") 