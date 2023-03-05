#!/usr/bin/python3.8

from time import sleep
from typing import Any, Dict, Generator
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from uvicorn import run
from os import listdir

from encoders.encoder import Encoder
from encoders.mjpeg_encoder import MJPEGEncoder
from encoders.mpeg4_encoder import MPEG4Encoder

ACTUAL_FPS = 60
method_to_encoder: Dict[str, Encoder] = {
    "mpeg4": MPEG4Encoder(),
    "mjpeg": MJPEGEncoder()
}
app = FastAPI()

def frame_stream() -> Generator[bytes, Any, None]:
    """
    Frame generator with variable framerate.
    """

    # get list of image names
    images = sorted(listdir("./frames"))

    # yield frames until generator is closed
    try:

        while True:

            for image in images:

                with open(f"./frames/{image}", "rb") as image_fd:

                        # yield frame
                        yield image_fd.read()

                        # TODO varied fps
                        sleep(1/ACTUAL_FPS)

    except GeneratorExit:
        pass


@app.get("/live/{method}")
async def live(method: str):
    """
    Returns encoded frames via chunked response based on requested method.
    """
    
    # resolve encoding solution
    encoder: Encoder = method_to_encoder.get(method, None)
    if not encoder:
        raise HTTPException(status_code=400, detail=f"Unsupported encoder method: '{method}'.")

    # get encoder stream with connection close handler
    stream: Generator[bytes, Any, None] = encoder.encode(frame_stream())
    async def _end_stream():
        stream.close()

    # encode and return chunks
    return StreamingResponse(stream, media_type=encoder.get_content_type(), background=_end_stream)

def main():
    run(app=app, host="0.0.0.0", port=20000)

if __name__ == "__main__":
    main()
