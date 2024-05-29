import queue
import time
from threading import Thread
from typing import Any

import numpy as np
from cv2.typing import MatLike
from numpy.typing import NDArray

from hwdesk.actions.actions import Click
from hwdesk.actions.actions import Move
from hwdesk.actions.actions import MoveAndClick
from hwdesk.actions.actions import PressAndRelease
from hwdesk.camera.base import BaseCamera
from hwdesk.camera.ms2130 import MS2130
from hwdesk.controls.base import BaseControls
from hwdesk.controls.ch9329 import CH9329
from hwdesk.window import ImgWindow


def gui_thread(
    window: ImgWindow,
    img_queue: queue.Queue[MatLike | NDArray[Any]],
    controller: BaseControls,
):
    modiers = {"shift": "shift", "ctrl": "ctrl", "win": "win", "alt": "alt"}
    pressed: list[str] = []
    while window.root.winfo_exists():
        try:
            img = img_queue.get_nowait()
            window.imshow(img)
        except queue.Empty:
            window.root.update()
        if not window.actions.empty():
            while not window.actions.empty():
                act = window.actions.get()
                keyt: tuple[bool, str] = (False, "")
                if isinstance(act, PressAndRelease):
                    keyt = (False, act.key)
                modifier = modiers.get(keyt[1], "")
                key = keyt[1]
                if modifier != key and key and not keyt[0]:
                    if pressed:
                        modifier = pressed.pop()
                    print(f"{key=}+{modifier=}, COM5")

                elif not keyt[0] and modifier:
                    pressed.append(modifier)
                elif keyt[0] and modifier:
                    pressed = [i for i in pressed if i != keyt[1]]
                if (
                    isinstance(act, MoveAndClick)
                    or isinstance(act, Move)
                    or isinstance(act, Click)
                ):
                    act.execute(controller)
        else:
            pressed.clear()
        time.sleep(1 / 30)


def capture_thread(
    img_queue: queue.Queue[MatLike | NDArray[Any]], camera: BaseCamera
):
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    while True:
        cur_time = time.time()
        img = camera.screenshot()
        if img is not None:
            img_queue.put(img)
        else:
            img_queue.put(dummy_img)
        diff = time.time() - cur_time
        if diff > 1:
            continue
        # do best to preserve camera fps,
        # as to fast queuing camera might cause
        # camera lagging
        sleep_time = diff - (1000 / camera.fps)
        if sleep_time > 0:
            time.sleep(sleep_time)


def main():
    contorller = CH9329("COM3")
    camera = MS2130(1)
    widow = ImgWindow("win1")
    img_queue: queue.Queue[MatLike | NDArray[Any]] = queue.Queue()
    t1 = Thread(target=capture_thread, args=(img_queue, camera))
    # we want to close camera as soon as gui closes
    t1.daemon = True
    t1.start()
    gui_thread(widow, img_queue, contorller)
    camera.release()


if __name__ == "__main__":
    main()