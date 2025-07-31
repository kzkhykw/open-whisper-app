import os
import numpy as np
import sounddevice as sd
import soundfile as sf
import threading
import time
from datetime import datetime


class AudioRecorder:
    """
    音声録音機能を提供するクラス
    
    リアルタイムで音声を録音し、WAVファイルとして保存する機能を提供します。
    録音はバックグラウンドスレッドで実行され、メインスレッドをブロックしません。
    """
    
    def __init__(self, sample_rate=16000, channels=1, device=None):
        """
        音声録音クラスの初期化
        
        Parameters
        ----------
        sample_rate : int, optional
            サンプリングレート（デフォルト: 16000Hz）
        channels : int, optional
            チャンネル数（デフォルト: 1（モノラル））
        device : int, optional
            使用する録音デバイスのID（デフォルト: None（デフォルトデバイス））
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device
        self.recording = False
        self.audio_data = []
        self._record_thread = None
        
        # 一時ディレクトリの設定
        self.temp_dir = os.path.join(os.path.expanduser("~"), ".open_super_whisper", "temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # パフォーマンス最適化用のキャッシュ
        self._last_recording_time = 0
        self._recording_start_time = 0
    
    def start_recording(self):
        """
        音声録音を開始する
        
        Returns
        -------
        bool
            録音開始が成功したかどうか
        """
        if self.recording:
            return False
            
        self.recording = True
        self.audio_data = []
        self._recording_start_time = time.time()
        
        # 録音スレッドを開始
        self._record_thread = threading.Thread(target=self._record)
        self._record_thread.daemon = True
        self._record_thread.start()
        
        print(f"[INFO] Recording started at {datetime.now()}")
        return True
    
    def stop_recording(self):
        """
        音声録音を停止し、保存したファイル名を返す
        
        Returns
        -------
        str or None
            保存された音声ファイルパス、失敗時はNone
        """
        if not self.recording:
            return None
            
        self.recording = False
        
        # 録音スレッドの終了を待機
        if self._record_thread and self._record_thread.is_alive():
            self._record_thread.join()
        
        # 録音時間を記録
        self._last_recording_time = time.time() - self._recording_start_time
        
        with open("/tmp/recorder_debug.log", "a") as logf:
            logf.write(f"[STOP_RECORDING] {datetime.now()}, Duration: {self._last_recording_time:.2f}s\n")
        
        # 現在のタイムスタンプに基づいたファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.temp_dir, f"recording_{timestamp}.wav")
        
        # 録音した音声を保存
        if self.audio_data:
            audio_data = np.concatenate(self.audio_data, axis=0)
            
            # 音声データの情報をログに記録
            duration = len(audio_data) / self.sample_rate
            max_amplitude = np.max(np.abs(audio_data))
            mean_amplitude = np.mean(np.abs(audio_data))
            
            print(f"[AUDIO INFO] Duration: {duration:.2f}s, Max amplitude: {max_amplitude:.4f}, Mean amplitude: {mean_amplitude:.4f}")
            
            # 音声レベルが低すぎる場合は警告
            if max_amplitude < 0.01:
                print(f"[WARNING] Audio level is very low (max: {max_amplitude:.4f}). Microphone might not be working properly.")
            
            # 最適化された音声保存
            try:
                # 音声データを16bit整数に変換して保存時間を短縮
                audio_data_int16 = (audio_data * 32767).astype(np.int16)
                sf.write(filename, audio_data_int16, self.sample_rate, subtype='PCM_16')
                
                with open("/tmp/recorder_debug.log", "a") as logf:
                    logf.write(f"Saved audio file: {filename}\n")
                    logf.write(f"Audio duration: {duration:.2f}s, max_amp: {max_amplitude:.4f}, mean_amp: {mean_amplitude:.4f}\n")
                
                print(f"[INFO] Audio saved successfully: {filename}")
                return filename
                
            except Exception as e:
                print(f"[ERROR] Failed to save audio file: {e}")
                # フォールバック: 通常のfloat形式で保存
                try:
                    sf.write(filename, audio_data, self.sample_rate)
                    print(f"[INFO] Audio saved with fallback method: {filename}")
                    return filename
                except Exception as fallback_error:
                    print(f"[ERROR] Fallback save also failed: {fallback_error}")
                    return None
        else:
            print(f"[ERROR] No audio data recorded. Audio data length: {len(self.audio_data)}")
            return None
    
    def _record(self):
        """
        音声データを録音する内部メソッド
        """
        try:
            # 録音コールバック関数
            def callback(indata, frames, time, status):
                if status:
                    print(f"[WARNING] Audio recording status: {status}")
                if self.recording:
                    # 音声データをコピーして保存
                    audio_chunk = indata.copy()
                    self.audio_data.append(audio_chunk)
            
            # 録音ストリームを開始
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                device=self.device,
                callback=callback,
                dtype=np.float32
            ):
                print(f"[INFO] Recording stream started")
                while self.recording:
                    time.sleep(0.1)  # 100ms間隔でチェック
                    
        except Exception as e:
            print(f"[ERROR] Recording error: {e}")
            self.recording = False
    
    def is_recording(self):
        """
        現在録音中かどうかを返す
        
        Returns
        -------
        bool
            録音中かどうか
        """
        return self.recording
    
    def get_last_recording_time(self):
        """
        最後の録音時間を取得する
        
        Returns
        -------
        float
            最後の録音にかかった時間（秒）
        """
        return self._last_recording_time
    
    def get_recording_duration(self):
        """
        現在の録音時間を取得する
        
        Returns
        -------
        float
            現在の録音時間（秒）
        """
        if self.recording:
            return time.time() - self._recording_start_time
        return 0.0
