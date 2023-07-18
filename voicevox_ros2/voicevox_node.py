import json
import wave

import pyaudio
import rclpy
import requests
from rclpy.node import Node
from rione_interfaces.srv import TextToSpeech

SPEAKER_ID = 2
TMP_FILE = "/tmp/tts.wav"
CHUNK = 1024


class VoicevoxNode(Node):
    def __init__(self):
        super().__init__("voicevox_node")

        self.declare_parameter("speaker_id", SPEAKER_ID)
        self._speaker_id = self.get_parameter("speaker_id").value

        self._tts_srv = self.create_service(TextToSpeech, "tts", self.tts_callback)

        self.get_logger().info("voicevox_node is running")
        self.get_logger().info(f"speaker_id {self._speaker_id}")

    def tts_callback(self, request, response):
        self.get_logger().info(f"Generating voice: {request.text}")

        try:
            # 音声合成クエリの作成
            audio_query = requests.post(
                "http://127.0.0.1:50021/audio_query", params={"text": request.text, "speaker": self._speaker_id}
            )

            # 音声合成データの作成
            synthesis = requests.post(
                "http://127.0.0.1:50021/synthesis",
                params={"speaker": self._speaker_id},
                data=json.dumps(audio_query.json()),
            )

            # wavファイルを/tmpに保存
            with open(TMP_FILE, "wb") as f:
                f.write(synthesis.content)

            # pyaudioで再生
            w = wave.open(TMP_FILE, "rb")
            p = pyaudio.PyAudio()
            stream = p.open(
                format=p.get_format_from_width(w.getsampwidth()),
                channels=w.getnchannels(),
                rate=w.getframerate(),
                output=True,
            )

            # 再生開始
            data = w.readframes(CHUNK)
            while len(data) > 0:
                stream.write(data)
                data = w.readframes(CHUNK)

            # 再生終了
            stream.stop_stream()
            stream.close()
            p.terminate()

            self.get_logger().info("Succecfully generated and played voice")

            response.result = True
        except Exception as e:
            self.get_logger().info("Failed to generate or play voice")
            print(e)

            response.result = False

        return response


def main():
    rclpy.init()

    voicevox_node = VoicevoxNode()

    try:
        rclpy.spin(voicevox_node)
    except KeyboardInterrupt:
        print("\nCtrl-c is pressed")
    finally:
        voicevox_node.destroy_node()

    rclpy.shutdown()
