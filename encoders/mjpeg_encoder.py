from typing import Any, Generator
from encoders.encoder import Encoder

class MJPEGEncoder(Encoder):
    """
    Encodes frames into MJPEG stream.
    """

    @classmethod
    def get_content_type(cls) -> str:
        return "multipart/x-mixed-replace;boundary=frame"

    @classmethod
    def encode(cls, input: Generator[bytes, Any, None]) -> Generator[bytes, Any, None]:

        # yield frames until stream is closed
        try:

            for frame in input:
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(frame) + b'\r\n')
        
        except GeneratorExit:
            pass
