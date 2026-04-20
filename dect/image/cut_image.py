import cv2
import os
import numpy as np

debug = False

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=2).flatten()
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=2).flatten()
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def get_warped_image(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

def straighten_screen(image_path, save_path, file_name):
    img = cv2.imread(image_path+file_name)
    img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 9)
    edged = cv2.Canny(blurred, 50, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    edged = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

    if debug:
        cv2.imshow("Edged", edged)
        cv2.waitKey(0)
    cnts, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    
    screen_cnt = None
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.1 * peri, True)
        if len(approx) == 4:
            screen_cnt = approx
            break
    print(f"找到的屏幕轮廓点: {screen_cnt}")
    print(edged.shape)

    rect_pts = order_points(screen_cnt)
    print(f"排序后的屏幕轮廓点: {rect_pts}")

    warped = get_warped_image(img, screen_cnt)
    warped = cv2.rotate(warped, cv2.ROTATE_90_CLOCKWISE)
    if debug:
        cv2.imshow("Warped", warped)
        cv2.waitKey(0)
    
    return warped

def straighten_screen_from_np(img):
    img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 9)
    edged = cv2.Canny(blurred, 50, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    edged = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

    if debug:
        cv2.imshow("Edged", edged)
        cv2.waitKey(0)
    cnts, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    
    screen_cnt = None
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.1 * peri, True)
        if len(approx) == 4:
            screen_cnt = approx
            break
    if screen_cnt is None:
        print("[DECT] 未检测到屏幕轮廓（四边形），请检查摄像头画面和光照条件")
        return None
    rect_pts = order_points(screen_cnt)

    warped = get_warped_image(img, screen_cnt)
    warped = cv2.rotate(warped, cv2.ROTATE_90_CLOCKWISE)
    if debug:
        cv2.imshow("Warped", warped)
        cv2.waitKey(0)
    
    return warped
