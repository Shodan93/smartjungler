import mss
import numpy as np
from config import CHAT_REGION


def capture_chat():
    """Macht einen Screenshot der konfigurierten Chat-Region.

    Gibt ein BGRA numpy-Array zurück (wie von mss geliefert).
    """
    with mss.mss() as sct:
        screenshot = sct.grab(CHAT_REGION)
        return np.array(screenshot)
