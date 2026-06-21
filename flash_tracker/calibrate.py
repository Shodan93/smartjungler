"""Kalibrierungs-Tool für die Chat-Region.

Starte dieses Script, WÄHREND League läuft (am besten im Spiel mit
sichtbarem Chat). Es macht einen Vollbild-Screenshot. Ziehe mit
gedrückter Maustaste ein Rechteck um das Chatfenster.

Beim Loslassen werden die passenden CHAT_REGION-Werte ausgegeben,
die du 1:1 in config.py eintragen kannst.

Bedienung:
    - Linke Maustaste gedrückt halten und Rechteck ziehen
    - 'r'  = Auswahl zurücksetzen
    - Enter/'q' = beenden
"""
import sys
import time
import mss
import numpy as np
import cv2

start = None
end = None
drawing = False


def on_mouse(event, x, y, flags, param):
    global start, end, drawing
    if event == cv2.EVENT_LBUTTONDOWN:
        start = (x, y)
        end = (x, y)
        drawing = True
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        end = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        end = (x, y)
        drawing = False
        print_region()


def print_region():
    if not start or not end:
        return
    left = min(start[0], end[0])
    top = min(start[1], end[1])
    width = abs(end[0] - start[0])
    height = abs(end[1] - start[1])
    print("\n>>> In config.py eintragen:")
    print("CHAT_REGION = {")
    print(f'    "top":    {top},')
    print(f'    "left":   {left},')
    print(f'    "width":  {width},')
    print(f'    "height": {height},')
    print("}\n")


def main():
    # Countdown, damit du zu League (offener Chat) wechseln kannst,
    # bevor der Screenshot gemacht wird. Dauer via Argument: calibrate.py 8
    secs = 5
    for a in sys.argv[1:]:
        if a.isdigit():
            secs = int(a)
    print(f"Wechsle JETZT zu League (offener Chat)! Screenshot in {secs}s …")
    for i in range(secs, 0, -1):
        print(f"  {i} …", flush=True)
        time.sleep(1)

    with mss.mss() as sct:
        screen = np.array(sct.grab(sct.monitors[1]))
    screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)

    win = "Chat-Region markieren  (r=reset, q/Enter=Ende)"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(win, on_mouse)

    while True:
        frame = screen.copy()
        if start and end:
            cv2.rectangle(frame, start, end, (0, 255, 136), 2)
        cv2.imshow(win, frame)
        k = cv2.waitKey(20) & 0xFF
        if k in (ord("q"), 13, 27):  # q, Enter, Esc
            break
        if k == ord("r"):
            globals()["start"] = None
            globals()["end"] = None

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
