import atexit
import sys

import cv2
from cv2.typing import MatLike

from hwdesk import logger
from hwdesk.camera.base import BaseCamera


class MS2130(BaseCamera):
    def __init__(self, index: int, fps: int = 10):
        logger.info("Initializing MS2130...")
        self.index = index
        self.fps = fps
        self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            logger.info(f"Openning video capture device ({index})...")
            self.cap.open(index)
        assert self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        assert self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        assert self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 50)
        assert self.cap.set(cv2.CAP_PROP_CONTRAST, 50)
        assert self.cap.set(cv2.CAP_PROP_SATURATION, 50)
        assert self.cap.set(cv2.CAP_PROP_HUE, 50)
        assert self.cap.set(cv2.CAP_PROP_FPS, fps)
        video_format = self.cap.get(cv2.CAP_PROP_FOURCC)
        video_format = int(video_format).to_bytes(4, sys.byteorder).decode()
        logger.info(f"MS2130 video format: {video_format}")
        atexit.register(lambda: self.cap.release())
        super().__init__(is_software=False)

    def screenshot(self) -> MatLike | None:
        self.cap.read()
        return self.cap.read()[1]

    def release(self) -> None:
        self.cap.release()