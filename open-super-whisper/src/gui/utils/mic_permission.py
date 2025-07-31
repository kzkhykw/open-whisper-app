import sys

if sys.platform == "darwin":
    try:
        from AVFoundation import AVCaptureDevice
    except ImportError:
        AVCaptureDevice = None

    def has_microphone_permission():
        if AVCaptureDevice is None:
            with open("/tmp/recorder_debug.log", "a") as logf:
                logf.write("mic permission: AVCaptureDevice is None\n")
            return False
        status = AVCaptureDevice.authorizationStatusForMediaType_("soun")
        with open("/tmp/recorder_debug.log", "a") as logf:
            logf.write(f"mic permission status: {status}\n")
        # "soun"はAudioのメディアタイプ
        # 0: NotDetermined, 1: Restricted, 2: Denied, 3: Authorized
        return status not in (1, 2)

    def request_microphone_permission():
        """
        マイク権限を明示的にリクエストする（macOS用）。
        """
        if AVCaptureDevice is None:
            with open("/tmp/recorder_debug.log", "a") as logf:
                logf.write("mic permission: AVCaptureDevice is None (request)\n")
            return False
        result = []
        def handler(granted):
            result.append(granted)
            with open("/tmp/recorder_debug.log", "a") as logf:
                logf.write(f"mic permission request result: {granted}\n")
        AVCaptureDevice.requestAccessForMediaType_completionHandler_("soun", handler)
        # macOSの仕様上、非同期なので即時には分からない
        return None
else:
    def has_microphone_permission():
        # 他OSは常にTrue（今後拡張可）
        return True
    def request_microphone_permission():
        return True 