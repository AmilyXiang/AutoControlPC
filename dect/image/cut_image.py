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
    
    img_area = img.shape[0] * img.shape[1]
    screen_cnt = _find_screen_contour(cnts, img_area)
    print(f"Screen contour points found: {screen_cnt}")
    print(edged.shape)

    rect_pts = order_points(screen_cnt)
    print(f"Ordered screen contour points: {rect_pts}")

    warped = get_warped_image(img, screen_cnt)
    warped = cv2.rotate(warped, cv2.ROTATE_90_CLOCKWISE)
    if debug:
        cv2.imshow("Warped", warped)
        cv2.waitKey(0)
    
    return warped

def _find_screen_contour(cnts, img_area):
    """Find the phone-screen quadrilateral among detected contours.

    Strategy:
    - Skip contours whose area is < 1% of the image (noise).
    - Try multiple approxPolyDP epsilon values (tight → loose) to find
      a 4-vertex polygon. The real screen may have slightly rounded
      corners that need a looser epsilon.
    - If no contour simplifies to exactly 4 vertices, fall back to the
      largest contour and force a 4-corner approximation via its
      bounding rotated rect.
    """
    min_area = img_area * 0.01  # at least 1% of the resized image
    for c in cnts:
        if cv2.contourArea(c) < min_area:
            break  # sorted by area desc, everything after is smaller
        peri = cv2.arcLength(c, True)
        for eps in (0.02, 0.04, 0.06, 0.08, 0.10):
            approx = cv2.approxPolyDP(c, eps * peri, True)
            if len(approx) == 4:
                return approx

    # Fallback: use the largest contour (if big enough) and derive
    # a 4-corner quad from its minimum-area rotated rectangle.
    if cnts and cv2.contourArea(cnts[0]) >= min_area:
        rect = cv2.minAreaRect(cnts[0])
        box = cv2.boxPoints(rect)
        return box.reshape(-1, 1, 2).astype(np.int32)
    return None

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
    
    img_area = img.shape[0] * img.shape[1]
    screen_cnt = _find_screen_contour(cnts, img_area)
    if screen_cnt is None:
        print("[DECT] No screen contour (quadrilateral) detected, check camera feed and lighting conditions")
        return None
    rect_pts = order_points(screen_cnt)

    warped = get_warped_image(img, screen_cnt)
    warped = cv2.rotate(warped, cv2.ROTATE_90_CLOCKWISE)
    if debug:
        cv2.imshow("Warped", warped)
        cv2.waitKey(0)
    
    return warped
