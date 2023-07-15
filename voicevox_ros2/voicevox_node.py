import json
import time

import pyaudio
import rclpy
import requests
from rclpy.node import Node
from rione_interfaces.srv import TextToSpeech

SPEAKER_ID = 2


class VoicevoxNode(Node):
    def __init__(self):
        super().__init__("voicevox_node")

        self.declare_parameter("speaker_id", SPEAKER_ID)
        self._speaker_id = self.get_parameter("speaker_id").value

        self._tts_srv = self.create_service(TextToSpeech, "tts", self.tts_callback)

    def tts_callback(self, request, response):
        self.get_logger().info(f"Generating voice: {request.text}")

        try:
            # 音声合成クエリの作成
            query = requests.post(
                "http://127.0.0.1:50021/audio_query", params={"text": request.text, "speaker": self._speaker_id}
            )

            # 音声合成データの作成
            synthesis = requests.post(
                "http://127.0.0.1:50021/synthesis", params={"speaker": self._speaker_id}, data=json.dumps(query.json())
            )

            # pyaudioで再生
            p = pyaudio.PyAudio()

            stream = p.open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

            # 再生するときノイズがあるので少し待つ
            time.sleep(0.2)

            # 音声データの再生
            self.get_logger().info(f"Speaking: {request.text}")
            stream.write(synthesis.content)

            # 再生の終了
            stream.stop_stream()
            stream.close()

            p.terminate()

            response.result = True
        except Exception as e:
            self.get_logger().info("Failed to generate or play voice")
            print(e)

            response.result = False

        return response


def main():
    rclpy.init()

    voicevox_node = VoicevoxNode()

    rclpy.spin(voicevox_node)

    voicevox_node.destroy_node()

    rclpy.shutdown()
