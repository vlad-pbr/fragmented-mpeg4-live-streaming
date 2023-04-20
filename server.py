#!/usr/bin/python3.8

from typing import Any, Generator
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from uvicorn import run

from encoders.encoder import Encoder
from utils.streaming_utils import method_to_encoder, frame_stream

app = FastAPI()

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
    run("server:app", host="0.0.0.0", port=20000, workers=10)

if __name__ == "__main__":
    main()
