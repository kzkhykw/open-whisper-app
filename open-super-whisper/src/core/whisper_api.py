import os
import json
import torch
from pathlib import Path
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import soundfile as sf
import numpy as np
import time


class WhisperTranscriber:
    """
    Hugging Face Transformersを使用したローカルWhisper文字起こし処理を行うクラス
    
    ローカルでWhisperモデルを実行し、カスタム語彙やシステム指示を
    活用して精度を向上させる機能を提供します。
    """
    
    # 利用可能なモデルのリスト
    AVAILABLE_MODELS = [
        {"id": "openai/whisper-tiny", "name": "Whisper Tiny", "description": "Fastest model, 39M parameters"},
        {"id": "openai/whisper-base", "name": "Whisper Base", "description": "Fast model, 74M parameters"},
        {"id": "openai/whisper-small", "name": "Whisper Small", "description": "Good balance, 244M parameters"},
        {"id": "openai/whisper-medium", "name": "Whisper Medium", "description": "High accuracy, 769M parameters"},
        {"id": "openai/whisper-large-v3", "name": "Whisper Large V3", "description": "Highest accuracy, 1550M parameters"},
        {"id": "openai/whisper-large-v3-turbo", "name": "Whisper Large V3 Turbo", "description": "Ultra-fast with high accuracy, 809M parameters"}
    ]
    
    def __init__(self, model_id="openai/whisper-large-v3-turbo"):
        """
        ローカルWhisper文字起こしクラスの初期化
        
        Parameters
        ----------
        model_id : str, optional
            使用するWhisperモデルのID（デフォルト: whisper-medium）
        """
        self.model_id = model_id
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        # GPU使用時の最適化設定
        if torch.cuda.is_available():
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.matmul.allow_tf32 = True
            print(f"[INFO] GPU optimization enabled: {torch.cuda.get_device_name()}")
        else:
            print(f"[INFO] Using CPU for transcription")
        
        # モデルとプロセッサーの初期化
        self.model = None
        self.processor = None
        self.pipe = None
        
        # カスタム語彙（プロンプト）のキャッシュ
        self.custom_vocabulary = []
        
        # システム指示用のリスト
        self.system_instructions = []
        
        # パフォーマンス最適化用のキャッシュ
        self._audio_cache = {}
        self._last_transcription_time = 0
        
        # モデルの読み込み（フォールバック付き）
        self._load_model_with_fallback()
    
    def _load_model_with_fallback(self):
        """フォールバック機能付きでモデルを読み込む"""
        # まず指定されたモデルで試行
        try:
            self._load_model()
            return
        except Exception as e:
            print(f"[WARNING] Failed to load {self.model_id}: {e}")
        
        # フォールバックモデルのリスト
        fallback_models = [
            "openai/whisper-large-v3-turbo",
            "openai/whisper-small",
            "openai/whisper-base",
            "openai/whisper-tiny"
        ]
        
        # フォールバックモデルを順番に試行
        for fallback_model in fallback_models:
            try:
                print(f"[INFO] Trying fallback model: {fallback_model}")
                self.model_id = fallback_model
                self._load_model()
                print(f"[INFO] Successfully loaded fallback model: {fallback_model}")
                return
            except Exception as e:
                print(f"[WARNING] Failed to load fallback model {fallback_model}: {e}")
                continue
        
        # すべてのモデルが失敗した場合
        raise Exception("すべてのWhisperモデルの読み込みに失敗しました。インターネット接続を確認してください。")
    
    def _check_cache_status(self):
        """キャッシュの状態を確認する"""
        try:
            cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
            if os.path.exists(cache_dir):
                cache_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, dirnames, filenames in os.walk(cache_dir)
                    for filename in filenames)
                print(f"[INFO] Cache directory exists: {cache_dir}")
                print(f"[INFO] Cache size: {cache_size / (1024*1024):.2f} MB")
                
                # 現在のモデルがキャッシュにあるかチェック
                model_cache_path = os.path.join(cache_dir, "models--" + self.model_id.replace("/", "--"))
                if os.path.exists(model_cache_path):
                    print(f"[INFO] Model {self.model_id} found in cache")
                    return True
                else:
                    print(f"[INFO] Model {self.model_id} not found in cache")
                    return False
            else:
                print(f"[INFO] Cache directory does not exist: {cache_dir}")
                return False
        except Exception as e:
            print(f"[WARNING] Failed to check cache status: {e}")
            return False

    def _load_model(self):
        """モデルとプロセッサーを読み込む"""
        try:
            print(f"[INFO] Loading model: {self.model_id}")
            print(f"[INFO] Device: {self.device}, dtype: {self.torch_dtype}")
            
            # キャッシュの状態を確認
            is_cached = self._check_cache_status()
            
            # キャッシュディレクトリの確認
            cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
            print(f"[INFO] Cache directory: {cache_dir}")
            
            if is_cached:
                print(f"[INFO] Using cached model: {self.model_id}")
            else:
                print(f"[INFO] Downloading model: {self.model_id}")
            
            # モデルの読み込み（キャッシュを使用）
            self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                self.model_id,
                torch_dtype=self.torch_dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True,
                cache_dir=cache_dir,
                local_files_only=False  # キャッシュにない場合はダウンロード
            )
            self.model.to(self.device)
            
            # プロセッサーの読み込み（キャッシュを使用）
            self.processor = AutoProcessor.from_pretrained(
                self.model_id,
                cache_dir=cache_dir,
                local_files_only=False
            )
            
            # パイプラインの作成
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=self.model,
                tokenizer=self.processor.tokenizer,
                feature_extractor=self.processor.feature_extractor,
                torch_dtype=self.torch_dtype,
                device=self.device,
                # パフォーマンス最適化設定
                model_kwargs={"use_cache": True},
                generate_kwargs={"do_sample": False},  # 決定論的生成で高速化
            )
            
            print(f"[INFO] Model loaded successfully: {self.model_id}")
            
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            print(f"[ERROR] Error type: {type(e).__name__}")
            print(f"[ERROR] Full error details: {str(e)}")
            
            # より具体的なエラーメッセージを提供
            if "Connection" in str(e) or "timeout" in str(e).lower():
                raise Exception(f"インターネット接続エラー: {e}")
            elif "disk space" in str(e).lower() or "no space" in str(e).lower():
                raise Exception(f"ディスク容量不足: {e}")
            elif "permission" in str(e).lower():
                raise Exception(f"権限エラー: {e}")
            else:
                raise Exception(f"モデル読み込みエラー: {e}")
    
    @classmethod
    def get_available_models(cls):
        """
        利用可能なモデルのリストを返す
        
        Returns
        -------
        list
            利用可能なモデルの情報を含む辞書のリスト
        """
        return cls.AVAILABLE_MODELS
        
    def set_model(self, model_id):
        """
        文字起こしに使用するモデルを設定する
        
        Parameters
        ----------
        model_id : str
            使用するモデルのID
        """
        if model_id != self.model_id:
            self.model_id = model_id
            self._load_model()
        
    def add_custom_vocabulary(self, terms):
        """
        文字起こし精度向上のためのカスタム語彙を追加する
        
        Parameters
        ----------
        terms : str or list
            追加する語彙（単語または単語のリスト）
        """
        if isinstance(terms, str):
            terms = [terms]
        self.custom_vocabulary.extend(terms)
    
    def clear_custom_vocabulary(self):
        """
        カスタム語彙リストをクリアする
        """
        self.custom_vocabulary = []
    
    def get_custom_vocabulary(self):
        """
        現在のカスタム語彙リストを取得する
        
        Returns
        -------
        list
            現在設定されているカスタム語彙のリスト
        """
        return self.custom_vocabulary
    
    def add_system_instruction(self, instructions):
        """
        システムプロンプトに指示を追加する
        
        Parameters
        ----------
        instructions : str or list
            追加するシステム指示（文字列または文字列のリスト）
        """
        if isinstance(instructions, str):
            instructions = [instructions]
        self.system_instructions.extend(instructions)
    
    def clear_system_instructions(self):
        """
        システム指示リストをクリアする
        """
        self.system_instructions = []
    
    def get_system_instructions(self):
        """
        現在のシステム指示リストを取得する
        
        Returns
        -------
        list
            現在設定されているシステム指示のリスト
        """
        return self.system_instructions
    
    def _build_prompt(self):
        """
        カスタム語彙とシステム指示からプロンプトを構築する
        
        Returns
        -------
        str
            構築されたプロンプト文字列
        """
        prompt_parts = []
        
        # 日本語対応のデフォルト指示を追加
        prompt_parts.append("Transcribe accurately in the original language. For Japanese, use proper Japanese characters and punctuation.")
        
        # カスタム語彙を追加
        if self.custom_vocabulary:
            vocab_text = " ".join(self.custom_vocabulary)
            prompt_parts.append(f"Vocabulary: {vocab_text}")
        
        # システム指示を追加
        if self.system_instructions:
            instructions_text = " ".join(self.system_instructions)
            prompt_parts.append(f"Instructions: {instructions_text}")
        
        return " ".join(prompt_parts)
    
    def _load_audio(self, audio_file):
        """
        音声ファイルを読み込んで適切な形式に変換する
        
        Parameters
        ----------
        audio_file : str
            音声ファイルのパス
            
        Returns
        -------
        dict
            音声データとサンプリングレートを含む辞書
        """
        try:
            # キャッシュをチェック
            if audio_file in self._audio_cache:
                print(f"[INFO] Using cached audio data for: {audio_file}")
                return self._audio_cache[audio_file]
            
            # 音声ファイルを読み込み
            audio_data, sample_rate = sf.read(audio_file)
            
            # モノラルに変換（ステレオの場合）
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
            
            # 16kHzにリサンプリング（必要に応じて）
            if sample_rate != 16000:
                # 簡単なリサンプリング（実際のプロジェクトではlibrosaなどを使用）
                print(f"[WARNING] Sample rate {sample_rate}Hz detected. Whisper expects 16kHz.")
            
            result = {
                "array": audio_data,
                "sampling_rate": sample_rate
            }
            
            # キャッシュに保存（メモリ使用量を考慮して最大10個まで）
            if len(self._audio_cache) < 10:
                self._audio_cache[audio_file] = result
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Failed to load audio file: {e}")
            raise
    
    def _optimize_generation_params(self, audio_duration):
        """
        音声の長さに基づいて生成パラメータを最適化する
        
        Parameters
        ----------
        audio_duration : float
            音声の長さ（秒）
            
        Returns
        -------
        dict
            最適化された生成パラメータ
        """
        # 音声の長さに基づいてパラメータを調整
        if audio_duration <= 10.0:
            # 短い音声（10秒以下）- より高速化
            max_tokens = 64  # より少ないトークン数
            temperature = 0.0  # 単一の温度値で高速化
            print(f"[INFO] Short audio detected ({audio_duration:.2f}s), using optimized parameters")
        elif audio_duration <= 30.0:
            # 中程度の音声（10-30秒）
            max_tokens = 128  # 短縮
            temperature = 0.0
            print(f"[INFO] Medium audio detected ({audio_duration:.2f}s), using balanced parameters")
        else:
            # 長い音声（30秒以上）
            max_tokens = 256  # 短縮
            temperature = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
            print(f"[INFO] Long audio detected ({audio_duration:.2f}s), using comprehensive parameters")
        
        return {
            "max_new_tokens": max_tokens,
            "num_beams": 1,
            "condition_on_prev_tokens": False,
            "compression_ratio_threshold": 1.35,
            "temperature": temperature,
            "logprob_threshold": -1.0,
            "no_speech_threshold": 0.6,
            "return_timestamps": True,
        }
    
    def transcribe(self, audio_file, language=None, response_format="text"):
        """
        ローカルWhisperモデルを使用して音声を文字起こしする
        
        Parameters
        ----------
        audio_file : str
            文字起こしする音声ファイルのパス
        language : str, optional
            文字起こしの言語コード（例："en"、"ja"、"zh"）
        response_format : str, optional
            応答フォーマット："text"、"json"、"verbose_json"、または"vtt"
            
        Returns
        -------
        str or dict
            応答フォーマットによって文字列または辞書形式の文字起こし結果
        """
        start_time = time.time()
        
        try:
            # ファイルの存在確認
            audio_path = Path(audio_file)
            if not audio_path.exists():
                raise FileNotFoundError(f"音声ファイルが見つかりません: {audio_file}")
            
            print(f"[INFO] Transcribing: {audio_file}")
            print(f"[INFO] Language: {language or 'auto'}")
            
            # 音声ファイルを読み込み
            audio = self._load_audio(str(audio_path))
            
            # 音声の長さをチェック
            audio_duration = len(audio["array"]) / audio["sampling_rate"]
            print(f"[INFO] Audio duration: {audio_duration:.2f} seconds")
            
            # 最適化された生成パラメータを取得
            generate_kwargs = self._optimize_generation_params(audio_duration)
            
            # 言語が指定されている場合は追加
            if language and language != "auto":
                generate_kwargs["language"] = language
                print(f"[INFO] Using specified language: {language}")
            else:
                print(f"[INFO] Using automatic language detection")
            
            # カスタム語彙とシステム指示を処理（簡素化版）
            prompt = self._build_prompt()
            if prompt:
                print(f"[INFO] Using custom prompt: {prompt}")
                # プロンプトが長い場合はmax_new_tokensを調整
                prompt_length = len(prompt.split())
                if prompt_length > 50:  # プロンプトが長い場合
                    generate_kwargs["max_new_tokens"] = max(128, generate_kwargs["max_new_tokens"] - prompt_length)
                
                # プロンプトを直接渡す（簡素化）
                try:
                    result = self.pipe(audio, generate_kwargs=generate_kwargs, prompt=prompt)
                except TypeError:
                    # promptパラメータがサポートされていない場合は、forced_decoder_idsを使用
                    print(f"[WARNING] Direct prompt not supported, using forced_decoder_ids")
                    prompt_tokens = self.processor.tokenizer.encode(prompt, add_special_tokens=False)
                    
                    # 言語とタスクを明示的に設定して警告を回避
                    if language and language != "auto":
                        generate_kwargs["language"] = language
                    generate_kwargs["task"] = "transcribe"
                    
                    # forced_decoder_idsを使用（警告は出るが動作する）
                    decoder_prompt_ids = self.processor.get_decoder_prompt_ids(language=language or "en", task="transcribe")
                    
                    # forced_decoder_idsを正しく設定
                    if isinstance(decoder_prompt_ids, tuple):
                        forced_decoder_ids = list(decoder_prompt_ids)
                    else:
                        forced_decoder_ids = [decoder_prompt_ids]
                    
                    # プロンプトトークンを追加
                    if forced_decoder_ids and len(forced_decoder_ids) > 0:
                        if isinstance(forced_decoder_ids[0], list):
                            forced_decoder_ids[0].extend(prompt_tokens)
                        else:
                            forced_decoder_ids[0] = list(forced_decoder_ids[0]) + prompt_tokens
                    
                    generate_kwargs["forced_decoder_ids"] = forced_decoder_ids
                    result = self.pipe(audio, generate_kwargs=generate_kwargs)
            else:
                # 文字起こしを実行（プロンプトなし）
                result = self.pipe(audio, generate_kwargs=generate_kwargs)
            
            # 処理時間を記録
            processing_time = time.time() - start_time
            self._last_transcription_time = processing_time
            print(f"[INFO] Transcription completed successfully in {processing_time:.2f} seconds")
            
            # 応答フォーマットに応じて結果を返す
            if response_format == "text":
                return result["text"]
            elif response_format == "json":
                return {
                    "text": result["text"],
                    "language": result.get("language", language),
                    "chunks": result.get("chunks", [])
                }
            elif response_format == "verbose_json":
                return result
            else:
                return result["text"]
                
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"[ERROR] Transcription failed after {processing_time:.2f} seconds: {e}")
            # 長い音声ファイルのエラーの場合は、より詳細な情報を提供
            if "3000 mel input features" in str(e) or "return_timestamps" in str(e):
                print(f"[ERROR] Long audio file detected. This error occurs when processing audio longer than 30 seconds.")
                print(f"[ERROR] The fix has been applied with return_timestamps=True parameter.")
            raise
    
    def get_last_transcription_time(self):
        """
        最後の文字起こし処理時間を取得する
        
        Returns
        -------
        float
            最後の文字起こし処理にかかった時間（秒）
        """
        return self._last_transcription_time
