# Copyright (c) 2026 Mishutka
# Licensed under the MIT License. See LICENSE file for details.
import sys
import os
import json
import copy
import csv
import time

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QGraphicsView, QGraphicsScene, QLabel, QFormLayout,
    QDoubleSpinBox, QSpinBox, QToolBar, QAction, QMessageBox,
    QInputDialog, QGraphicsRectItem, QGraphicsEllipseItem, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QLineEdit, QDialogButtonBox, QGraphicsItemGroup, QGraphicsPolygonItem,
    QGraphicsLineItem, QGraphicsItem, QScrollArea, QComboBox, QGraphicsPathItem, QGraphicsTextItem, QGraphicsPixmapItem
)
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QKeySequence, QCursor, QPolygonF, QPainterPath, QFont, QPixmap
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer

def get_app_dir():
    """Папка, где лежит программа (.py или .exe)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def find_column(header, alternatives):
    """Поиск индекса столбца по возможным именам (без регистра)."""
    lower = [str(h).strip().lower() for h in header]
    for alt in alternatives:
        alt = alt.lower()
        if alt in lower:
            return lower.index(alt)
    return -1

LIB_FILENAME = "footprints.json"

# ---------- дефолтная библиотека ----------
DEFAULT_FOOTPRINT_LIBRARY = {
    "0201":  {"type": "chip", "size": [0.6, 0.3],   "zero_angle_tape": 0, "pins": 2},
    "0402":  {"type": "chip", "size": [1.0, 0.5],   "zero_angle_tape": 0, "pins": 2},
    "0603":  {"type": "chip", "size": [1.6, 0.8],   "zero_angle_tape": 0, "pins": 2},
    "0805":  {"type": "chip", "size": [2.0, 1.25],  "zero_angle_tape": 0, "pins": 2},
    "1206":  {"type": "chip", "size": [3.2, 1.6],   "zero_angle_tape": 0, "pins": 2},
    "1210":  {"type": "chip", "size": [3.2, 2.5],   "zero_angle_tape": 0, "pins": 2},
    "C0402": {"type": "chip", "size": [1.0, 0.5],   "zero_angle_tape": 0, "pins": 2},
    "C0603": {"type": "chip", "size": [1.6, 0.8],   "zero_angle_tape": 0, "pins": 2},
    "C0805": {"type": "chip", "size": [2.0, 1.25],  "zero_angle_tape": 0, "pins": 2},
    "C1206": {"type": "chip", "size": [3.2, 1.6],   "zero_angle_tape": 0, "pins": 2},
    "R0402": {"type": "chip", "size": [1.0, 0.5],   "zero_angle_tape": 0, "pins": 2},
    "R0603": {"type": "chip", "size": [1.6, 0.8],   "zero_angle_tape": 0, "pins": 2},
    "R0805": {"type": "chip", "size": [2.0, 1.25],  "zero_angle_tape": 0, "pins": 2},
    "R1206": {"type": "chip", "size": [3.2, 1.6],   "zero_angle_tape": 0, "pins": 2},
    "LED0603": {"type": "led", "size": [1.6, 0.8],  "zero_angle_tape": 0, "pins": 2},
    "SOD123":  {"type": "sod", "size": [3.7, 1.8],  "zero_angle_tape": 0, "pins": 2},
    "SOD323":  {"type": "sod", "size": [2.1, 1.3],  "zero_angle_tape": 0, "pins": 2},
    "SOT23":    {"type": "sot", "size": [3.0, 1.4],  "zero_angle_tape": 0, "pins": 3},
    "SOT23-3":  {"type": "sot", "size": [3.0, 1.4],  "zero_angle_tape": 0, "pins": 3},
    "SOT23-5":  {"type": "sot", "size": [2.9, 1.6],  "zero_angle_tape": 0, "pins": 5},
    "SOT23-6":  {"type": "sot", "size": [2.9, 1.6],  "zero_angle_tape": 0, "pins": 6},
    "SOT223":   {"type": "sot", "size": [6.5, 3.5],  "zero_angle_tape": 0, "pins": 4},
    "SOT89":    {"type": "sot", "size": [4.5, 2.5],  "zero_angle_tape": 0, "pins": 3},
    "SOT323":   {"type": "sot", "size": [2.0, 1.25], "zero_angle_tape": 0, "pins": 3},
    "SOT363":   {"type": "sot", "size": [2.1, 2.0],  "zero_angle_tape": 0, "pins": 6},
    "SOT523":   {"type": "sot", "size": [1.6, 1.2],  "zero_angle_tape": 0, "pins": 3},
    "SOT563":   {"type": "sot", "size": [1.6, 1.6],  "zero_angle_tape": 0, "pins": 6},
    "SOT343":   {"type": "sot", "size": [2.0, 1.25], "zero_angle_tape": 0, "pins": 4},
    "SOT457":   {"type": "sot", "size": [2.0, 2.0],  "zero_angle_tape": 0, "pins": 6},
    "SOT764":   {"type": "sot", "size": [2.6, 2.6],  "zero_angle_tape": 0, "pins": 8},
    "SC70":     {"type": "sot", "size": [2.0, 1.25], "zero_angle_tape": 0, "pins": 3},
    "SC70-3":   {"type": "sot", "size": [2.0, 1.25], "zero_angle_tape": 0, "pins": 3},
    "SC70-5":   {"type": "sot", "size": [2.0, 1.25], "zero_angle_tape": 0, "pins": 5},
    "SC70-6":   {"type": "sot", "size": [2.0, 1.25], "zero_angle_tape": 0, "pins": 6},
    "SOIC8":   {"type": "soic", "size": [4.9, 3.9], "zero_angle_tape": 0, "pins": 8},
    "SOIC14":  {"type": "soic", "size": [8.7, 3.9], "zero_angle_tape": 0, "pins": 14},
    "SOIC16":  {"type": "soic", "size": [10.3, 3.9],"zero_angle_tape": 0, "pins": 16},
    "SOP4":    {"type": "sop", "size": [4.4, 2.8], "zero_angle_tape": 0, "pins": 4},
    "SOP8":    {"type": "sop", "size": [4.9, 3.9], "zero_angle_tape": 0, "pins": 8},
    "SOP16":   {"type": "sop", "size": [10.0,4.0], "zero_angle_tape": 0, "pins": 16},
    "TSSOP8":  {"type": "tssop","size": [3.0, 4.4], "zero_angle_tape": 0, "pins": 8},
    "TSSOP14": {"type": "tssop","size": [5.0, 4.4], "zero_angle_tape": 0, "pins": 14},
    "TSSOP20": {"type": "tssop","size": [6.5, 4.4], "zero_angle_tape": 0, "pins": 20},
    "QFN32":   {"type": "qfn", "size": [5.0, 5.0],  "zero_angle_tape": 0, "pins": 32},
    "QFN48":   {"type": "qfn", "size": [7.0, 7.0],  "zero_angle_tape": 0, "pins": 48},
    "QFN64":   {"type": "qfn", "size": [9.0, 9.0],  "zero_angle_tape": 0, "pins": 64},
    "QFP32":   {"type": "qfp", "size": [7.0, 7.0],  "zero_angle_tape": 0, "pins": 32},
    "QFP64":   {"type": "qfp", "size": [10.0,10.0], "zero_angle_tape": 0, "pins": 64},
    "QFP100":  {"type": "qfp", "size": [14.0,14.0], "zero_angle_tape": 0, "pins": 100},
    "LQFP48":  {"type": "qfp", "size": [7.0, 7.0],  "zero_angle_tape": 0, "pins": 48},
    "LQFP64":  {"type": "qfp", "size": [10.0,10.0], "zero_angle_tape": 0, "pins": 64},
    "LQFP100": {"type": "qfp", "size": [14.0,14.0], "zero_angle_tape": 0, "pins": 100},
    "BGA50":   {"type": "bga", "size": [6.0, 6.0],  "zero_angle_tape": 0, "pins": 50},
    "BGA144":  {"type": "bga", "size": [14.0,14.0], "zero_angle_tape": 0, "pins": 144},
    "DO-214AC": {"type": "do214", "size": [4.5, 2.6],   "zero_angle_tape": 0, "pins": 2},
    "SMA":      {"type": "do214", "size": [4.5, 2.6],   "zero_angle_tape": 0, "pins": 2},
    "DO-214AA": {"type": "do214", "size": [4.6, 3.95],  "zero_angle_tape": 0, "pins": 2},
    "SMB":      {"type": "do214", "size": [4.6, 3.95],  "zero_angle_tape": 0, "pins": 2},
    "DO-214AB": {"type": "do214", "size": [7.11, 6.22], "zero_angle_tape": 0, "pins": 2},
    "SMC":      {"type": "do214", "size": [7.11, 6.22], "zero_angle_tape": 0, "pins": 2},
    "USIP8":    {"type": "module", "size": [3.0, 2.8], "zero_angle_tape": 0, "pins": 8}
}

# ---------- функции работы с JSON ----------
def get_lib_path():
    return os.path.join(get_app_dir(), LIB_FILENAME)

def load_footprint_library():
    path = get_lib_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError
            changed = False
            for k, v in DEFAULT_FOOTPRINT_LIBRARY.items():
                if k not in data:
                    data[k] = v
                    changed = True
            for fp in data.values():
                if "comment" not in fp:
                    fp["comment"] = ""
                    changed = True
            if changed:
                with open(path, "w", encoding="utf-8") as fw:
                    json.dump(data, fw, indent=2, ensure_ascii=False)
            return data
        except Exception:
            return json.loads(json.dumps(DEFAULT_FOOTPRINT_LIBRARY))
    else:
        lib = json.loads(json.dumps(DEFAULT_FOOTPRINT_LIBRARY))
        for fp in lib.values():
            fp["comment"] = ""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(lib, f, indent=2, ensure_ascii=False)
        return lib

def save_footprint_library(lib):
    path = get_lib_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(lib, f, indent=2, ensure_ascii=False)

FOOTPRINT_LIBRARY = load_footprint_library()
# ---------- генерация матрицы падов ----------

def generate_pad_matrix(matrix_type, count_x, count_y,
                        pitch_x, pitch_y, pad_w, pad_h,
                        first_pin, order, body_info=None, soic_sides=0):
    """
    matrix_type:
        0 — Полная сетка (BGA)
        1 — QFN (пады по 4 сторонам, внутри body)
        2 — QFP (пады по 4 сторонам, снаружи body)
        3 — SOIC (пады на двух сторонах; soic_sides: 0 — верх+низ, 1 — лево+право)
    """
    pads = []

    if matrix_type == 0:
        # ---------- Полная сетка (BGA) ----------
        total_w = (count_x - 1) * pitch_x
        total_h = (count_y - 1) * pitch_y
        start_x = -total_w / 2.0
        start_y = total_h / 2.0

        coords = []
        for iy in range(count_y):
            for ix in range(count_x):
                coords.append((start_x + ix * pitch_x,
                               start_y - iy * pitch_y))

        if order == 1:
            coords = []
            for iy in range(count_y - 1, -1, -1):
                for ix in range(count_x):
                    coords.append((start_x + ix * pitch_x,
                                   start_y - iy * pitch_y))
        elif order == 2:
            coords = []
            for ix in range(count_x):
                for iy in range(count_y):
                    coords.append((start_x + ix * pitch_x,
                                   start_y - iy * pitch_y))
        elif order == 3:
            coords = []
            for ix in range(count_x):
                for iy in range(count_y - 1, -1, -1):
                    coords.append((start_x + ix * pitch_x,
                                   start_y - iy * pitch_y))
        elif order == 4 and count_x > 1 and count_y > 1:
            ring = []
            for ix in range(count_x):
                ring.append((start_x + ix * pitch_x, start_y))
            for iy in range(1, count_y):
                ring.append((start_x + (count_x - 1) * pitch_x,
                             start_y - iy * pitch_y))
            for ix in range(count_x - 2, -1, -1):
                ring.append((start_x + ix * pitch_x,
                             start_y - (count_y - 1) * pitch_y))
            for iy in range(count_y - 2, 0, -1):
                ring.append((start_x, start_y - iy * pitch_y))
            coords = ring

        pin = first_pin
        for (x, y) in coords:
            pads.append({
                "kind": "pad",
                "x": float(x), "y": float(y),
                "w": float(pad_w), "h": float(pad_h),
                "pin": int(pin),
            })
            pin += 1

        return pads

    # ---------- Периметр: QFN / QFP / SOIC ----------
    if body_info:
        body_w = float(body_info["w"])
        body_h = float(body_info["h"])
        body_x = float(body_info["x"])
        body_y = float(body_info["y"])
    else:
        body_w = 2.0; body_h = 2.0
        body_x = 0.0; body_y = 0.0

    left   = body_x - body_w / 2.0
    right  = body_x + body_w / 2.0
    top    = body_y + body_h / 2.0
    bottom = body_y - body_h / 2.0

    # Координаты по X для верхней и нижней стороны
    if count_x <= 1:
        xs = [body_x]
    else:
        x_first = left + pad_w / 2.0
        x_last  = right - pad_w / 2.0
        step = (x_last - x_first) / (count_x - 1)
        xs = [x_first + i * step for i in range(count_x)]

    # Координаты по Y для левой и правой стороны
    if count_y <= 1:
        ys = [body_y]
    else:
        y_first = top - pad_w / 2.0
        y_last  = bottom + pad_w / 2.0
        step = (y_first - y_last) / (count_y - 1)
        ys = [y_first - i * step for i in range(count_y)]

    # Смещение падов относительно края body:
    # QFN — внутрь (отрицательное), QFP — наружу (положительное)
    if matrix_type == 1:      # QFN — внутри
        top_off_y    = -pad_h / 2.0
        bottom_off_y =  pad_h / 2.0
        right_off_x  = -pad_h / 2.0
        left_off_x   =  pad_h / 2.0
    else:                      # QFP — снаружи
        top_off_y    =  pad_h / 2.0
        bottom_off_y = -pad_h / 2.0
        right_off_x  =  pad_h / 2.0
        left_off_x   = -pad_h / 2.0

    top_pads = []
    for x in xs:
        top_pads.append({
            "kind": "pad",
            "x": float(x), "y": float(top + top_off_y),
            "w": float(pad_w), "h": float(pad_h),
        })

    right_pads = []
    for y in ys:
        right_pads.append({
            "kind": "pad",
            "x": float(right + right_off_x), "y": float(y),
            "w": float(pad_h), "h": float(pad_w),
        })

    bottom_pads = []
    for x in reversed(xs):
        bottom_pads.append({
            "kind": "pad",
            "x": float(x), "y": float(bottom + bottom_off_y),
            "w": float(pad_w), "h": float(pad_h),
        })

    left_pads = []
    for y in reversed(ys):
        left_pads.append({
            "kind": "pad",
            "x": float(left + left_off_x), "y": float(y),
            "w": float(pad_h), "h": float(pad_w),
        })

    # ---------- Формируем итоговую последовательность ----------
    if matrix_type in (1, 2):     # QFN или QFP — по 4 сторонам
        sequence = top_pads + right_pads + bottom_pads + left_pads
    else:                          # SOIC — по 2 сторонам
        if soic_sides == 0:
            # Верх + низ. Верхние — слева направо, нижние — справа налево.
            sequence = top_pads + bottom_pads
        else:
            # Лево + право. Левые — сверху вниз, правые — снизу вверх.
            # Для этого пересоберём left/right пады в правильном порядке.
            left_side = []
            for y in ys:             # сверху вниз
                left_side.append({
                    "kind": "pad",
                    "x": float(left + left_off_x), "y": float(y),
                    "w": float(pad_h), "h": float(pad_w),
                })
            right_side = []
            for y in reversed(ys):   # снизу вверх
                right_side.append({
                    "kind": "pad",
                    "x": float(right + right_off_x), "y": float(y),
                    "w": float(pad_h), "h": float(pad_w),
                })
            sequence = left_side + right_side

    pin = first_pin
    for p in sequence:
        p["pin"] = int(pin)
        pads.append(p)
        pin += 1

    return pads

# ---------- графические элементы ----------

class ShapeRectItem(QGraphicsRectItem):
    def __init__(self, shape_dict, editor, is_pad=False):
        super().__init__()
        self.shape = shape_dict
        self.editor = editor
        self.is_pad = is_pad
        self.resizing = False

        self.setFlags(
            QGraphicsRectItem.ItemIsMovable
            | QGraphicsRectItem.ItemIsSelectable
            | QGraphicsRectItem.ItemSendsGeometryChanges
        )
        color = QColor(30, 144, 255) if not is_pad else QColor(0, 120, 220)
        self.setPen(QPen(color, 1))
        self.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 60)))
        if is_pad:
            self.setZValue(2)
        else:
            self.setZValue(1)
        self.update_from_shape()

    def shape_path(self):
        rect = self.rect()
        corners = self.shape.get("corners", {})
        if corners:
            w = rect.width()
            h = rect.height()
            # Получаем параметры для каждого угла
            tl_r = corners.get("tl", {}).get("radius", 0.0)
            tl_c = corners.get("tl", {}).get("chamfer", 0.0)
            tr_r = corners.get("tr", {}).get("radius", 0.0)
            tr_c = corners.get("tr", {}).get("chamfer", 0.0)
            bl_r = corners.get("bl", {}).get("radius", 0.0)
            bl_c = corners.get("bl", {}).get("chamfer", 0.0)
            br_r = corners.get("br", {}).get("radius", 0.0)
            br_c = corners.get("br", {}).get("chamfer", 0.0)

            # Ограничиваем значения половиной соответствующей стороны
            max_w = w / 2.0
            max_h = h / 2.0
            tl_r = min(tl_r, max_w, max_h)
            tr_r = min(tr_r, max_w, max_h)
            bl_r = min(bl_r, max_w, max_h)
            br_r = min(br_r, max_w, max_h)
            tl_c = min(tl_c, max_w, max_h)
            tr_c = min(tr_c, max_w, max_h)
            bl_c = min(bl_c, max_w, max_h)
            br_c = min(br_c, max_w, max_h)

            # Преобразуем в пиксели
            tl_r_px = tl_r * self.editor.scale_factor
            tr_r_px = tr_r * self.editor.scale_factor
            bl_r_px = bl_r * self.editor.scale_factor
            br_r_px = br_r * self.editor.scale_factor
            tl_c_px = tl_c * self.editor.scale_factor
            tr_c_px = tr_c * self.editor.scale_factor
            bl_c_px = bl_c * self.editor.scale_factor
            br_c_px = br_c * self.editor.scale_factor

            path = QPainterPath()
            # Верхняя сторона (с учётом левого верхнего угла)
            if tl_r_px > 0 or tl_c_px > 0:
                start_x = rect.left() + (tl_r_px if tl_r_px > 0 else tl_c_px)
            else:
                start_x = rect.left()
            path.moveTo(start_x, rect.top())

            # Верхняя сторона до правого верхнего угла
            if tr_r_px > 0 or tr_c_px > 0:
                end_x = rect.right() - (tr_r_px if tr_r_px > 0 else tr_c_px)
            else:
                end_x = rect.right()
            path.lineTo(end_x, rect.top())

            # Правый верхний угол
            if tr_r_px > 0:
                path.arcTo(rect.right() - 2*tr_r_px, rect.top(), 2*tr_r_px, 2*tr_r_px, 90, -90)
            elif tr_c_px > 0:
                path.lineTo(rect.right(), rect.top() + tr_c_px)
            else:
                path.lineTo(rect.right(), rect.top())

            # Правая сторона
            if br_r_px > 0 or br_c_px > 0:
                end_y = rect.bottom() - (br_r_px if br_r_px > 0 else br_c_px)
            else:
                end_y = rect.bottom()
            path.lineTo(rect.right(), end_y)

            # Правый нижний угол
            if br_r_px > 0:
                path.arcTo(rect.right() - 2*br_r_px, rect.bottom() - 2*br_r_px, 2*br_r_px, 2*br_r_px, 0, -90)
            elif br_c_px > 0:
                path.lineTo(rect.right() - br_c_px, rect.bottom())
            else:
                path.lineTo(rect.right(), rect.bottom())

            # Нижняя сторона
            if bl_r_px > 0 or bl_c_px > 0:
                start_x = rect.left() + (bl_r_px if bl_r_px > 0 else bl_c_px)
            else:
                start_x = rect.left()
            path.lineTo(start_x, rect.bottom())

            # Левый нижний угол
            if bl_r_px > 0:
                path.arcTo(rect.left(), rect.bottom() - 2*bl_r_px, 2*bl_r_px, 2*bl_r_px, -90, -90)
            elif bl_c_px > 0:
                path.lineTo(rect.left(), rect.bottom() - bl_c_px)
            else:
                path.lineTo(rect.left(), rect.bottom())

            # Левая сторона
            if tl_r_px > 0 or tl_c_px > 0:
                start_y = rect.top() + (tl_r_px if tl_r_px > 0 else tl_c_px)
            else:
                start_y = rect.top()
            path.lineTo(rect.left(), start_y)

            # Левый верхний угол
            if tl_r_px > 0:
                path.arcTo(rect.left(), rect.top(), 2*tl_r_px, 2*tl_r_px, 180, -90)
            elif tl_c_px > 0:
                path.lineTo(rect.left() + tl_c_px, rect.top())
            else:
                path.lineTo(rect.left(), rect.top())

            path.closeSubpath()
            return path
        else:
            # Общие радиус или срез
            radius = self.shape.get("corner_radius", 0.0) * self.editor.scale_factor
            chamfer = self.shape.get("chamfer", 0.0) * self.editor.scale_factor
            if radius > 0:
                path = QPainterPath()
                path.addRoundedRect(rect, radius, radius)
                return path
            elif chamfer > 0:
                w = rect.width()
                h = rect.height()
                c = min(chamfer, w/2, h/2)
                path = QPainterPath()
                path.moveTo(rect.left() + c, rect.top())
                path.lineTo(rect.right() - c, rect.top())
                path.lineTo(rect.right(), rect.top() + c)
                path.lineTo(rect.right(), rect.bottom() - c)
                path.lineTo(rect.right() - c, rect.bottom())
                path.lineTo(rect.left() + c, rect.bottom())
                path.lineTo(rect.left(), rect.bottom() - c)
                path.lineTo(rect.left(), rect.top() + c)
                path.closeSubpath()
                return path
            else:
                path = QPainterPath()
                path.addRect(rect)
                return path

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawPath(self.shape_path())

    def update_from_shape(self):
        sf = self.editor.scale_factor
        w = float(self.shape.get("w", 0.0)) * sf
        h = float(self.shape.get("h", 0.0)) * sf
        x = float(self.shape.get("x", 0.0)) * sf
        y = float(self.shape.get("y", 0.0)) * sf
        self.setRect(-w/2, -h/2, w, h)
        self.setPos(x, y)
        self.update()

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionHasChanged and not self.resizing:
            sf = self.editor.scale_factor
            pos = self.pos()
            self.shape["x"] = pos.x() / sf
            self.shape["y"] = pos.y() / sf
            if self.isSelected():
                self.editor.update_shape_controls(self.shape)
            if hasattr(self.editor, "_mark_dirty"):
                self.editor._mark_dirty()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier:
            self.resizing = True
            self._resize_start_local = event.pos()
            event.accept()
        else:
            self.resizing = False
            self.setSelected(True)
            self.editor.select_shape(self.shape)
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            p = event.pos()
            half_w = max(0.05 * self.editor.scale_factor, abs(p.x()))
            half_h = max(0.05 * self.editor.scale_factor, abs(p.y()))
            self.setRect(-half_w, -half_h, 2*half_w, 2*half_h)
            sf = self.editor.scale_factor
            rect = self.rect()
            self.shape["w"] = rect.width() / sf
            self.shape["h"] = rect.height() / sf
            self.editor.on_shape_resized(self.shape)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.resizing:
            self.resizing = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)


class Pin1Item(QGraphicsEllipseItem):
    def __init__(self, shape_dict, editor):
        super().__init__()
        self.shape = shape_dict
        self.editor = editor
        self.setFlags(
            QGraphicsEllipseItem.ItemIsMovable
            | QGraphicsEllipseItem.ItemIsSelectable
            | QGraphicsEllipseItem.ItemSendsGeometryChanges
        )
        self.setBrush(QBrush(QColor(255, 80, 80)))
        self.setPen(QPen(QColor(255, 80, 80)))
        self.setZValue(3)
        self.update_from_shape()

    def update_from_shape(self):
        sf = self.editor.scale_factor
        r = float(self.shape.get("r", 0.3)) * sf
        x = float(self.shape.get("x", 0.0)) * sf
        y = float(self.shape.get("y", 0.0)) * sf
        self.setRect(-r, -r, 2*r, 2*r)
        self.setPos(x, y)

    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.ItemPositionHasChanged:
            sf = self.editor.scale_factor
            pos = self.pos()
            self.shape["x"] = pos.x() / sf
            self.shape["y"] = pos.y() / sf
            if self.isSelected():
                self.editor.update_shape_controls(self.shape)
            if hasattr(self.editor, "_mark_dirty"):
                self.editor._mark_dirty()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        self.editor._begin_undo()
        self.setSelected(True)
        self.editor.select_shape(self.shape)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.editor._end_undo()


class DiodeItem(QGraphicsItemGroup):
    def __init__(self, shape_dict, editor):
        super().__init__()
        self.shape = shape_dict
        self.editor = editor
        self.resizing = False

        self.setFlags(
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemIsSelectable
            | QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setZValue(2)

        self.triangle = QGraphicsPolygonItem()
        self.cathode = QGraphicsPolygonItem()
        self.axis_line = QGraphicsLineItem()

        color = QColor(255, 140, 0)
        brush = QBrush(color)
        pen = QPen(color, 1)
        self.triangle.setBrush(brush)
        self.triangle.setPen(pen)
        self.cathode.setBrush(brush)
        self.cathode.setPen(pen)
        self.axis_line.setPen(pen)

        self.addToGroup(self.triangle)
        self.addToGroup(self.cathode)
        self.addToGroup(self.axis_line)

        self.update_from_shape()

    def update_from_shape(self):
        sf = self.editor.scale_factor
        w = float(self.shape.get("w", 0.5)) * sf
        h = float(self.shape.get("h", 0.3)) * sf
        x = float(self.shape.get("x", 0.0)) * sf
        y = float(self.shape.get("y", 0.0)) * sf

        # треугольник
        tri_points = [
            QPointF(-w/2, -h/2),
            QPointF(-w/2,  h/2),
            QPointF( w/2,  0.0)
        ]
        self.triangle.setPolygon(QPolygonF(tri_points))

        # катодная линия (вертикальная полоска справа)
        line_width = max(0.05 * sf, w * 0.12)
        line_height = h * 0.7
        line_x = w/2 - line_width/2
        line_y = -line_height/2
        line_points = [
            QPointF(line_x, line_y),
            QPointF(line_x + line_width, line_y),
            QPointF(line_x + line_width, line_y + line_height),
            QPointF(line_x, line_y + line_height)
        ]
        self.cathode.setPolygon(QPolygonF(line_points))

        # осевая линия
        line_extend = max(0.1 * w, 0.2 * sf)
        line_start_x = -w
        line_end_x = w
        line_y = 0.0
        self.axis_line.setLine(line_start_x, line_y, line_end_x, line_y)

        self.setPos(x, y)
        angle = self.shape.get("angle", 0.0)
        self.setRotation(angle)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and not self.resizing:
            sf = self.editor.scale_factor
            pos = self.pos()
            self.shape["x"] = pos.x() / sf
            self.shape["y"] = pos.y() / sf
            if self.isSelected():
                self.editor.update_shape_controls(self.shape)
            if hasattr(self.editor, "_mark_dirty"):
                self.editor._mark_dirty()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier:
            self.editor._begin_undo()
            self.resizing = True
            self._resize_start_local = event.pos()
            event.accept()
        else:
            self.editor._begin_undo()
            self.resizing = False
            self.setSelected(True)
            self.editor.select_shape(self.shape)
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            p = event.pos()
            sf = self.editor.scale_factor
            new_w = max(0.1, abs(p.x()) * 2 / sf)
            new_h = max(0.1, abs(p.y()) * 2 / sf)
            self.shape["w"] = new_w
            self.shape["h"] = new_h
            self.update_from_shape()
            self.editor.on_shape_resized(self.shape)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.resizing:
            self.resizing = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
        self.editor._end_undo()

class PolarityStripeItem(QGraphicsRectItem):
    """Чёрная полоса (например, плюсовой торец тантала)."""

    def __init__(self, shape_dict, editor):
        super().__init__()
        self.shape = shape_dict
        self.editor = editor
        self.resizing = False

        self.setFlags(
            QGraphicsRectItem.ItemIsMovable
            | QGraphicsRectItem.ItemIsSelectable
            | QGraphicsRectItem.ItemSendsGeometryChanges
        )
        # Сплошная чёрная заливка
        self.setPen(QPen(QColor(0, 0, 0), 1))
        self.setBrush(QBrush(QColor(0, 0, 0)))
        self.setZValue(2)
        self.update_from_shape()

    def update_from_shape(self):
        sf = self.editor.scale_factor
        w = float(self.shape.get("w", 0.5)) * sf
        h = float(self.shape.get("h", 0.15)) * sf
        x = float(self.shape.get("x", 0.0)) * sf
        y = float(self.shape.get("y", 0.0)) * sf
        self.setRect(-w / 2, -h / 2, w, h)
        self.setPos(x, y)
        angle = float(self.shape.get("angle", 0.0))
        self.setRotation(angle)
        self.update()

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionHasChanged and not self.resizing:
            sf = self.editor.scale_factor
            pos = self.pos()
            self.shape["x"] = pos.x() / sf
            self.shape["y"] = pos.y() / sf
            if self.isSelected():
                self.editor.update_shape_controls(self.shape)
            if hasattr(self.editor, "_mark_dirty"):
                self.editor._mark_dirty()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier:
            self.editor._begin_undo()
            self.resizing = True
            self._resize_start_local = event.pos()
            event.accept()
        else:
            self.editor._begin_undo()
            self.resizing = False
            self.setSelected(True)
            self.editor.select_shape(self.shape)
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            p = event.pos()
            half_w = max(0.05 * self.editor.scale_factor, abs(p.x()))
            half_h = max(0.02 * self.editor.scale_factor, abs(p.y()))
            self.setRect(-half_w, -half_h, 2 * half_w, 2 * half_h)
            sf = self.editor.scale_factor
            rect = self.rect()
            self.shape["w"] = rect.width() / sf
            self.shape["h"] = rect.height() / sf
            self.editor.on_shape_resized(self.shape)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.resizing:
            self.resizing = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
        self.editor._end_undo()


class PolaritySignItem(QGraphicsItemGroup):
    """Знак полярности «+» или «−» (два тонких прямоугольника)."""

    def __init__(self, shape_dict, editor):
        super().__init__()
        self.shape = shape_dict
        self.editor = editor
        self.resizing = False

        self.setFlags(
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemIsSelectable
            | QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setZValue(3)

        # Два тонких прямоугольника с чёрной заливкой
        self.h_bar = QGraphicsRectItem()
        self.v_bar = QGraphicsRectItem()
        for bar in (self.h_bar, self.v_bar):
            bar.setPen(QPen(Qt.NoPen))
            bar.setBrush(QBrush(QColor(0, 0, 0)))
            bar.setZValue(3)

        self.addToGroup(self.h_bar)
        self.addToGroup(self.v_bar)

        self.update_from_shape()

    def update_from_shape(self):
        sf = self.editor.scale_factor
        w = float(self.shape.get("w", 0.6)) * sf
        h = float(self.shape.get("h", 0.6)) * sf
        x = float(self.shape.get("x", 0.0)) * sf
        y = float(self.shape.get("y", 0.0)) * sf
        sign = self.shape.get("sign", "+")

        # Толщина штрихов — 18% от меньшей стороны, но не меньше 1 пикселя
        thickness = max(1.0, min(w, h) * 0.18)

        # Горизонтальная черта
        self.h_bar.setRect(-w / 2, -thickness / 2, w, thickness)

        # Вертикальная черта — только для «+»
        if sign == "+":
            self.v_bar.setRect(-thickness / 2, -h / 2, thickness, h)
            self.v_bar.setVisible(True)
        else:
            self.v_bar.setVisible(False)

        self.setPos(x, y)
        angle = float(self.shape.get("angle", 0.0))
        self.setRotation(angle)
        self.update()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and not self.resizing:
            sf = self.editor.scale_factor
            pos = self.pos()
            self.shape["x"] = pos.x() / sf
            self.shape["y"] = pos.y() / sf
            if self.isSelected():
                self.editor.update_shape_controls(self.shape)
            if hasattr(self.editor, "_mark_dirty"):
                self.editor._mark_dirty()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier:
            self.editor._begin_undo()
            self.resizing = True
            self._resize_start_local = event.pos()
            event.accept()
        else:
            self.editor._begin_undo()
            self.resizing = False
            self.setSelected(True)
            self.editor.select_shape(self.shape)
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            p = event.pos()
            sf = self.editor.scale_factor
            new_w = max(0.1, abs(p.x()) * 2 / sf)
            new_h = max(0.1, abs(p.y()) * 2 / sf)
            self.shape["w"] = new_w
            self.shape["h"] = new_h
            self.update_from_shape()
            self.editor.on_shape_resized(self.shape)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.resizing:
            self.resizing = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
        self.editor._end_undo()


# ---------- диалог создания нового корпуса ----------
class NewFootprintDialog(QDialog):
    def __init__(self, parent=None, title="Новый корпус", name="", comment=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)

        self.edit_name = QLineEdit(name)
        self.edit_name.setPlaceholderText("Имя корпуса")
        self.edit_comment = QLineEdit(comment)
        self.edit_comment.setPlaceholderText("Комментарий (необязательно)")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(QLabel("Имя:"))
        layout.addWidget(self.edit_name)
        layout.addWidget(QLabel("Комментарий:"))
        layout.addWidget(self.edit_comment)
        layout.addWidget(buttons)

    def get_data(self):
        return self.edit_name.text().strip(), self.edit_comment.text().strip()

# ---------- диалог генерации матрицы падов ----------
class PadMatrixDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Генерация матрицы падов")
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.combo_matrix_type = QComboBox()
        self.combo_matrix_type.addItems([
            "Полная сетка (BGA)",
            "QFN (пады внутри тела)",
            "QFP (пады снаружи тела)",
            "SOIC (2 стороны)",
        ])

        self.combo_sides = QComboBox()
        self.combo_sides.addItems(["Верх + низ", "Лево + право"])

        self.spin_count_x = QSpinBox()
        self.spin_count_x.setRange(1, 100)
        self.spin_count_x.setValue(4)

        self.spin_count_y = QSpinBox()
        self.spin_count_y.setRange(1, 100)
        self.spin_count_y.setValue(4)

        self.spin_pitch_x = QDoubleSpinBox()
        self.spin_pitch_x.setRange(0.01, 100.0)
        self.spin_pitch_x.setDecimals(3)
        self.spin_pitch_x.setSingleStep(0.05)
        self.spin_pitch_x.setValue(0.5)

        self.spin_pitch_y = QDoubleSpinBox()
        self.spin_pitch_y.setRange(0.01, 100.0)
        self.spin_pitch_y.setDecimals(3)
        self.spin_pitch_y.setSingleStep(0.05)
        self.spin_pitch_y.setValue(0.5)

        self.spin_pad_w = QDoubleSpinBox()
        self.spin_pad_w.setRange(0.01, 100.0)
        self.spin_pad_w.setDecimals(3)
        self.spin_pad_w.setSingleStep(0.05)
        self.spin_pad_w.setValue(0.3)

        self.spin_pad_h = QDoubleSpinBox()
        self.spin_pad_h.setRange(0.01, 100.0)
        self.spin_pad_h.setDecimals(3)
        self.spin_pad_h.setSingleStep(0.05)
        self.spin_pad_h.setValue(0.3)

        self.spin_first_pin = QSpinBox()
        self.spin_first_pin.setRange(0, 10000)
        self.spin_first_pin.setValue(1)

        self.combo_order = QComboBox()
        self.combo_order.addItems([
            "По строкам (сверху-вниз, слева-направо)",
            "По строкам (снизу-вверх, слева-направо)",
            "По столбцам (слева-направо, сверху-вниз)",
            "По столбцам (слева-направо, снизу-вверх)",
            "Против часовой стрелки (по кольцу)",
        ])

        form.addRow("Тип матрицы:", self.combo_matrix_type)
        form.addRow("Стороны (только для SOIC):", self.combo_sides)
        form.addRow("Падов сверху и снизу (count_x):", self.spin_count_x)
        form.addRow("Падов слева и справа (count_y):", self.spin_count_y)
        form.addRow("Шаг по X, мм (только для BGA):", self.spin_pitch_x)
        form.addRow("Шаг по Y, мм (только для BGA):", self.spin_pitch_y)
        form.addRow("Ширина пада (по X), мм:", self.spin_pad_w)
        form.addRow("Высота пада (по Y), мм:", self.spin_pad_h)
        form.addRow("Первый номер вывода:", self.spin_first_pin)
        form.addRow("Порядок нумерации (только для BGA):", self.combo_order)

        layout.addLayout(form)

        # При смене типа матрицы — включаем/выключаем поля шага и порядка
        self.combo_matrix_type.currentIndexChanged.connect(self._update_field_states)
        self._update_field_states(0)

        # Нижний ряд кнопок: Превью ... OK/Cancel
        btn_row = QHBoxLayout()
        self.btn_preview = QPushButton("Превью")
        self.btn_preview.clicked.connect(self.on_preview)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        btn_row.addWidget(self.btn_preview)
        btn_row.addStretch(1)
        btn_row.addWidget(buttons)
        layout.addLayout(btn_row)

        self._preview_dialog = None

    def _update_field_states(self, _):
        """Включает/выключает поля в зависимости от типа матрицы."""
        idx = self.combo_matrix_type.currentIndex()

        if idx == 0:              # BGA
            self.spin_count_x.setEnabled(True)
            self.spin_count_y.setEnabled(True)
            self.spin_pitch_x.setEnabled(True)
            self.spin_pitch_y.setEnabled(True)
            self.combo_order.setEnabled(True)
            self.combo_sides.setEnabled(False)
        elif idx in (1, 2):       # QFN или QFP
            self.spin_count_x.setEnabled(True)
            self.spin_count_y.setEnabled(True)
            self.spin_pitch_x.setEnabled(False)
            self.spin_pitch_y.setEnabled(False)
            self.combo_order.setEnabled(False)
            self.combo_sides.setEnabled(False)
        else:                      # SOIC
            self.spin_count_x.setEnabled(True)
            self.spin_count_y.setEnabled(True)
            self.spin_pitch_x.setEnabled(False)
            self.spin_pitch_y.setEnabled(False)
            self.combo_order.setEnabled(False)
            self.combo_sides.setEnabled(True)

    def get_data(self):
        return {
            "matrix_type": self.combo_matrix_type.currentIndex(),
            "soic_sides": self.combo_sides.currentIndex(),
            "count_x": self.spin_count_x.value(),
            "count_y": self.spin_count_y.value(),
            "pitch_x": self.spin_pitch_x.value(),
            "pitch_y": self.spin_pitch_y.value(),
            "pad_w": self.spin_pad_w.value(),
            "pad_h": self.spin_pad_h.value(),
            "first_pin": self.spin_first_pin.value(),
            "order": self.combo_order.currentIndex(),
        }

    def on_preview(self):
        """Открыть окно предпросмотра и передать туда текущие параметры."""
        data = self.get_data()

        # Получаем shapes текущего корпуса у родителя (FootprintEditorWindow)
        shapes = []
        parent = self.parent()
        if parent is not None and hasattr(parent, "current_shapes"):
            shapes = parent.current_shapes or []

        # Ищем body среди shapes
        body_info = None
        for sh in shapes:
            if sh.get("kind") == "body":
                body_info = {
                    "x": float(sh.get("x", 0.0)),
                    "y": float(sh.get("y", 0.0)),
                    "w": float(sh.get("w", 0.0)),
                    "h": float(sh.get("h", 0.0)),
                }
                break

        if self._preview_dialog is None:
            self._preview_dialog = PadMatrixPreviewDialog(self)
        self._preview_dialog.set_current_shapes(shapes)
        self._preview_dialog.update_from_data(
            data, body_info=body_info,
            soic_sides=data.get("soic_sides", 0),
        )
        self._preview_dialog.show()
        self._preview_dialog.raise_()
        self._preview_dialog.activateWindow()

class PadMatrixPreviewDialog(QDialog):
    """Окно предпросмотра матрицы падов с телом корпуса."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Предпросмотр матрицы падов")
        self.resize(600, 600)
        self.setWindowFlags(Qt.Window)

        layout = QVBoxLayout(self)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setBackgroundBrush(QBrush(QColor(250, 250, 250)))
        layout.addWidget(self.view)

        self.lbl_info = QLabel("")
        layout.addWidget(self.lbl_info)

        self.current_shapes = []

    def set_current_shapes(self, shapes):
        """Передать список уже существующих элементов корпуса."""
        self.current_shapes = shapes or []

    def update_from_data(self, data, body_info=None, soic_sides=0):
        """Перерисовать превью: тело корпуса + матрица падов."""
        self.scene.clear()

        pads = generate_pad_matrix(
            data["matrix_type"], data["count_x"], data["count_y"],
            data["pitch_x"], data["pitch_y"], data["pad_w"], data["pad_h"],
            data["first_pin"], data["order"],
            body_info=body_info, soic_sides=soic_sides,
        )

        minx = miny = 1e9
        maxx = maxy = -1e9

        # ---- 1. Рисуем существующие элементы корпуса ----
        for sh in self.current_shapes:
            kind = sh.get("kind")

            if kind == "body":
                w = float(sh.get("w", 0.0))
                h = float(sh.get("h", 0.0))
                x = float(sh.get("x", 0.0))
                y = float(sh.get("y", 0.0))
                rect = QRectF(x - w/2, y - h/2, w, h)
                path = QPainterPath()
                path.addRect(rect)
                item = QGraphicsPathItem(path)
                pen = QPen(QColor(30, 144, 255))
                pen.setCosmetic(True)
                pen.setWidthF(1.5)
                item.setPen(pen)
                item.setBrush(QBrush(QColor(30, 144, 255, 40)))
                self.scene.addItem(item)
                minx = min(minx, x - w/2); maxx = max(maxx, x + w/2)
                miny = min(miny, y - h/2); maxy = max(maxy, y + h/2)

            elif kind == "pad":
                w = float(sh.get("w", 0.0))
                h = float(sh.get("h", 0.0))
                x = float(sh.get("x", 0.0))
                y = float(sh.get("y", 0.0))
                rect = QRectF(x - w/2, y - h/2, w, h)
                path = QPainterPath()
                path.addRect(rect)
                item = QGraphicsPathItem(path)
                pen = QPen(QColor(0, 120, 220))
                pen.setCosmetic(True)
                pen.setWidthF(1.0)
                item.setPen(pen)
                item.setBrush(QBrush(QColor(0, 120, 220, 40)))
                self.scene.addItem(item)
                minx = min(minx, x - w/2); maxx = max(maxx, x + w/2)
                miny = min(miny, y - h/2); maxy = max(maxy, y + h/2)

            elif kind == "pin1":
                r = float(sh.get("r", 0.3))
                x = float(sh.get("x", 0.0))
                y = float(sh.get("y", 0.0))
                circ = QGraphicsEllipseItem(x - r, y - r, 2*r, 2*r)
                pen = QPen(QColor(220, 60, 60))
                pen.setCosmetic(True)
                pen.setWidthF(1.0)
                circ.setPen(pen)
                # Полупрозрачная заливка — pin1 больше не «съедает» пады
                circ.setBrush(QBrush(QColor(255, 80, 80, 60)))
                self.scene.addItem(circ)
                minx = min(minx, x - r); maxx = max(maxx, x + r)
                miny = min(miny, y - r); maxy = max(maxy, y + r)

            elif kind == "diode":
                w = float(sh.get("w", 0.5))
                h = float(sh.get("h", 0.3))
                x = float(sh.get("x", 0.0))
                y = float(sh.get("y", 0.0))
                tri = QPolygonF([
                    QPointF(x - w/2, y - h/2),
                    QPointF(x - w/2, y + h/2),
                    QPointF(x + w/2, y),
                ])
                item = QGraphicsPolygonItem(tri)
                pen = QPen(QColor(255, 140, 0))
                pen.setCosmetic(True)
                pen.setWidthF(1.0)
                item.setPen(pen)
                item.setBrush(QBrush(QColor(255, 140, 0, 100)))
                self.scene.addItem(item)
                minx = min(minx, x - w/2); maxx = max(maxx, x + w/2)
                miny = min(miny, y - h/2); maxy = max(maxy, y + h/2)

        # ---- 2. Рисуем новые пады из матрицы (без номеров) ----
        for p in pads:
            x = p["x"]; y = p["y"]; w = p["w"]; h = p["h"]
            rect = QRectF(x - w/2, y - h/2, w, h)
            path = QPainterPath()
            path.addRect(rect)
            item = QGraphicsPathItem(path)
            pen = QPen(QColor(220, 30, 30))
            pen.setCosmetic(True)
            pen.setWidthF(1.2)
            item.setPen(pen)
            item.setBrush(QBrush(QColor(255, 200, 200, 100)))
            self.scene.addItem(item)

            minx = min(minx, x - w/2); maxx = max(maxx, x + w/2)
            miny = min(miny, y - h/2); maxy = max(maxy, y + h/2)

        if minx == 1e9:
            self.scene.setSceneRect(QRectF(-1, -1, 2, 2))
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self.lbl_info.setText("Нет данных для отображения")
            return

        # ---- 3. Границы с отступом ----
        margin = max(data["pitch_x"], data["pitch_y"], 0.5)
        rect = QRectF(minx - margin, miny - margin,
                      (maxx - minx) + 2 * margin,
                      (maxy - miny) + 2 * margin)
        self.scene.setSceneRect(rect)
        self.view.fitInView(rect, Qt.KeepAspectRatio)

        self.lbl_info.setText(
            f"Красным — новые пады ({len(pads)} шт., с {data['first_pin']} по "
            f"{data['first_pin'] + len(pads) - 1}). "
            f"Голубым — существующие body/pad. "
            f"Красное кольцо — ключ Pin1."
        )


# ---------- главное окно ----------
class FootprintEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Графический редактор корпусов 'Library Editor' by Mishutka 0.1.1")
        self.resize(1100, 700)
        self.scale_factor = 20.0

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        # левая панель
        left_layout = QVBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск...")
        left_layout.addWidget(self.search_edit)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Footprint", "Comment"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        left_layout.addWidget(self.table)

        self.btn_new_fp = QPushButton("Новый корпус…")
        self.btn_del_fp = QPushButton("Удалить корпус")
        left_layout.addWidget(self.btn_new_fp)
        left_layout.addWidget(self.btn_del_fp)
        self.btn_rename_fp = QPushButton("Переименовать корпус")
        self.btn_clone_fp = QPushButton("Копировать корпус")
        left_layout.addWidget(self.btn_rename_fp)
        left_layout.addWidget(self.btn_clone_fp)
        # ---- МИНИ-ПРЕВЬЮ ----
        left_layout.addWidget(QLabel("Предпросмотр:"))
        self.preview_scene = QGraphicsScene()
        self.preview_view = QGraphicsView(self.preview_scene)
        self.preview_view.setRenderHint(QPainter.Antialiasing)
        self.preview_view.setFixedHeight(200)
        self.preview_view.setInteractive(False)      # без выделения/движения
        self.preview_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.preview_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_layout.addWidget(self.preview_view)
        # ---- КОНЕЦ МИНИ-ПРЕВЬЮ ----
        main_layout.addLayout(left_layout, 1)

        # правая панель
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout, 3)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        right_layout.addWidget(self.view, 2)
        self.view.viewport().setMouseTracking(True)
        self.view.wheelEvent = self.view_wheel_event
        # --- фоновая картинка при первом запуске ---
        self.bg_item = None
        self._show_startup_background()

        # панель свойств с прокруткой
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        form = QFormLayout()
        settings_layout.addLayout(form)
        scroll_area = QScrollArea()
        scroll_area.setWidget(settings_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(400)   # уменьшено для большего графика
        right_layout.addWidget(scroll_area, 1)

        self.lbl_fp_name = QLabel("-")
        self.spin_zero_angle = QDoubleSpinBox()
        self.spin_zero_angle.setRange(-180.0, 180.0)
        self.spin_zero_angle.setSingleStep(5.0)

        self.lbl_sel_type = QLabel("-")
        self.spin_x = QDoubleSpinBox()
        self.spin_y = QDoubleSpinBox()
        self.spin_w = QDoubleSpinBox()
        self.spin_h = QDoubleSpinBox()
        self.spin_r = QDoubleSpinBox()
        self.spin_pin = QSpinBox()
        self.spin_corner_radius = QDoubleSpinBox()
        self.spin_chamfer = QDoubleSpinBox()

        for s in (self.spin_x, self.spin_y, self.spin_w, self.spin_h, self.spin_r,
                  self.spin_corner_radius, self.spin_chamfer):
            s.setRange(-1000.0, 1000.0)
            s.setDecimals(3)
            s.setSingleStep(0.1)
        self.spin_pin.setRange(0, 1024)

        # --- поля для индивидуальных углов (новый формат: тип + значение) ---
        def make_corner_widgets():
            combo = QComboBox()
            combo.addItems(["нет", "радиус", "срез"])
            spin = QDoubleSpinBox()
            spin.setRange(0.0, 100.0)
            spin.setDecimals(3)
            spin.setSingleStep(0.1)
            spin.setEnabled(False)
            combo.setEnabled(False)
            return combo, spin

        self.combo_corner_tl, self.spin_corner_tl = make_corner_widgets()
        self.combo_corner_tr, self.spin_corner_tr = make_corner_widgets()
        self.combo_corner_bl, self.spin_corner_bl = make_corner_widgets()
        self.combo_corner_br, self.spin_corner_br = make_corner_widgets()

        form.addRow("Корпус:", self.lbl_fp_name)
        form.addRow("Нулевой угол (в ленте), °:", self.spin_zero_angle)
        form.addRow(QLabel("<b>Выбранный элемент</b>"), QLabel(""))
        form.addRow("Тип:", self.lbl_sel_type)
        form.addRow("X, мм:", self.spin_x)
        form.addRow("Y, мм:", self.spin_y)
        form.addRow("Ширина, мм:", self.spin_w)
        form.addRow("Высота, мм:", self.spin_h)
        form.addRow("Радиус (ключ), мм:", self.spin_r)
        form.addRow("Радиус скругления (общий), мм:", self.spin_corner_radius)
        form.addRow("Срез (общий), мм:", self.spin_chamfer)
        form.addRow("Номер вывода:", self.spin_pin)
        self.combo_sign_type = QComboBox()
        self.combo_sign_type.addItems(["+", "-"])
        form.addRow("Знак полярности:", self.combo_sign_type)
        form.addRow(QLabel("<b>Индивидуальные углы</b>"), QLabel(""))

        # вспомогательная функция для упаковки combo+spin в один контейнер
        def corner_row(combo, spin):
            w = QWidget()
            lay = QHBoxLayout(w)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(combo)
            lay.addWidget(spin)
            return w

        form.addRow("Верхний левый:", corner_row(self.combo_corner_tl, self.spin_corner_tl))
        form.addRow("Верхний правый:", corner_row(self.combo_corner_tr, self.spin_corner_tr))
        form.addRow("Нижний левый:", corner_row(self.combo_corner_bl, self.spin_corner_bl))
        form.addRow("Нижний правый:", corner_row(self.combo_corner_br, self.spin_corner_br))

        btn_row = QHBoxLayout()
        self.btn_add_body = QPushButton("Добавить корпус")
        self.btn_add_pad = QPushButton("Добавить вывод")
        self.btn_add_pad_matrix = QPushButton("Добавить матрицу падов")
        self.btn_add_pin1 = QPushButton("Добавить ключ (Pin1)")
        self.btn_add_diode = QPushButton("Добавить диод")
        self.btn_del_shape = QPushButton("Удалить элемент")
        btn_row.addWidget(self.btn_add_body)
        btn_row.addWidget(self.btn_add_pad)
        btn_row.addWidget(self.btn_add_pad_matrix)
        btn_row.addWidget(self.btn_add_pin1)
        btn_row.addWidget(self.btn_add_diode)
        btn_row.addWidget(self.btn_del_shape)
        right_layout.addLayout(btn_row)
        btn_row2 = QHBoxLayout()
        self.btn_add_stripe = QPushButton("Добавить полосу (тантал)")
        self.btn_add_polarity_sign = QPushButton("Добавить знак +/-")
        btn_row2.addWidget(self.btn_add_stripe)
        btn_row2.addWidget(self.btn_add_polarity_sign)
        btn_row2.addStretch(1)
        right_layout.addLayout(btn_row2)

        bottom_row = QHBoxLayout()
        self.btn_save_local = QPushButton("Сохранить текущий корпус")
        bottom_row.addWidget(self.btn_save_local)
        right_layout.addLayout(bottom_row)

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Undo / Redo на панели
        self.act_undo_tb = QAction("↶ Отмена (Ctrl+Z)", self)
        self.act_undo_tb.setShortcut(QKeySequence.Undo)
        self.act_undo_tb.triggered.connect(self.on_undo)
        toolbar.addAction(self.act_undo_tb)

        self.act_redo_tb = QAction("↷ Повтор (Ctrl+Y)", self)
        self.act_redo_tb.setShortcut(QKeySequence("Ctrl+Y"))
        self.act_redo_tb.triggered.connect(self.on_redo)
        toolbar.addAction(self.act_redo_tb)

        toolbar.addSeparator()

        self.act_save_json = QAction("Сохранить всю библиотеку в JSON", self)
        toolbar.addAction(self.act_save_json)

        self.act_check_csv = QAction("Проверить CSV по библиотеке", self)
        toolbar.addAction(self.act_check_csv)
        self.act_check_csv.triggered.connect(self.on_check_csv)

        # состояние
        self.current_fp_key = None
        self.current_fp_info = None
        self.current_shapes = None
        self.shape_to_item = {}
        self.selected_shape = None
        # ---- автосохранение ----
        self._dirty = False              # были ли изменения с момента последнего сохранения
        self.auto_save_interval_ms = 3 * 60 * 1000   # 3 минуты
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.setInterval(self.auto_save_interval_ms)
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.start()
        # ---- конец блока автосохранения ----

        # сигналы
        self.search_edit.textChanged.connect(self.filter_table)
        self.table.currentItemChanged.connect(self.on_table_current_item_changed)
        self.table.itemChanged.connect(self.on_table_item_changed)
        self.btn_new_fp.clicked.connect(self.on_new_fp)
        self.btn_del_fp.clicked.connect(self.on_delete_fp)
        self.btn_rename_fp.clicked.connect(self.on_rename_fp)
        self.btn_clone_fp.clicked.connect(self.on_clone_fp)
        self.spin_zero_angle.valueChanged.connect(self.on_zero_angle_changed)
        self.spin_x.valueChanged.connect(self.on_shape_param_changed)
        self.spin_y.valueChanged.connect(self.on_shape_param_changed)
        self.spin_w.valueChanged.connect(self.on_shape_param_changed)
        self.spin_h.valueChanged.connect(self.on_shape_param_changed)
        self.spin_r.valueChanged.connect(self.on_shape_param_changed)
        self.spin_pin.valueChanged.connect(self.on_shape_param_changed)
        self.spin_corner_radius.valueChanged.connect(self.on_shape_param_changed)
        self.spin_chamfer.valueChanged.connect(self.on_shape_param_changed)
        # комбобоксы углов
        self.combo_corner_tl.currentIndexChanged.connect(self.on_corner_type_changed)
        self.combo_corner_tr.currentIndexChanged.connect(self.on_corner_type_changed)
        self.combo_corner_bl.currentIndexChanged.connect(self.on_corner_type_changed)
        self.combo_corner_br.currentIndexChanged.connect(self.on_corner_type_changed)
        # спинбоксы значений углов
        self.spin_corner_tl.valueChanged.connect(self.on_shape_param_changed)
        self.spin_corner_tr.valueChanged.connect(self.on_shape_param_changed)
        self.spin_corner_bl.valueChanged.connect(self.on_shape_param_changed)
        self.spin_corner_br.valueChanged.connect(self.on_shape_param_changed)

        self.btn_add_body.clicked.connect(self.on_add_body)
        self.btn_add_pad.clicked.connect(self.on_add_pad)
        self.btn_add_pad_matrix.clicked.connect(self.on_add_pad_matrix)
        self.btn_add_pin1.clicked.connect(self.on_add_pin1)
        self.btn_add_diode.clicked.connect(self.on_add_diode)
        self.btn_del_shape.clicked.connect(self.on_del_shape)
        self.btn_add_stripe.clicked.connect(self.on_add_stripe)
        self.btn_add_polarity_sign.clicked.connect(self.on_add_polarity_sign)
        self.combo_sign_type.currentIndexChanged.connect(self.on_sign_type_changed)
        self.btn_save_local.clicked.connect(self.on_save_current_fp)
        self.act_save_json.triggered.connect(self.on_save_all_json)

        self.reload_list()

        # clipboard
        self.clipboard = QApplication.clipboard()
        self.shortcut_copy = QAction(self)
        self.shortcut_copy.setShortcut(QKeySequence.Copy)
        self.shortcut_copy.triggered.connect(self.on_copy)
        self.addAction(self.shortcut_copy)
        self.shortcut_paste = QAction(self)
        self.shortcut_paste.setShortcut(QKeySequence.Paste)
        self.shortcut_paste.triggered.connect(self.on_paste)
        self.addAction(self.shortcut_paste)

        self.shortcut_delete = QAction(self)
        self.shortcut_delete.setShortcut(QKeySequence.Delete)
        self.shortcut_delete.triggered.connect(self.on_del_shape)
        self.addAction(self.shortcut_delete)

        # ---- Undo / Redo ----
        self._undo_stack = []
        self._redo_stack = []
        self._undo_open = False
        self._undo_max = 50

        self.act_undo = QAction(self)
        self.act_undo.setShortcut(QKeySequence.Undo)      # обычно Ctrl+Z
        self.act_undo.triggered.connect(self.on_undo)
        self.addAction(self.act_undo)

        self.act_redo = QAction(self)
        self.act_redo.setShortcut(QKeySequence.Redo)      # обычно Ctrl+Shift+Z
        self.act_redo.triggered.connect(self.on_redo)
        self.addAction(self.act_redo)

        # Дополнительная комбинация для Redo: Ctrl+Y (часто используется в Windows)
        self.act_redo2 = QAction(self)
        self.act_redo2.setShortcut(QKeySequence("Ctrl+Y"))
        self.act_redo2.triggered.connect(self.on_redo)
        self.addAction(self.act_redo2)

        # Таймер авто-закрытия транзакции (для спинбоксов и прочих "серий" изменений)
        self._undo_close_timer = QTimer(self)
        self._undo_close_timer.setSingleShot(True)
        self._undo_close_timer.timeout.connect(self._end_undo)
        # ---- конец блока Undo/Redo ----

    # ---------- служебные методы ----------
    def on_copy(self):
        if self.selected_shape is None:
            self.statusBar().showMessage("Нет выбранного элемента для копирования", 3000)
            return
        try:
            payload = copy.deepcopy(self.selected_shape)
            text = json.dumps(payload, ensure_ascii=False)
            self.clipboard.setText(text)
            self.statusBar().showMessage("Элемент скопирован в буфер", 2000)
        except Exception as e:
            self.statusBar().showMessage(f"Ошибка копирования: {e}", 4000)

    def on_paste(self):
        if self.current_shapes is None:
            self.statusBar().showMessage("Нет активного корпуса для вставки", 3000)
            return
        text = self.clipboard.text()
        if not text:
            self.statusBar().showMessage("Буфер пуст", 2000)
            return
        try:
            data = json.loads(text)
            if not isinstance(data, dict) or "kind" not in data:
                self.statusBar().showMessage("В буфере нет данных о форме", 3000)
                return
            new_sh = copy.deepcopy(data)
            cursor_pos = self.view.mapFromGlobal(QCursor.pos())
            scene_pos = self.view.mapToScene(cursor_pos)
            sf = self.scale_factor
            model_x = scene_pos.x() / sf
            model_y = scene_pos.y() / sf
            if "x" in new_sh:
                new_sh["x"] = model_x
            if "y" in new_sh:
                new_sh["y"] = model_y
            self._begin_undo()
            self.current_shapes.append(new_sh)
            self._end_undo()
            self.select_shape(new_sh)
            self.rebuild_scene(preserve_view=True)
            self.statusBar().showMessage("Элемент вставлен", 2000)
        except Exception as e:
            self.statusBar().showMessage(f"Ошибка вставки: {e}", 4000)

    def _show_startup_background(self):
        """Показать backlib.png на рабочем поле при запуске программы."""
        script_dir = get_app_dir()
        img_path = os.path.join(script_dir, "backlib.png")
        if not os.path.exists(img_path):
            print(f"[BG] Файл не найден: {img_path}")
            return
        pixmap = QPixmap(img_path)
        if pixmap.isNull():
            print("[BG] Не удалось загрузить backlib.png")
            return
        self.bg_item = QGraphicsPixmapItem(pixmap)
        self.bg_item.setZValue(-1000)
        self.scene.addItem(self.bg_item)
        self.scene.setSceneRect(self.bg_item.boundingRect())
        self.view.fitInView(self.bg_item.boundingRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        """При растягивании окна — подгоняем картинку под новые размеры."""
        super().resizeEvent(event)
        if (self.bg_item is not None
                and self.bg_item.scene() is not None
                and not self.current_shapes):
            self.view.fitInView(self.bg_item.boundingRect(), Qt.KeepAspectRatio)

    def view_wheel_event(self, event):
        # Пока показан стартовый фон — зум колёсиком запрещён
        if self.bg_item is not None and self.bg_item.scene() is not None:
            event.ignore()
            return
        if event.angleDelta().y() > 0:
            self.view.scale(1.1, 1.1)
        else:
            self.view.scale(0.9, 0.9)

    def reload_list(self):
        self.table.blockSignals(True)   # чтобы при заполнении не срабатывал itemChanged
        self.table.setRowCount(0)
        for key, fp in sorted(FOOTPRINT_LIBRARY.items()):
            row = self.table.rowCount()
            self.table.insertRow(row)

            # --- колонка 0: имя корпуса (запрет редактирования) ---
            item_name = QTableWidgetItem(key)
            item_name.setFlags(item_name.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, item_name)

            # --- колонка 1: комментарий (разрешаем редактирование) ---
            item_comment = QTableWidgetItem(fp.get("comment", ""))
            item_comment.setFlags(item_comment.flags() | Qt.ItemIsEditable)
            self.table.setItem(row, 1, item_comment)

        self.table.blockSignals(False)
        self.filter_table(self.search_edit.text())

    def filter_table(self, text):
        text = text.strip().lower()
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text().lower()
            comment = self.table.item(row, 1).text().lower()
            self.table.setRowHidden(row, not (text == "" or text in name or text in comment))

    def on_table_current_item_changed(self, current, previous):
        if current is not None:
            name = self.table.item(current.row(), 0).text()
            self.on_fp_selected(name)

    def on_table_item_changed(self, item):
        """Вызывается при редактировании ячейки таблицы.
        Нас интересует только столбец 1 (Comment)."""
        if item is None:
            return
        if item.column() != 1:
            return  # реагируем только на комментарии

        row = item.row()
        name_item = self.table.item(row, 0)
        if name_item is None:
            return

        key = name_item.text()
        if key in FOOTPRINT_LIBRARY:
            new_comment = item.text()
            FOOTPRINT_LIBRARY[key]["comment"] = new_comment
            self.statusBar().showMessage(
                f"Комментарий для '{key}' обновлён. "
                f"Не забудьте нажать 'Сохранить всю библиотеку в JSON'.",
                5000
            )
        self._mark_dirty()

    def sync_current_shapes_from_scene(self):
        if not self.current_shapes or not self.shape_to_item:
            return
        sf = self.scale_factor
        for sh in self.current_shapes:
            item = self.shape_to_item.get(id(sh))
            if item is None:
                continue
            kind = sh.get("kind")
            if kind in ("body", "pad", "stripe"):
                pos = item.pos()
                rect = item.rect()
                sh["x"] = pos.x() / sf
                sh["y"] = pos.y() / sf
                sh["w"] = rect.width() / sf
                sh["h"] = rect.height() / sf
            elif kind == "pin1":
                pos = item.pos()
                rect = item.rect()
                sh["x"] = pos.x() / sf
                sh["y"] = pos.y() / sf
                sh["r"] = rect.width() / 2.0 / sf
            elif kind == "diode":
                pos = item.pos()
                sh["x"] = pos.x() / sf
                sh["y"] = pos.y() / sf
            elif kind == "polarity_sign":
                pos = item.pos()
                sh["x"] = pos.x() / sf
                sh["y"] = pos.y() / sf

    def update_size_from_shapes(self, info):
        shapes = info.get("shapes")
        if not shapes:
            return
        minx = miny = 1e9
        maxx = maxy = -1e9
        for sh in shapes:
            kind = sh.get("kind")
            if kind in ("body", "pad"):
                w = float(sh.get("w", 0.0))
                h = float(sh.get("h", 0.0))
                x = float(sh.get("x", 0.0))
                y = float(sh.get("y", 0.0))
                minx = min(minx, x - w/2)
                maxx = max(maxx, x + w/2)
                miny = min(miny, y - h/2)
                maxy = max(maxy, y + h/2)
            elif kind == "pin1":
                r = float(sh.get("r", 0.0))
                x = float(sh.get("x", 0.0))
                y = float(sh.get("y", 0.0))
                minx = min(minx, x - r)
                maxx = max(maxx, x + r)
                miny = min(miny, y - r)
                maxy = max(maxy, y + r)
            elif kind == "diode":
                w = float(sh.get("w", 0.0))
                h = float(sh.get("h", 0.0))
                x = float(sh.get("x", 0.0))
                y = float(sh.get("y", 0.0))
                minx = min(minx, x - w/2)
                maxx = max(maxx, x + w/2)
                miny = min(miny, y - h/2)
                maxy = max(maxy, y + h/2)
            elif kind in ("stripe", "polarity_sign"):
                w = float(sh.get("w", 0.0))
                h = float(sh.get("h", 0.0))
                x = float(sh.get("x", 0.0))
                y = float(sh.get("y", 0.0))
                minx = min(minx, x - w / 2)
                maxx = max(maxx, x + w / 2)
                miny = min(miny, y - h / 2)
                maxy = max(maxy, y + h / 2)

        if minx == 1e9:
            return
        info["size"] = [maxx - minx, maxy - miny]

    def apply_view_transform(self):
        old_center = self.view.mapToScene(self.view.viewport().rect().center())
        self.view.resetTransform()
        angle = float(self.spin_zero_angle.value())
        self.view.rotate(angle)
        self.view.centerOn(old_center)
        if not hasattr(self, '_initial_fit_done'):
            if not self.scene.sceneRect().isNull():
                self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self._initial_fit_done = True

    def on_fp_selected(self, key):
        if self.current_fp_key is not None and self.current_fp_info is not None:
            self.sync_current_shapes_from_scene()
            self.update_size_from_shapes(self.current_fp_info)

        if not key:
            return
        # Переключились на другой корпус — история отмены больше неактуальна
        self._clear_undo_history()
        self.current_fp_key = key
        self.current_fp_info = FOOTPRINT_LIBRARY.get(key)
        if self.current_fp_info is None:
            return

        self.lbl_fp_name.setText(key)
        angle = float(self.current_fp_info.get("zero_angle_tape", 0.0))
        self.spin_zero_angle.blockSignals(True)
        self.spin_zero_angle.setValue(angle)
        self.spin_zero_angle.blockSignals(False)

        if "shapes" not in self.current_fp_info:
            size = self.current_fp_info.get("size", [3.0, 1.5])
            w, h = float(size[0]), float(size[1])
            shapes = [
                {"kind": "body", "x": 0.0, "y": 0.0, "w": w, "h": h,
                 "corner_radius": 0.0, "chamfer": 0.0},
                {"kind": "pin1", "x": -w/2 + 0.3, "y": h/2 - 0.3, "r": 0.25}
            ]
            self.current_fp_info["shapes"] = shapes
            self.current_fp_info.setdefault("mode", "manual")

        self.current_shapes = self.current_fp_info["shapes"]
        self.selected_shape = None
        self.rebuild_scene()
        self.update_shape_controls(None)

    def rebuild_scene(self, preserve_view=False):
        if preserve_view:
            old_center = self.view.mapToScene(self.view.viewport().rect().center())
            old_transform = self.view.transform()

        selected_shape_id = id(self.selected_shape) if self.selected_shape else None
        self.bg_item = None
        self.scene.clear()
        self.shape_to_item.clear()

        if not self.current_shapes:
            self.scene.setSceneRect(QRectF(-10, -10, 20, 20))
            self.apply_view_transform()
            return

        sf = self.scale_factor
        minx = miny = 1e9
        maxx = maxy = -1e9

        for sh in self.current_shapes:
            kind = sh.get("kind")
            if kind in ("body", "pad"):
                item = ShapeRectItem(sh, self, is_pad=(kind == "pad"))
                self.scene.addItem(item)
                self.shape_to_item[id(sh)] = item
                if id(sh) == selected_shape_id:
                    item.setSelected(True)
                w = float(sh.get("w", 0.0))
                h = float(sh.get("h", 0.0))
                x = float(sh.get("x", 0.0))
                y = float(sh.get("y", 0.0))
                minx = min(minx, x - w/2)
                maxx = max(maxx, x + w/2)
                miny = min(miny, y - h/2)
                maxy = max(maxy, y + h/2)

            elif kind == "pin1":
                item = Pin1Item(sh, self)
                self.scene.addItem(item)
                self.shape_to_item[id(sh)] = item
                if id(sh) == selected_shape_id:
                    item.setSelected(True)
                r = float(sh.get("r", 0.0))
                x = float(sh.get("x", 0.0))
                y = float(sh.get("y", 0.0))
                minx = min(minx, x - r)
                maxx = max(maxx, x + r)
                miny = min(miny, y - r)
                maxy = max(maxy, y + r)

            elif kind == "diode":
                item = DiodeItem(sh, self)
                self.scene.addItem(item)
                self.shape_to_item[id(sh)] = item
                if id(sh) == selected_shape_id:
                    item.setSelected(True)
                w = float(sh.get("w", 0.0))
                h = float(sh.get("h", 0.0))
                x = float(sh.get("x", 0.0))
                y = float(sh.get("y", 0.0))
                minx = min(minx, x - w/2)
                maxx = max(maxx, x + w/2)
                miny = min(miny, y - h/2)
                maxy = max(maxy, y + h/2)

            elif kind == "stripe":
                item = PolarityStripeItem(sh, self)
                self.scene.addItem(item)
                self.shape_to_item[id(sh)] = item
                if id(sh) == selected_shape_id:
                    item.setSelected(True)
                w = float(sh.get("w", 0.0))
                h = float(sh.get("h", 0.0))
                x = float(sh.get("x", 0.0))
                y = float(sh.get("y", 0.0))
                minx = min(minx, x - w/2)
                maxx = max(maxx, x + w/2)
                miny = min(miny, y - h/2)
                maxy = max(maxy, y + h/2)

            elif kind == "polarity_sign":
                item = PolaritySignItem(sh, self)
                self.scene.addItem(item)
                self.shape_to_item[id(sh)] = item
                if id(sh) == selected_shape_id:
                    item.setSelected(True)
                w = float(sh.get("w", 0.0))
                h = float(sh.get("h", 0.0))
                x = float(sh.get("x", 0.0))
                y = float(sh.get("y", 0.0))
                minx = min(minx, x - w/2)
                maxx = max(maxx, x + w/2)
                miny = min(miny, y - h/2)
                maxy = max(maxy, y + h/2)

        if minx == 1e9:
            minx, maxx, miny, maxy = -1, 1, -1, 1
        rect = QRectF(minx * sf, miny * sf, (maxx - minx) * sf, (maxy - miny) * sf)
        self.scene.setSceneRect(rect.adjusted(-20, -20, 20, 20))

        if preserve_view:
            self.view.setTransform(old_transform)
            self.view.centerOn(old_center)
        else:
            self.apply_view_transform()

        self._refresh_preview()

    def _refresh_preview(self):
        """Отрисовать миниатюру текущего корпуса в preview_scene."""
        self.preview_scene.clear()

        if not self.current_shapes:
            self.preview_scene.setSceneRect(QRectF(-1, -1, 2, 2))
            self.preview_view.fitInView(self.preview_scene.sceneRect(),
                                        Qt.KeepAspectRatio)
            return

        # Тот же масштаб, что и в основной сцене
        sf = self.scale_factor

        minx = miny = 1e9
        maxx = maxy = -1e9

        for sh in self.current_shapes:
            kind = sh.get("kind")
            if kind in ("body", "pad"):
                w = float(sh.get("w", 0.0)) * sf
                h = float(sh.get("h", 0.0)) * sf
                x = float(sh.get("x", 0.0)) * sf
                y = float(sh.get("y", 0.0)) * sf
                rect = QRectF(-w/2, -h/2, w, h)
                path = QPainterPath()
                path.addRect(rect)
                item = QGraphicsPathItem(path)
                item.setPos(x, y)
                color = QColor(30, 144, 255) if kind == "body" else QColor(0, 120, 220)
                item.setPen(QPen(color))
                item.setBrush(QBrush(QColor(color.red(), color.green(),
                                            color.blue(), 80)))
                self.preview_scene.addItem(item)
                minx = min(minx, x - w/2); maxx = max(maxx, x + w/2)
                miny = min(miny, y - h/2); maxy = max(maxy, y + h/2)

            elif kind == "pin1":
                r = float(sh.get("r", 0.3)) * sf
                x = float(sh.get("x", 0.0)) * sf
                y = float(sh.get("y", 0.0)) * sf
                circ = QGraphicsEllipseItem(-r, -r, 2*r, 2*r)
                circ.setPos(x, y)
                circ.setBrush(QBrush(QColor(255, 80, 80)))
                circ.setPen(QPen(QColor(255, 80, 80)))
                self.preview_scene.addItem(circ)
                minx = min(minx, x - r); maxx = max(maxx, x + r)
                miny = min(miny, y - r); maxy = max(maxy, y + r)

            elif kind == "diode":
                w = float(sh.get("w", 0.5)) * sf
                h = float(sh.get("h", 0.3)) * sf
                x = float(sh.get("x", 0.0)) * sf
                y = float(sh.get("y", 0.0)) * sf
                tri = QPolygonF([
                    QPointF(-w/2, -h/2),
                    QPointF(-w/2,  h/2),
                    QPointF( w/2,  0.0),
                ])
                tri_item = QGraphicsPolygonItem(tri)
                tri_item.setPos(x, y)
                color = QColor(255, 140, 0)
                tri_item.setPen(QPen(color))
                tri_item.setBrush(QBrush(color))
                self.preview_scene.addItem(tri_item)
                # катодная линия
                lw = max(0.05 * sf, w * 0.12)
                lh = h * 0.7
                line_points = QPolygonF([
                    QPointF(w/2 - lw/2, -lh/2),
                    QPointF(w/2 + lw/2, -lh/2),
                    QPointF(w/2 + lw/2,  lh/2),
                    QPointF(w/2 - lw/2,  lh/2),
                ])
                line_item = QGraphicsPolygonItem(line_points)
                line_item.setPos(x, y)
                line_item.setPen(QPen(color))
                line_item.setBrush(QBrush(color))
                self.preview_scene.addItem(line_item)
                minx = min(minx, x - w/2); maxx = max(maxx, x + w/2)
                miny = min(miny, y - h/2); maxy = max(maxy, y + h/2)

            elif kind == "stripe":
                w = float(sh.get("w", 0.5)) * sf
                h = float(sh.get("h", 0.2)) * sf
                x = float(sh.get("x", 0.0)) * sf
                y = float(sh.get("y", 0.0)) * sf
                rect = QRectF(-w / 2, -h / 2, w, h)
                stripe = QGraphicsRectItem(rect)
                stripe.setPos(x, y)
                stripe.setPen(QPen(QColor(0, 0, 0)))
                stripe.setBrush(QBrush(QColor(0, 0, 0)))
                self.preview_scene.addItem(stripe)
                minx = min(minx, x - w / 2); maxx = max(maxx, x + w / 2)
                miny = min(miny, y - h / 2); maxy = max(maxy, y + h / 2)

            elif kind == "polarity_sign":
                w = float(sh.get("w", 0.6)) * sf
                h = float(sh.get("h", 0.6)) * sf
                x = float(sh.get("x", 0.0)) * sf
                y = float(sh.get("y", 0.0)) * sf
                sign = sh.get("sign", "+")
                thickness = max(1.0, min(w, h) * 0.18)

                h_bar = QGraphicsRectItem(-w / 2, -thickness / 2, w, thickness)
                h_bar.setPos(x, y)
                h_bar.setPen(QPen(Qt.NoPen))
                h_bar.setBrush(QBrush(QColor(0, 0, 0)))
                self.preview_scene.addItem(h_bar)

                if sign == "+":
                    v_bar = QGraphicsRectItem(-thickness / 2, -h / 2,
                                              thickness, h)
                    v_bar.setPos(x, y)
                    v_bar.setPen(QPen(Qt.NoPen))
                    v_bar.setBrush(QBrush(QColor(0, 0, 0)))
                    self.preview_scene.addItem(v_bar)

                minx = min(minx, x - w / 2); maxx = max(maxx, x + w / 2)
                miny = min(miny, y - h / 2); maxy = max(maxy, y + h / 2)
        if minx == 1e9:
            minx, maxx, miny, maxy = -1, 1, -1, 1

        # Небольшой отступ
        margin = 5
        rect = QRectF(minx - margin, miny - margin,
                      (maxx - minx) + 2*margin,
                      (maxy - miny) + 2*margin)
        self.preview_scene.setSceneRect(rect)
        self.preview_view.fitInView(rect, Qt.KeepAspectRatio)

    def select_shape(self, shape):
        for item in self.scene.items():
            item.setSelected(False)
        item = self.shape_to_item.get(id(shape))
        if item:
            item.setSelected(True)
        self.selected_shape = shape
        self.update_shape_controls(shape)

    def update_shape_controls(self, shape):
        # блокируем все сигналы
        all_widgets = (
            self.spin_x, self.spin_y, self.spin_w, self.spin_h, self.spin_r,
            self.spin_pin, self.spin_corner_radius, self.spin_chamfer,
            self.combo_corner_tl, self.combo_corner_tr,
            self.combo_corner_bl, self.combo_corner_br,
            self.spin_corner_tl, self.spin_corner_tr,
            self.spin_corner_bl, self.spin_corner_br,
        )
        for w in all_widgets:
            w.blockSignals(True)

        if shape is None:
            self.lbl_sel_type.setText("-")
            for s in (self.spin_x, self.spin_y, self.spin_w, self.spin_h, self.spin_r,
                      self.spin_corner_radius, self.spin_chamfer):
                s.setValue(0.0)
            self.spin_pin.setValue(0)
            for combo in (self.combo_corner_tl, self.combo_corner_tr,
                          self.combo_corner_bl, self.combo_corner_br):
                combo.setCurrentIndex(0)
            for spin in (self.spin_corner_tl, self.spin_corner_tr,
                         self.spin_corner_bl, self.spin_corner_br):
                spin.setValue(0.0)

            for w in all_widgets:
                w.setEnabled(False)
        else:
            kind = shape.get("kind", "?")
            self.lbl_sel_type.setText(kind)
            self.spin_x.setValue(float(shape.get("x", 0.0)))
            self.spin_y.setValue(float(shape.get("y", 0.0)))

            if kind in ("body", "pad", "diode", "stripe", "polarity_sign"):
                self.spin_w.setValue(float(shape.get("w", 0.0)))
                self.spin_h.setValue(float(shape.get("h", 0.0)))
                self.spin_w.setEnabled(True)
                self.spin_h.setEnabled(True)
                self.spin_r.setEnabled(False)
            else:  # pin1
                self.spin_r.setValue(float(shape.get("r", 0.3)))
                self.spin_w.setEnabled(False)
                self.spin_h.setEnabled(False)
                self.spin_r.setEnabled(True)

            # --- заливка для индивидуальных углов ---
            corners = shape.get("corners", {}) if kind == "body" else {}

            def set_corner(combo, spin, corner_key):
                c = corners.get(corner_key, {})
                r = float(c.get("radius", 0.0))
                ch = float(c.get("chamfer", 0.0))
                if r > 0:
                    combo.setCurrentIndex(1)   # радиус
                    spin.setValue(r)
                    spin.setEnabled(True)
                elif ch > 0:
                    combo.setCurrentIndex(2)   # срез
                    spin.setValue(ch)
                    spin.setEnabled(True)
                else:
                    combo.setCurrentIndex(0)   # нет
                    spin.setValue(0.0)
                    spin.setEnabled(False)

            if kind == "body":
                # включаем общие поля
                self.spin_corner_radius.setValue(float(shape.get("corner_radius", 0.0)))
                self.spin_chamfer.setValue(float(shape.get("chamfer", 0.0)))
                self.spin_corner_radius.setEnabled(True)
                self.spin_chamfer.setEnabled(True)

                set_corner(self.combo_corner_tl, self.spin_corner_tl, "tl")
                set_corner(self.combo_corner_tr, self.spin_corner_tr, "tr")
                set_corner(self.combo_corner_bl, self.spin_corner_bl, "bl")
                set_corner(self.combo_corner_br, self.spin_corner_br, "br")

                for w in (self.combo_corner_tl, self.combo_corner_tr,
                          self.combo_corner_bl, self.combo_corner_br):
                    w.setEnabled(True)
            else:
                self.spin_corner_radius.setEnabled(False)
                self.spin_chamfer.setEnabled(False)
                for combo in (self.combo_corner_tl, self.combo_corner_tr,
                              self.combo_corner_bl, self.combo_corner_br):
                    combo.setCurrentIndex(0)
                    combo.setEnabled(False)
                for spin in (self.spin_corner_tl, self.spin_corner_tr,
                             self.spin_corner_bl, self.spin_corner_br):
                    spin.setValue(0.0)
                    spin.setEnabled(False)

            if kind == "pad":
                self.spin_pin.setValue(int(shape.get("pin", 1)))
                self.spin_pin.setEnabled(True)
            else:
                self.spin_pin.setEnabled(False)

            # --- знак полярности: поле всегда активно ---
            if kind == "polarity_sign":
                self.combo_sign_type.blockSignals(True)
                idx = self.combo_sign_type.findText(shape.get("sign", "+"))
                if idx < 0:
                    idx = 0
                self.combo_sign_type.setCurrentIndex(idx)
                self.combo_sign_type.blockSignals(False)

            self.spin_x.setEnabled(True)
            self.spin_y.setEnabled(True)

        for w in all_widgets:
            w.blockSignals(False)

    def on_shape_resized(self, shape):
        if shape is self.selected_shape:
            self.update_shape_controls(shape)

    def on_corner_type_changed(self, _):
        """При смене типа угла (нет/радиус/срез) включаем/выключаем спинбокс."""
        pairs = [
            (self.combo_corner_tl, self.spin_corner_tl),
            (self.combo_corner_tr, self.spin_corner_tr),
            (self.combo_corner_bl, self.spin_corner_bl),
            (self.combo_corner_br, self.spin_corner_br),
        ]
        for combo, spin in pairs:
            # индекс 0 = «нет», 1 = «радиус», 2 = «срез»
            if combo.currentIndex() == 0:
                spin.setEnabled(False)
                spin.setValue(0.0)
            else:
                spin.setEnabled(True)

        # Обновляем данные выбранной формы
        self.on_shape_param_changed(None)

    def on_shape_param_changed(self, _):
        if self.selected_shape is None:
            return
        self._begin_undo()
        sh = self.selected_shape
        kind = sh.get("kind")
        sh["x"] = float(self.spin_x.value())
        sh["y"] = float(self.spin_y.value())
        if kind in ("body", "pad", "diode", "stripe", "polarity_sign"):
            sh["w"] = float(self.spin_w.value())
            sh["h"] = float(self.spin_h.value())
        if kind == "pin1":
            sh["r"] = float(self.spin_r.value())
        if kind == "pad":
            sh["pin"] = int(self.spin_pin.value())
        if kind == "body":
            sh["corner_radius"] = float(self.spin_corner_radius.value())
            sh["chamfer"] = float(self.spin_chamfer.value())

            def pack_corner(combo, spin):
                idx = combo.currentIndex()
                val = float(spin.value())
                if idx == 1:      # радиус
                    return {"radius": val, "chamfer": 0.0}
                elif idx == 2:    # срез
                    return {"radius": 0.0, "chamfer": val}
                else:             # нет
                    return {"radius": 0.0, "chamfer": 0.0}

            corners = {
                "tl": pack_corner(self.combo_corner_tl, self.spin_corner_tl),
                "tr": pack_corner(self.combo_corner_tr, self.spin_corner_tr),
                "bl": pack_corner(self.combo_corner_bl, self.spin_corner_bl),
                "br": pack_corner(self.combo_corner_br, self.spin_corner_br),
            }
            sh["corners"] = corners

        item = self.shape_to_item.get(id(sh))
        if isinstance(item, ShapeRectItem):
            item.update_from_shape()
        elif isinstance(item, Pin1Item):
            item.update_from_shape()
        elif isinstance(item, DiodeItem):
            item.update_from_shape()
        elif isinstance(item, PolarityStripeItem):
            item.update_from_shape()
        elif isinstance(item, PolaritySignItem):
            item.update_from_shape()

        # обновляем превью (если уже добавлено)
        if hasattr(self, "_refresh_preview"):
            self._refresh_preview()
        # Транзакция закроется сама через 400 мс тишины
        self._undo_close_timer.start(400)

    # ---------- кнопки добавления элементов ----------
    def on_add_body(self):
        if self.current_shapes is None:
            return
        sh = {"kind": "body", "x": 0.0, "y": 0.0, "w": 2.0, "h": 1.0,
              "corner_radius": 0.0, "chamfer": 0.0, "corners": {}}
        self._begin_undo()
        self.current_shapes.append(sh)
        self._end_undo()
        self.select_shape(sh)
        self.rebuild_scene(preserve_view=True)
        self._mark_dirty()

    def on_add_pad(self):
        if self.current_shapes is None:
            return
        sh = {"kind": "pad", "x": 0.0, "y": -0.5, "w": 0.1, "h": 0.2, "pin": 1}
        self._begin_undo()
        self.current_shapes.append(sh)
        self._end_undo()
        self.select_shape(sh)
        self.rebuild_scene(preserve_view=True)
        self._mark_dirty()

    def on_add_pad_matrix(self):
        """Генерация матрицы падов с заданными параметрами."""
        if self.current_shapes is None:
            QMessageBox.warning(self, "Нет корпуса",
                                "Сначала выберите или создайте корпус.")
            return

        dlg = PadMatrixDialog(self)
        if dlg.exec_() != QDialog.Accepted:
            return

        data = dlg.get_data()

        # Ищем body среди текущих shapes
        body_info = None
        for sh in self.current_shapes:
            if sh.get("kind") == "body":
                body_info = {
                    "x": float(sh.get("x", 0.0)),
                    "y": float(sh.get("y", 0.0)),
                    "w": float(sh.get("w", 0.0)),
                    "h": float(sh.get("h", 0.0)),
                }
                break

        pads = generate_pad_matrix(
            data["matrix_type"], data["count_x"], data["count_y"],
            data["pitch_x"], data["pitch_y"], data["pad_w"], data["pad_h"],
            data["first_pin"], data["order"],
            body_info=body_info,
            soic_sides=data.get("soic_sides", 0),
        )

        if not pads:
            QMessageBox.warning(self, "Пустой результат",
                                "Заданные параметры не создали ни одного пада.")
            return

        self._begin_undo()
        for pad in pads:
            self.current_shapes.append(pad)
        self._end_undo()

        self.rebuild_scene(preserve_view=True)
        self._mark_dirty()  # если добавляли автосохранение
        self.statusBar().showMessage(
            f"Добавлено падов: {len(pads)} "
            f"(с {data['first_pin']} по {data['first_pin'] + len(pads) - 1})",
            5000
        )
        self._mark_dirty()

    def on_add_pin1(self):
        if self.current_shapes is None:
            return
        sh = {"kind": "pin1", "x": -1.0, "y": 1.0, "r": 0.3}
        self._begin_undo()
        self.current_shapes.append(sh)
        self._end_undo()
        self.select_shape(sh)
        self.rebuild_scene(preserve_view=True)
        self._mark_dirty()

    def on_add_diode(self):
        if self.current_shapes is None:
            return
        sh = {"kind": "diode", "x": 0.0, "y": 0.0, "w": 0.5, "h": 0.3, "angle": 0.0}
        self._begin_undo()
        self.current_shapes.append(sh)
        self._end_undo()
        self.select_shape(sh)
        self.rebuild_scene(preserve_view=True)
        self._mark_dirty()

    def on_add_stripe(self):
        if self.current_shapes is None:
            return
        sh = {"kind": "stripe", "x": 0.0, "y": 0.0,
              "w": 1.0, "h": 0.2, "angle": 0.0}
        self._begin_undo()
        self.current_shapes.append(sh)
        self._end_undo()
        self.select_shape(sh)
        self.rebuild_scene(preserve_view=True)
        self._mark_dirty()

    def on_add_polarity_sign(self):
        if self.current_shapes is None:
            return
        sign_value = self.combo_sign_type.currentText() or "+"
        sh = {"kind": "polarity_sign", "x": 0.0, "y": 0.0,
              "w": 0.6, "h": 0.6, "angle": 0.0, "sign": sign_value}
        self._begin_undo()
        self.current_shapes.append(sh)
        self._end_undo()
        self.select_shape(sh)
        self.rebuild_scene(preserve_view=True)
        self._mark_dirty()

    def on_sign_type_changed(self, _):
        """Смена типа знака (+/-) в свойствах выбранного polarity_sign."""
        if self.selected_shape is None:
            return
        if self.selected_shape.get("kind") != "polarity_sign":
            return
        self._begin_undo()
        self.selected_shape["sign"] = self.combo_sign_type.currentText()
        item = self.shape_to_item.get(id(self.selected_shape))
        if isinstance(item, PolaritySignItem):
            item.update_from_shape()
        self._mark_dirty()
        if hasattr(self, "_refresh_preview"):
            self._refresh_preview()
        self._undo_close_timer.start(400)

    def on_del_shape(self):
        if self.current_shapes is None or self.selected_shape is None:
            return
        self._begin_undo()
        try:
            self.current_shapes.remove(self.selected_shape)
        except ValueError:
            pass
        self._end_undo()
        self.selected_shape = None
        self.rebuild_scene(preserve_view=True)
        self.update_shape_controls(None)
        self._mark_dirty()

    # ---------- операции с корпусами ----------
    def on_zero_angle_changed(self, val):
        if self.current_fp_info is None:
            return
        self._begin_undo()
        self.current_fp_info["zero_angle_tape"] = float(val)
        self.apply_view_transform()
        self._mark_dirty()
        self._undo_close_timer.start(400)

    def on_new_fp(self):
        dlg = NewFootprintDialog(self, "Новый корпус")
        if dlg.exec_() != QDialog.Accepted:
            return
        name, comment = dlg.get_data()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Имя корпуса не может быть пустым.")
            return
        if name in FOOTPRINT_LIBRARY:
            QMessageBox.warning(self, "Ошибка", "Корпус с таким именем уже существует.")
            return
        info = {
            "mode": "manual",
            "zero_angle_tape": 0.0,
            "size": [3.0, 1.5],
            "shapes": [
                {"kind": "body", "x": 0.0, "y": 0.0, "w": 3.0, "h": 1.5,
                 "corner_radius": 0.0, "chamfer": 0.0, "corners": {}},
                {"kind": "pin1", "x": -1.2, "y": 0.7, "r": 0.3}
            ],
            "comment": comment
        }
        FOOTPRINT_LIBRARY[name] = info
        self.reload_list()
        self._mark_dirty()
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == name:
                self.table.selectRow(row)
                break

    def on_delete_fp(self):
        key = self.current_fp_key
        if not key:
            return
        if key not in FOOTPRINT_LIBRARY:
            return
        if QMessageBox.question(self, "Удалить корпус", f"Удалить '{key}' из библиотеки?",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        del FOOTPRINT_LIBRARY[key]
        self.current_fp_key = None
        self.current_fp_info = None
        self.current_shapes = None
        self.selected_shape = None
        self.scene.clear()
        self.reload_list()
        self._mark_dirty()

    def on_rename_fp(self):
        if not self.current_fp_key:
            QMessageBox.warning(self, "Нет корпуса", "Выберите корпус в списке.")
            return
        old_name = self.current_fp_key
        new_name, ok = QInputDialog.getText(self, "Переименовать корпус",
                                            f"Новое имя для корпуса '{old_name}':", text=old_name)
        if not ok or not new_name:
            return
        new_name = new_name.strip()
        if new_name in FOOTPRINT_LIBRARY:
            QMessageBox.warning(self, "Ошибка", "Корпус с таким именем уже существует.")
            return
        FOOTPRINT_LIBRARY[new_name] = FOOTPRINT_LIBRARY.pop(old_name)
        self.current_fp_key = new_name
        self.reload_list()
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == new_name:
                self.table.selectRow(row)
                break
        self.statusBar().showMessage(f"Корпус '{old_name}' переименован в '{new_name}'", 3000)
        self._mark_dirty()

    def on_clone_fp(self):
        if not self.current_fp_key:
            QMessageBox.warning(self, "Нет корпуса", "Выберите корпус в списке.")
            return
        original_name = self.current_fp_key
        original_fp = FOOTPRINT_LIBRARY[original_name]
        new_fp = copy.deepcopy(original_fp)
        base = original_name + "_copy"
        new_name = base
        index = 2
        while new_name in FOOTPRINT_LIBRARY:
            new_name = f"{base}{index}"
            index += 1
        FOOTPRINT_LIBRARY[new_name] = new_fp
        self.reload_list()
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == new_name:
                self.table.selectRow(row)
                break
        self.statusBar().showMessage(f"Создана копия корпуса: {new_name}", 3000)
        self._mark_dirty()

    # ---------- сохранение ----------
    def on_save_current_fp(self):
        if not self.current_fp_key or not self.current_fp_info:
            return
        self.sync_current_shapes_from_scene()
        self.update_size_from_shapes(self.current_fp_info)
        msg = f"Корпус '{self.current_fp_key}' обновлён (в памяти). " \
              f"Чтобы записать в файл, нажмите 'Сохранить всю библиотеку в JSON'."
        self.statusBar().showMessage(msg, 6000)

    def on_save_all_json(self):
        if self.current_fp_key and self.current_fp_info:
            self.sync_current_shapes_from_scene()
            self.update_size_from_shapes(self.current_fp_info)
        save_footprint_library(FOOTPRINT_LIBRARY)
        self._dirty = False
        QMessageBox.information(self, "Сохранено", "Библиотека записана в footprints.json")

    def _mark_dirty(self):
        """Пометить библиотеку как изменённую."""
        self._dirty = True

    def _auto_save(self):
        """Таймер автосохранения: сохраняет только если есть изменения."""
        if not self._dirty:
            return
        try:
            # синхронизируем текущий корпус, если он открыт
            if self.current_fp_key and self.current_fp_info:
                self.sync_current_shapes_from_scene()
                self.update_size_from_shapes(self.current_fp_info)

            save_footprint_library(FOOTPRINT_LIBRARY)
            self._dirty = False
            from datetime import datetime
            now = datetime.now().strftime("%H:%M")
            self.statusBar().showMessage(f"Автосохранение: OK в {now}", 5000)
            print(f"[AUTO-SAVE] библиотека сохранена в {now}")
        except Exception as e:
            self.statusBar().showMessage(f"Автосохранение не удалось: {e}", 5000)
            print(f"[AUTO-SAVE ERROR] {e}")

    def closeEvent(self, event):
        """Спросить, сохранять ли изменения при закрытии."""
        if self._dirty:
            reply = QMessageBox.question(
                self, "Несохранённые изменения",
                "В библиотеке есть несохранённые изменения.\nСохранить их перед закрытием?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )
            if reply == QMessageBox.Save:
                try:
                    if self.current_fp_key and self.current_fp_info:
                        self.sync_current_shapes_from_scene()
                        self.update_size_from_shapes(self.current_fp_info)
                    save_footprint_library(FOOTPRINT_LIBRARY)
                    self._dirty = False
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{e}")
                    event.ignore()
                    return
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        event.accept()

    def on_check_csv(self):
        self.check_dialog = CsvCheckDialog(FOOTPRINT_LIBRARY)
        self.check_dialog.setAttribute(Qt.WA_DeleteOnClose, False)
        self.check_dialog.show()

    # ---------- Undo / Redo ----------
    def _make_snapshot(self):
        """Сделать снимок текущего состояния корпуса."""
        if self.current_fp_info is None:
            return None
        shapes = copy.deepcopy(self.current_shapes) if self.current_shapes else []
        zero = float(self.spin_zero_angle.value())
        sel_idx = -1
        if self.selected_shape is not None and self.current_shapes:
            for i, sh in enumerate(self.current_shapes):
                if sh is self.selected_shape:
                    sel_idx = i
                    break
        return {
            "key": self.current_fp_key,
            "shapes": shapes,
            "zero_angle": zero,
            "selected_idx": sel_idx,
        }

    def _restore_snapshot(self, snap):
        """Восстановить состояние корпуса из снимка."""
        if snap is None or self.current_fp_info is None:
            return
        self.current_fp_info["shapes"] = snap["shapes"]
        self.current_fp_info["zero_angle_tape"] = snap["zero_angle"]
        self.current_shapes = self.current_fp_info["shapes"]

        # Нулевой угол — без сигналов
        self.spin_zero_angle.blockSignals(True)
        self.spin_zero_angle.setValue(snap["zero_angle"])
        self.spin_zero_angle.blockSignals(False)

        # Восстанавливаем выделение по индексу
        idx = snap.get("selected_idx", -1)
        if 0 <= idx < len(self.current_shapes):
            self.selected_shape = self.current_shapes[idx]
        else:
            self.selected_shape = None

        # Полная перерисовка
        self._initial_fit_done = True   # чтобы не сбрасывать зум/поворот
        self.rebuild_scene(preserve_view=True)
        self.update_shape_controls(self.selected_shape)
        self._mark_dirty()

    def _begin_undo(self):
        """Открыть транзакцию отмены: сохраняем снимок «до изменения»."""
        if self._undo_open:
            return
        if self.current_fp_info is None:
            return
        snap = self._make_snapshot()
        if snap is None:
            return
        self._undo_stack.append(snap)
        if len(self._undo_stack) > self._undo_max:
            self._undo_stack.pop(0)
        self._redo_stack.clear()
        self._undo_open = True

    def _end_undo(self):
        """Закрыть транзакцию отмены."""
        self._undo_open = False

    def on_undo(self):
        # Принудительно закрываем незавершённую транзакцию
        self._end_undo()
        if not self._undo_stack:
            self.statusBar().showMessage("Отменять нечего", 2000)
            return
        # Текущее состояние уходит в redo
        cur = self._make_snapshot()
        if cur is not None:
            self._redo_stack.append(cur)
        snap = self._undo_stack.pop()
        self._restore_snapshot(snap)
        self.statusBar().showMessage(
            f"Отмена (осталось в стеке: {len(self._undo_stack)})", 2000
        )

    def on_redo(self):
        self._end_undo()
        if not self._redo_stack:
            self.statusBar().showMessage("Повторять нечего", 2000)
            return
        cur = self._make_snapshot()
        if cur is not None:
            self._undo_stack.append(cur)
        snap = self._redo_stack.pop()
        self._restore_snapshot(snap)
        self.statusBar().showMessage(
            f"Повтор (осталось в стеке: {len(self._redo_stack)})", 2000
        )

    def _clear_undo_history(self):
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._undo_open = False
        if self._undo_close_timer.isActive():
            self._undo_close_timer.stop()

# ---------- простой диалог импорта CSV для проверки ----------
class CsvSimpleImportDialog(QDialog):
    """Упрощённый импорт CSV: кодировка, разделитель, пропуск строк,
       выбор столбца Component Name и превью."""

    DELIMITER_PRESETS = [
        (";",   "Точка с запятой  ( ; )"),
        (",",   "Запятая  ( , )"),
        ("\t",  "Табуляция  ( Tab )"),
        ("|",   "Вертикальная черта  ( | )"),
    ]

    ENCODING_PRESETS = [
        ("utf-8",   "UTF-8"),
        ("cp1251",  "Windows-1251 (кириллица)"),
        ("cp1252",  "Windows-1252"),
        ("latin-1", "Latin-1"),
    ]

    CUSTOM_DELIM = "__custom__"
    PREVIEW_ROWS = 15

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Импорт CSV для проверки")
        self.resize(900, 720)

        self.file_path = file_path
        self.raw_data = None

        layout = QVBoxLayout(self)

        # Заголовок
        lbl_file = QLabel(f"<b>Файл:</b> {os.path.basename(file_path)}")
        lbl_file.setWordWrap(True)
        layout.addWidget(lbl_file)

        # Параметры чтения
        params_row = QHBoxLayout()

        params_row.addWidget(QLabel("Кодировка:"))
        self.combo_encoding = QComboBox()
        for code, label in self.ENCODING_PRESETS:
            self.combo_encoding.addItem(label, code)
        params_row.addWidget(self.combo_encoding)

        params_row.addSpacing(20)
        params_row.addWidget(QLabel("Разделитель:"))
        self.combo_delim = QComboBox()
        for val, label in self.DELIMITER_PRESETS:
            self.combo_delim.addItem(label, val)
        self.combo_delim.addItem("Другой…", self.CUSTOM_DELIM)
        params_row.addWidget(self.combo_delim)

        self.edit_custom_delim = QLineEdit()
        self.edit_custom_delim.setPlaceholderText("символ")
        self.edit_custom_delim.setFixedWidth(60)
        self.edit_custom_delim.setEnabled(False)
        params_row.addWidget(self.edit_custom_delim)

        params_row.addSpacing(20)
        params_row.addWidget(QLabel("Пропустить строк сверху:"))
        self.spin_skip = QSpinBox()
        self.spin_skip.setRange(0, 1000)
        self.spin_skip.setValue(0)
        params_row.addWidget(self.spin_skip)

        params_row.addStretch(1)
        self.btn_reload = QPushButton("Перечитать")
        params_row.addWidget(self.btn_reload)

        layout.addLayout(params_row)

        # Превью
        layout.addWidget(QLabel(
            "Превью (первая не пропущенная строка считается заголовком, показана жирным):"
        ))
        self.table_preview = QTableWidget()
        self.table_preview.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_preview.setSelectionMode(QTableWidget.NoSelection)
        self.table_preview.setAlternatingRowColors(True)
        self.table_preview.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_preview.setMinimumHeight(280)
        layout.addWidget(self.table_preview)

        # Выбор столбца Component Name
        form = QFormLayout()
        self.combo_comp_name = QComboBox()
        form.addRow("Столбец Component Name *:", self.combo_comp_name)
        layout.addLayout(form)

        # Кнопки
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        # Сигналы
        self.combo_encoding.currentIndexChanged.connect(self._reload)
        self.combo_delim.currentIndexChanged.connect(self._on_delim_changed)
        self.edit_custom_delim.editingFinished.connect(self._reload)
        self.spin_skip.valueChanged.connect(self._reload)
        self.btn_reload.clicked.connect(self._reload)

        # Первичная загрузка
        self._reload()

    # ---------- внутренние методы ----------

    def _on_delim_changed(self, _):
        data = self.combo_delim.currentData()
        self.edit_custom_delim.setEnabled(data == self.CUSTOM_DELIM)
        if data != self.CUSTOM_DELIM:
            self._reload()

    def _get_delimiter(self):
        data = self.combo_delim.currentData()
        if data == self.CUSTOM_DELIM:
            txt = self.edit_custom_delim.text()
            return txt[0] if txt else ","
        return data

    def _read_file(self):
        encoding = self.combo_encoding.currentData()
        delim = self._get_delimiter()
        try:
            with open(self.file_path, "r", encoding=encoding, newline="") as f:
                reader = csv.reader(f, delimiter=delim)
                return list(reader)
        except Exception as e:
            QMessageBox.warning(
                self, "Ошибка чтения файла",
                f"Не удалось прочитать файл с кодировкой «{encoding}»:\n{e}"
            )
            return None

    def _reload(self):
        # Запомним текущий выбор по имени столбца
        old_name = None
        if self.combo_comp_name.count() > 0:
            old_name = self.combo_comp_name.currentText()

        data = self._read_file()
        if data is None:
            return

        self.raw_data = data
        skip = self.spin_skip.value()
        if skip >= len(data):
            skip = 0
            self.spin_skip.blockSignals(True)
            self.spin_skip.setValue(0)
            self.spin_skip.blockSignals(False)

        header = data[skip] if data else []

        self._fill_preview(data, skip)
        self._populate_columns(header)

        # Восстановить/установить выбор
        target_idx = -1
        if old_name:
            # Пытаемся найти по имени
            for i in range(self.combo_comp_name.count()):
                if self.combo_comp_name.itemText(i) == old_name:
                    target_idx = i
                    break
        if target_idx < 0:
            # Автоподбор по старому правилу
            auto = find_column(header, ["CN", "component_name", "name",
                                        "description", "Component Name"])
            if auto >= 0:
                for i in range(self.combo_comp_name.count()):
                    if self.combo_comp_name.itemData(i) == auto:
                        target_idx = i
                        break
        if target_idx < 0 and self.combo_comp_name.count() > 0:
            target_idx = 0

        if target_idx >= 0:
            self.combo_comp_name.blockSignals(True)
            self.combo_comp_name.setCurrentIndex(target_idx)
            self.combo_comp_name.blockSignals(False)

    def _fill_preview(self, data, skip):
        self.table_preview.clear()
        if not data or skip >= len(data):
            self.table_preview.setRowCount(0)
            self.table_preview.setColumnCount(0)
            return

        header = data[skip]
        ncols = len(header)
        if ncols == 0:
            self.table_preview.setRowCount(0)
            self.table_preview.setColumnCount(0)
            return

        nrows = min(len(data) - skip, self.PREVIEW_ROWS)
        self.table_preview.setColumnCount(ncols)
        self.table_preview.setRowCount(nrows)
        self.table_preview.setHorizontalHeaderLabels([f"#{i}" for i in range(ncols)])
        self.table_preview.setVerticalHeaderLabels(
            [str(skip + i) for i in range(nrows)]
        )

        for r in range(nrows):
            row_data = data[skip + r] if skip + r < len(data) else []
            for c in range(ncols):
                v = row_data[c] if c < len(row_data) else ""
                item = QTableWidgetItem(str(v))
                if r == 0:
                    f = item.font()
                    f.setBold(True)
                    item.setFont(f)
                    item.setBackground(QBrush(QColor(230, 230, 250)))
                self.table_preview.setItem(r, c, item)

        self.table_preview.resizeColumnsToContents()

    def _populate_columns(self, header):
        self.combo_comp_name.blockSignals(True)
        self.combo_comp_name.clear()
        for i, h in enumerate(header):
            self.combo_comp_name.addItem(f"#{i}: {h}", i)
        self.combo_comp_name.blockSignals(False)

    def accept(self):
        if not self.raw_data:
            QMessageBox.warning(self, "Нет данных",
                                "Файл не прочитан или пуст.")
            return
        skip = self.spin_skip.value()
        if skip >= len(self.raw_data):
            QMessageBox.warning(self, "Нет данных",
                                "После пропуска строк не осталось данных.")
            return
        if self.combo_comp_name.currentData() is None:
            QMessageBox.warning(self, "Не выбран столбец",
                                "Выберите столбец с Component Name.")
            return
        super().accept()

    def get_result(self):
        return {
            "delimiter":  self._get_delimiter(),
            "encoding":   self.combo_encoding.currentData(),
            "skip_lines": self.spin_skip.value(),
            "raw_data":   self.raw_data,
            "comp_col":   self.combo_comp_name.currentData(),
        }

# ---------- диалог проверки CSV ----------
class CsvCheckDialog(QDialog):
    def __init__(self, library, parent=None):
        super().__init__()
        self.setWindowFlags(Qt.Window)
        self.library = library
        self.setWindowTitle("Проверка CSV по библиотеке корпусов")
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        btn_open = QPushButton("Открыть CSV файл")
        btn_open.clicked.connect(self.open_csv)
        layout.addWidget(btn_open)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Component Name", "Used Footprint"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

    def open_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать CSV файл", "", "CSV files (*.csv);;All files (*)"
        )
        if not path:
            return
        dlg = CsvSimpleImportDialog(path, self)
        if dlg.exec_() != QDialog.Accepted:
            return
        result = dlg.get_result()
        try:
            self.process_csv_data(result)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось обработать CSV:\n{str(e)}")

    def process_csv_data(self, result):
        """Построить таблицу по данным, полученным из диалога импорта.
           Компоненты с одинаковым Component Name показываются один раз."""
        raw = result["raw_data"]
        skip = result["skip_lines"]
        comp_col = result["comp_col"]

        if not raw or skip >= len(raw):
            return

        seen = set()
        data = []
        for row in raw[skip + 1:]:
            if not any(cell and str(cell).strip() for cell in row):
                continue
            if comp_col >= len(row):
                comp_name = ""
            else:
                comp_name = str(row[comp_col]).strip()
            if not comp_name:
                continue
            # Пропускаем уже встречавшиеся Component Name
            if comp_name in seen:
                continue
            seen.add(comp_name)

            used_key = self.match_footprint_info(comp_name)
            display_fp = used_key if used_key is not None else "НЕ НАЙДЕН"
            data.append((comp_name, display_fp))

        self.table.setRowCount(len(data))
        for i, (comp, fp) in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(comp))
            item_fp = QTableWidgetItem(fp)
            if fp == "НЕ НАЙДЕН":
                font = item_fp.font()
                font.setBold(True)
                item_fp.setFont(font)
            self.table.setItem(i, 1, item_fp)

    def detect_delimiter(self, first_line):
        if first_line.count(";") > first_line.count(","):
            return ";"
        if "\t" in first_line:
            return "\t"
        return ","

    def find_column(self, header, alternatives):
        lower = [h.strip().lower() for h in header]
        for alt in alternatives:
            if alt.lower() in lower:
                return lower.index(alt.lower())
        return -1

    def match_footprint_info(self, comp_name):
        lib = self.library
        if not comp_name:
            return None
        comp_upper = comp_name.upper()
        for key in lib:
            if key.upper() == comp_upper:
                return key

        patterns = [
            "0201", "0402", "0603", "0805", "1206", "1210",
            "C0402", "C0603", "C0805", "C1206",
            "R0402", "R0603", "R0805", "R1206",
            "SOT23", "SOT23-3", "SOT23-5", "SOT23-6", "SOT223",
            "SOT89", "SOT323", "SOT363", "SOT523", "SOT563",
            "SC70", "SC70-3", "SC70-5", "SC70-6",
            "SOIC8", "SOIC14", "SOIC16", "SOP4", "SOP8", "SOP16",
            "TSSOP8", "TSSOP14", "TSSOP20",
            "QFN32", "QFN48", "QFN64",
            "QFP32", "QFP64", "QFP100",
            "LQFP48", "LQFP64", "LQFP100",
            "BGA50", "BGA144",
            "DO-214AC", "DO-214AA", "DO-214AB",
            "SMA", "SMB", "SMC",
            "LED0603",
            "USIP8"
        ]
        for p in patterns:
            if p in comp_upper:
                if p in lib:
                    return p
                for key in lib:
                    if p in key.upper():
                        return key

        sorted_keys = sorted(lib.keys(), key=len, reverse=True)
        for key in sorted_keys:
            key_upper = key.upper()
            if key_upper in comp_upper or comp_upper in key_upper:
                return key
        return None


# ---------- запуск ----------
def main():
    app = QApplication(sys.argv)
    win = FootprintEditorWindow()
    win.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()