from queue import Queue
from subprocess import DEVNULL, PIPE, Popen
from threading import Thread
from time import sleep
from typing import Any, Generator
from encoders.encoder import Encoder
from datetime import datetime, timedelta

DESIRED_FPS: int = 60
FRAMES_PER_KEYFRAME: int = 1
H264_CRF: int = 25

class MPEG4Encoder(Encoder):

    _encoder_cmd = [
        "ffmpeg",
        "-r", f"{DESIRED_FPS}",
        "-i", "pipe:0",
        "-g", f"{FRAMES_PER_KEYFRAME}",
        "-vf", "drawtext=text='%{localtime}':fontsize=48:fontcolor=white:box=1:boxborderw=6:boxcolor=black@0.75:x=(w-text_w)/2:y=h-text_h-20",
        "-vcodec", "libx264",
        "-tune", "zerolatency",
        "-flush_packets", "1",
        "-preset", "ultrafast",
        "-crf", f"{H264_CRF}",
        "-an",
        "-f", "mp4",
        "-movflags", "frag_keyframe+empty_moov+faststart",
        "pipe:1"
    ]

    @classmethod
    def get_content_type(cls) -> str:
        return "video/mp4"

    @classmethod
    def encode(cls, input: Generator[bytes, Any, None]) -> Generator[bytes, Any, None]:
        
        # init frame queue
        queue = Queue(maxsize=DESIRED_FPS)
        complete = False

        # run encoder process
        encoder_process = Popen(
            cls._encoder_cmd,
            stdin=PIPE,
            stdout=PIPE,
            stderr=DEVNULL
        )

        def _enqueue():

            for frame in input:

                # if queue is full - drop last frame
                if queue.full():
                    queue.get()

                # enqueue new frame
                queue.put(frame)

                # iterating thread must properly close the generator
                if complete:
                    input.close()

        def _feed():

            frame: bytes = None
            next_feed: datetime = datetime.now()

            try:

                while not complete:

                    if datetime.now() > next_feed:

                        # if frame in queue - switch to new frame
                        if not queue.empty():
                            frame = queue.get()
                        
                        # send frame to encoder
                        if frame:
                            encoder_process.stdin.write(frame)

                        next_feed += timedelta(milliseconds=1000 / queue.maxsize)

            except BrokenPipeError:
                pass

        # start enqueueing and feeding threads
        Thread(target=_enqueue).start()
        Thread(target=_feed).start()

        # yield encoded frames until generator is closed
        try:
            while True:
                yield encoder_process.stdout.readline()
        except GeneratorExit:
            pass

        # cleanup
        encoder_process.kill()
        complete = True
