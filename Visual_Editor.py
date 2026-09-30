# Copyright (c) 2026 Dudka & Mishutka
# Licensed under the MIT License. See LICENSE file for details.
import sys
import os
import csv
import json
import math
import re
import traceback
import subprocess

from PyQt5.QtWidgets import QGraphicsObject, QGraphicsPathItem
from PyQt5.QtGui import QPainterPath, QPen, QColor, QBrush
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QGraphicsItemGroup
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QGraphicsView,
    QGraphicsScene, QGraphicsItemGroup, QGraphicsPathItem, QGraphicsTextItem,
    QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsPixmapItem,
    QVBoxLayout, QWidget, QToolBar, QAction, QSplitter, QTableView,
    QAbstractItemView, QMenu, QLabel, QHBoxLayout, QStyledItemDelegate,
    QInputDialog, QGraphicsPolygonItem, QGraphicsLineItem,
    QDialog, QDialogButtonBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QLineEdit, QFormLayout, QSpinBox, QPushButton
)
from PyQt5.QtCore import (
    Qt, QRectF, QAbstractTableModel, QModelIndex, QVariant, QPoint, QItemSelection, QItemSelectionModel,
    qInstallMessageHandler, QPointF
)
from PyQt5.QtGui import (
    QPen, QBrush, QColor, QPainterPath, QFont, QIcon, QPixmap, QPainter, QPolygonF
)

def get_app_dir():
    """Папка, где лежит программа (.py или .exe)."""
    if getattr(sys, "frozen", False):
        # Запущено как exe (PyInstaller)
        return os.path.dirname(sys.executable)
    # Запущено как .py
    return os.path.dirname(os.path.abspath(__file__))


# -------------------- CSV helpers --------------------


def detect_delimiter(first_line: str) -> str:
    """Простейшее определение разделителя для CSV."""
    if first_line.count(";") > first_line.count(","):
        return ";"
    if "\t" in first_line:
        return "\t"
    return ","


def find_column(header, alternatives):
    """Поиск индекса столбца по возможным именам (без регистра)."""
    lower = [h.strip().lower() for h in header]
    for alt in alternatives:
        alt = alt.lower()
        if alt in lower:
            return lower.index(alt)
    return -1


# -------------------- Footprint library --------------------

LIB_FILENAME = "footprints.json"

DEFAULT_FOOTPRINT_LIBRARY = {
    "0201": {"type": "chip", "size": [0.6, 0.3], "zero_angle_tape": 0, "pins": 2},
    "0402": {"type": "chip", "size": [1.0, 0.5], "zero_angle_tape": 0, "pins": 2},
    "0603": {"type": "chip", "size": [1.6, 0.8], "zero_angle_tape": 0, "pins": 2},
    "0805": {"type": "chip", "size": [2.0, 1.25], "zero_angle_tape": 0, "pins": 2},
    "1206": {"type": "chip", "size": [3.2, 1.6], "zero_angle_tape": 0, "pins": 2},
    "1210": {"type": "chip", "size": [3.2, 2.5], "zero_angle_tape": 0, "pins": 2},

    "C0402": {"type": "chip", "size": [1.0, 0.5], "zero_angle_tape": 0, "pins": 2},
    "C0603": {"type": "chip", "size": [1.6, 0.8], "zero_angle_tape": 0, "pins": 2},
    "C0805": {"type": "chip", "size": [2.0, 1.25], "zero_angle_tape": 0, "pins": 2},
    "C1206": {"type": "chip", "size": [3.2, 1.6], "zero_angle_tape": 0, "pins": 2},

    "R0402": {"type": "chip", "size": [1.0, 0.5], "zero_angle_tape": 0, "pins": 2},
    "R0603": {"type": "chip", "size": [1.6, 0.8], "zero_angle_tape": 0, "pins": 2},
    "R0805": {"type": "chip", "size": [2.0, 1.25], "zero_angle_tape": 0, "pins": 2},
    "R1206": {"type": "chip", "size": [3.2, 1.6], "zero_angle_tape": 0, "pins": 2},

    "LED0603": {"type": "led", "size": [1.6, 0.8], "zero_angle_tape": 0, "pins": 2},

    "SOD123": {"type": "sod", "size": [3.7, 1.8], "zero_angle_tape": 0, "pins": 2},
    "SOD323": {"type": "sod", "size": [2.1, 1.3], "zero_angle_tape": 0, "pins": 2},

    "SOT23": {"type": "sot", "size": [3.0, 1.4], "zero_angle_tape": 0, "pins": 3},
    "SOT23-3": {"type": "sot", "size": [3.0, 1.4], "zero_angle_tape": 0, "pins": 3},
    "SOT23-5": {"type": "sot", "size": [2.9, 1.6], "zero_angle_tape": 0, "pins": 5},
    "SOT23-6": {"type": "sot", "size": [2.9, 1.6], "zero_angle_tape": 0, "pins": 6},
    "SOT223": {"type": "sot", "size": [6.5, 3.5], "zero_angle_tape": 0, "pins": 4},
    "SOT89": {"type": "sot", "size": [4.5, 2.5], "zero_angle_tape": 0, "pins": 3},
    "SOT323": {"type": "sot", "size": [2.0, 1.25], "zero_angle_tape": 0, "pins": 3},
    "SOT363": {"type": "sot", "size": [2.1, 2.0], "zero_angle_tape": 0, "pins": 6},
    "SOT523": {"type": "sot", "size": [1.6, 1.2], "zero_angle_tape": 0, "pins": 3},
    "SOT563": {"type": "sot", "size": [1.6, 1.6], "zero_angle_tape": 0, "pins": 6},
    "SOT343": {"type": "sot", "size": [2.0, 1.25], "zero_angle_tape": 0, "pins": 4},
    "SOT457": {"type": "sot", "size": [2.0, 2.0], "zero_angle_tape": 0, "pins": 6},
    "SOT764": {"type": "sot", "size": [2.6, 2.6], "zero_angle_tape": 0, "pins": 8},

    "SC70": {"type": "sot", "size": [2.0, 1.25], "zero_angle_tape": 0, "pins": 3},
    "SC70-3": {"type": "sot", "size": [2.0, 1.25], "zero_angle_tape": 0, "pins": 3},
    "SC70-5": {"type": "sot", "size": [2.0, 1.25], "zero_angle_tape": 0, "pins": 5},
    "SC70-6": {"type": "sot", "size": [2.0, 1.25], "zero_angle_tape": 0, "pins": 6},

    "SOIC8": {"type": "soic", "size": [4.9, 3.9], "zero_angle_tape": 0, "pins": 8},
    "SOIC14": {"type": "soic", "size": [8.7, 3.9], "zero_angle_tape": 0, "pins": 14},
    "SOIC16": {"type": "soic", "size": [10.3, 3.9], "zero_angle_tape": 0, "pins": 16},

    "SOP4": {"type": "sop", "size": [4.4, 2.8], "zero_angle_tape": 0, "pins": 4},
    "SOP8": {"type": "sop", "size": [4.9, 3.9], "zero_angle_tape": 0, "pins": 8},
    "SOP16": {"type": "sop", "size": [10.0, 4.0], "zero_angle_tape": 0, "pins": 16},

    "TSSOP8": {"type": "tssop", "size": [3.0, 4.4], "zero_angle_tape": 0, "pins": 8},
    "TSSOP14": {"type": "tssop", "size": [5.0, 4.4], "zero_angle_tape": 0, "pins": 14},
    "TSSOP20": {"type": "tssop", "size": [6.5, 4.4], "zero_angle_tape": 0, "pins": 20},

    "QFN32": {"type": "qfn", "size": [5.0, 5.0], "zero_angle_tape": 0, "pins": 32},
    "QFN48": {"type": "qfn", "size": [7.0, 7.0], "zero_angle_tape": 0, "pins": 48},
    "QFN64": {"type": "qfn", "size": [9.0, 9.0], "zero_angle_tape": 0, "pins": 64},

    "QFP32": {"type": "qfp", "size": [7.0, 7.0], "zero_angle_tape": 0, "pins": 32},
    "QFP64": {"type": "qfp", "size": [10.0, 10.0], "zero_angle_tape": 0, "pins": 64},
    "QFP100": {"type": "qfp", "size": [14.0, 14.0], "zero_angle_tape": 0, "pins": 100},

    "LQFP48": {"type": "qfp", "size": [7.0, 7.0], "zero_angle_tape": 0, "pins": 48},
    "LQFP64": {"type": "qfp", "size": [10.0, 10.0], "zero_angle_tape": 0, "pins": 64},
    "LQFP100": {"type": "qfp", "size": [14.0, 14.0], "zero_angle_tape": 0, "pins": 100},

    "BGA50": {"type": "bga", "size": [6.0, 6.0], "zero_angle_tape": 0, "pins": 50},
    "BGA144": {"type": "bga", "size": [14.0, 14.0], "zero_angle_tape": 0, "pins": 144},

    "DO-214AC": {"type": "do214", "size": [4.5, 2.6], "zero_angle_tape": 0, "pins": 2},
    "SMA": {"type": "do214", "size": [4.5, 2.6], "zero_angle_tape": 0, "pins": 2},
    "DO-214AA": {"type": "do214", "size": [4.6, 3.95], "zero_angle_tape": 0, "pins": 2},
    "SMB": {"type": "do214", "size": [4.6, 3.95], "zero_angle_tape": 0, "pins": 2},
    "DO-214AB": {"type": "do214", "size": [7.11, 6.22], "zero_angle_tape": 0, "pins": 2},
    "SMC": {"type": "do214", "size": [7.11, 6.22], "zero_angle_tape": 0, "pins": 2},

    "USIP8": {"type": "module", "size": [3.0, 2.8], "zero_angle_tape": 0, "pins": 8}
}


def get_lib_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, LIB_FILENAME)


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
            if changed:
                with open(path, "w", encoding="utf-8") as fw:
                    json.dump(data, fw, indent=2, ensure_ascii=False)
            return data
        except Exception:
            return json.loads(json.dumps(DEFAULT_FOOTPRINT_LIBRARY))
    else:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_FOOTPRINT_LIBRARY, f, indent=2, ensure_ascii=False)
        return json.loads(json.dumps(DEFAULT_FOOTPRINT_LIBRARY))


# -------------------- DXF loader (очень простой) --------------------

def load_dxf_polylines(path):
    """
    Расширенный DXF-парсер:
    - поддерживает POLYLINE / LWPOLYLINE;
    - понимает BLOCK / INSERT (вставки блоков);
    - возвращает список полилиний [(x, y), ...].
    """
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.rstrip("\n\r") for line in f]
    except Exception as e:
        print("DXF open error:", e)
        return []

    polylines = []
    blocks = {}   # имя блока -> список полилиний
    current_block = None
    current_poly = None
    inside_poly = False
    i = 0
    n = len(lines)

    while i < n - 1:
        code = lines[i].strip()
        value = lines[i + 1].strip()
        i += 2

        # --- Начало блока ---
        if code == "0" and value == "BLOCK":
            current_block = {"name": None, "polys": []}

        elif current_block is not None and code == "2" and not current_block["name"]:
            current_block["name"] = value

        elif code == "0" and value == "ENDBLK":
            if current_block and current_block["name"]:
                blocks[current_block["name"]] = current_block["polys"]
            current_block = None

        # --- Полилинии (внутри блока или вне его) ---
        elif code == "0" and value in ("POLYLINE", "LWPOLYLINE"):
            if current_poly:
                if current_block:
                    current_block["polys"].append(current_poly)
                else:
                    polylines.append(current_poly)
            current_poly = []
            inside_poly = True

        elif code == "0" and value in ("SEQEND", "ENDSEC"):
            if current_poly:
                if current_block:
                    current_block["polys"].append(current_poly)
                else:
                    polylines.append(current_poly)
                current_poly = []
            inside_poly = False

        elif inside_poly and code == "10":
            try:
                x = float(value)
            except ValueError:
                continue
            y = 0.0
            if i < n - 1 and lines[i].strip() == "20":
                try:
                    y = float(lines[i + 1].strip())
                    i += 2
                except ValueError:
                    y = 0.0
            current_poly.append((x, y))

        # --- Вставка блока (INSERT) ---
        elif code == "0" and value == "INSERT":
            block_name = None
            insert_x = insert_y = 0.0
            scale_x = scale_y = 1.0
            rotation = 0.0

            # читаем параметры вставки
            while i < n - 1:
                c2 = lines[i].strip()
                v2 = lines[i + 1].strip()
                i += 2
                if c2 == "2":
                    block_name = v2
                elif c2 == "10":
                    try:
                        insert_x = float(v2)
                    except ValueError:
                        pass
                elif c2 == "20":
                    try:
                        insert_y = float(v2)
                    except ValueError:
                        pass
                elif c2 == "41":
                    scale_x = float(v2)
                elif c2 == "42":
                    scale_y = float(v2)
                elif c2 == "50":
                    rotation = float(v2)
                elif c2 == "0":
                    i -= 2
                    break

            if block_name and block_name in blocks:
                # вставляем все полилинии блока со сдвигом
                for poly in blocks[block_name]:
                    new_poly = []
                    for (x, y) in poly:
                        # применяем масштаб и поворот
                        xr = x * scale_x
                        yr = y * scale_y
                        if rotation != 0.0:
                            import math
                            angle = math.radians(rotation)
                            xr, yr = (
                                xr * math.cos(angle) - yr * math.sin(angle),
                                xr * math.sin(angle) + yr * math.cos(angle),
                            )
                        new_poly.append((xr + insert_x, yr + insert_y))
                    polylines.append(new_poly)

    # добавим последнюю полилинию, если осталась
    if current_poly:
        if current_block:
            current_block["polys"].append(current_poly)
        else:
            polylines.append(current_poly)

    return polylines


# -------------------- Graphics view with zoom & bottom view --------------------


class BoardView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        # Убираем ScrollHandDrag и будем управлять перетаскиванием вручную
        self.setDragMode(QGraphicsView.NoDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.scale_factor = 1.0
        self.setCursor(Qt.ArrowCursor)
        self.zoom_enabled = False
        # Ссылка на загруженный DXF-объект (нужна для Ctrl + колесо)
        self.dxf_item = None

        # Переменные для ручного перетаскивания
        self._is_dragging = False
        self._drag_start_pos = QPoint()

    def wheelEvent(self, event):
        # --- Ctrl + колесо: масштаб ТОЛЬКО у DXF ---
        if (event.modifiers() & Qt.ControlModifier) and self.dxf_item is not None \
                and self.dxf_item.scene() is not None:
            delta = event.angleDelta().y()
            if delta == 0:
                event.accept()
                return
            factor = 1.1 if delta > 0 else 1.0 / 1.1
            new_scale = self.dxf_item.scale() * factor
            # Ограничиваем разумными пределами
            if new_scale < 0.05:
                new_scale = 0.05
            if new_scale > 20.0:
                new_scale = 20.0
            self.dxf_item.setScale(new_scale)
            print(f"[DXF] Scale by Ctrl+wheel: {new_scale:.3f}")
            event.accept()
            return

        # --- Обычное колесо: зум всей сцены ---
        if not self.zoom_enabled:
            event.ignore()
            return
        angle = event.angleDelta().y()
        if angle > 0:
            factor = 1.1
        else:
            factor = 1.0 / 1.1
        self.scale_factor *= factor
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Начинаем перетаскивание при нажатии левой кнопки
            self._is_dragging = True
            self._drag_start_pos = event.pos()
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_dragging:
            # Вычисляем смещение и перемещаем view
            delta = event.pos() - self._drag_start_pos
            self._drag_start_pos = event.pos()

            # Получаем текущие значения горизонтального и вертикального скролла
            h_scroll = self.horizontalScrollBar()
            v_scroll = self.verticalScrollBar()

            # Обновляем позиции скроллбаров
            h_scroll.setValue(h_scroll.value() - delta.x())
            v_scroll.setValue(v_scroll.value() - delta.y())

            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._is_dragging:
            # Заканчиваем перетаскивание
            self._is_dragging = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def reset_view(self, rect: QRectF):
        self.resetTransform()
        self.scale_factor = 1.0
        if not rect.isNull():
            self.fitInView(rect, Qt.KeepAspectRatio)


# -------------------- Component item --------------------


class ComponentItem(QGraphicsItemGroup):
    def __init__(
            self, editor, row_index, designator, comp_name, footprint,
            x_mm, y_mm, rotation_deg, pkg_info, scale_factor,
            dxf_paths=None, bottom_view=False
    ):
        super().__init__()
        self.editor = editor
        self.row_index = row_index
        self.designator = designator
        self.comp_name = comp_name
        self.footprint = footprint
        self.scale_factor = scale_factor
        self.pkg_info = pkg_info or {}
        self.dxf_paths = dxf_paths or []
        self.bottom_view = bottom_view

        # Сохраняем исходные координаты
        self.original_x_mm = x_mm
        self.original_y_mm = y_mm

        # Применяем инвертацию X если включен bottom_view
        if bottom_view:
            self.display_x_mm = -x_mm
        else:
            self.display_x_mm = x_mm

        # Инвертируем Y для отображения в Qt системе координат
        self.display_y_mm = -y_mm

        # csv rotation
        self.csv_rotation = rotation_deg
        self.lib_angle = float(self.pkg_info.get("zero_angle_tape", 0.0)) if self.pkg_info else 0.0

        # построить геометрию
        size = self.pkg_info.get("size", [1.0, 0.5])
        self.width_mm = float(size[0]) if size else 1.0
        self.height_mm = float(size[1]) if size else 0.5

        self.rebuild_geometry()

        # текст с designator (независимый от трансформаций)
        self._build_designator_label()

        self.setPos(self.display_x_mm * scale_factor, self.display_y_mm * scale_factor)
        visual_angle = -self.csv_rotation
        self.setRotation(visual_angle + self.lib_angle)
        self.setFlag(QGraphicsItemGroup.ItemIsSelectable, True)
        self.setFiltersChildEvents(True)
        self.update_tooltip()

    def rebuild_geometry(self):
        """Перестроить геометрию компонента (удалить старую и создать новую)."""
        # Удаляем все дочерние элементы (геометрию)
        for child in self.childItems():
            child.setParentItem(None)
            if child.scene():
                child.scene().removeItem(child)
        # Воссоздаём геометрию на основе текущих параметров
        if self.pkg_info and self.pkg_info.get("shapes"):
            self._build_shape_from_manual_shapes(self.pkg_info["shapes"])
        elif self.dxf_paths:
            self._build_shape_from_dxf(self.dxf_paths, self.width_mm, self.height_mm)
        else:
            self._build_shape_from_library(self.width_mm, self.height_mm)

    # ----- geometry builders -----

    def _build_designator_label(self):
        # Создаем текст как отдельный элемент сцены, не как дочерний
        self.text_item = QGraphicsTextItem()
        self.text_item.setPlainText(self.designator or "")
        font = QFont()
        font.setPointSize(4)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(Qt.darkBlue)

        # Вычисляем глобальные координаты для текста
        self.update_text_position()

        self.text_item.setZValue(2.0)

        # Добавляем текст на сцену через редактор
        if self.editor and self.editor.scene:
            self.editor.scene.addItem(self.text_item)

    def update_text_position(self):
        """Обновить позицию текста в глобальных координатах"""
        if not hasattr(self, 'text_item'):
            return

        text_rect = self.text_item.boundingRect()
        text_width = text_rect.width()
        text_height = text_rect.height()

        # Глобальные координаты центра компонента (с учетом bottom_view)
        if self.bottom_view:
            center_x = -self.original_x_mm * self.scale_factor
        else:
            center_x = self.original_x_mm * self.scale_factor

        center_y = self.display_y_mm * self.scale_factor

        # Обычная позиция - по центру
        text_x = center_x - text_width / 2
        text_y = center_y - text_height / 2

        self.text_item.setPos(text_x, text_y)

    def update_bottom_view(self, bottom_view_enabled):
        """Обновить отображение для bottom view (инвертация X)"""
        self.bottom_view = bottom_view_enabled

        if bottom_view_enabled:
            self.display_x_mm = -self.original_x_mm
        else:
            self.display_x_mm = self.original_x_mm

        self.setPos(self.display_x_mm * self.scale_factor, self.display_y_mm * self.scale_factor)
        self.update_text_position()

    def update_rotation(self, new_csv_rotation=None):
        """Обновить поворот компонента и позицию текста"""
        if new_csv_rotation is not None:
            self.csv_rotation = new_csv_rotation
            # Инвертируем угол для визуального отображения
            visual_angle = -self.csv_rotation
            self.setRotation(visual_angle + self.lib_angle)
        # Текст всегда остается без поворота и в правильной позиции
        self.update_text_position()

    def remove_from_scene(self):
        """Удалить компонент и его текст со сцены"""
        if hasattr(self, 'text_item') and self.text_item.scene():
            self.scene().removeItem(self.text_item)
        if self.scene():
            self.scene().removeItem(self)

    def _build_shape_from_manual_shapes(self, shapes):
        sf = self.scale_factor
        for sh in shapes:
            kind = sh.get("kind")
            if kind in ("body", "pad"):
                w = float(sh.get("w", 0.0)) * sf
                h = float(sh.get("h", 0.0)) * sf
                x = float(sh.get("x", 0.0)) * sf
                y = float(sh.get("y", 0.0)) * sf
    
                if kind == "body":
                    path = self._create_body_path(w, h, sh)
                else:  # pad
                    rect = QRectF(-w / 2, -h / 2, w, h)
                    path = QPainterPath()
                    path.addRect(rect)
    
                item = QGraphicsPathItem(path, self)
                item.setPos(x, y)
                color = QColor(30, 144, 255) if kind == "body" else QColor(0, 120, 220)
                item.setPen(QPen(color))
                item.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 80)))
                item.setZValue(0.5 if kind == "pad" else 0.0)

            elif kind == "pin1":
                r = float(sh.get("r", 0.3)) * sf
                x = float(sh.get("x", 0.0)) * sf
                y = float(sh.get("y", 0.0)) * sf
                circ = QGraphicsEllipseItem(-r, -r, 2 * r, 2 * r, self)
                circ.setPos(x, y)
                circ.setBrush(QBrush(QColor(255, 80, 80)))
                circ.setPen(QPen(QColor(255, 80, 80)))
                circ.setZValue(1.5)

            elif kind == "diode":
                w = float(sh.get("w", 0.0)) * sf
                h = float(sh.get("h", 0.0)) * sf
                x = float(sh.get("x", 0.0)) * sf
                y = float(sh.get("y", 0.0)) * sf

                # Треугольник
                tri_points = [
                    QPointF(-w/2, -h/2),
                    QPointF(-w/2,  h/2),
                    QPointF( w/2,  0.0)
                ]
                tri_polygon = QPolygonF(tri_points)
                tri_item = QGraphicsPolygonItem(tri_polygon, self)
                tri_item.setPos(x, y)
                color = QColor(255, 140, 0)   # оранжевый
                tri_item.setPen(QPen(color))
                tri_item.setBrush(QBrush(color))
                tri_item.setZValue(1.0)

                # Катодная линия (вертикальная полоска справа)
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
                line_poly = QPolygonF(line_points)
                line_item = QGraphicsPolygonItem(line_poly, self)
                line_item.setPos(x, y)
                line_item.setPen(QPen(color))
                line_item.setBrush(QBrush(color))
                line_item.setZValue(1.0)

                # Осевая линия
                line_start_x = -w
                line_end_x = w
                axis_line = QGraphicsLineItem(line_start_x, 0.0, line_end_x, 0.0, self)
                axis_line.setPos(x, y)
                axis_line.setPen(QPen(color, 1))
                axis_line.setZValue(1.0)

            elif kind == "stripe":
                w = float(sh.get("w", 0.5)) * sf
                h = float(sh.get("h", 0.2)) * sf
                x = float(sh.get("x", 0.0)) * sf
                y = float(sh.get("y", 0.0)) * sf
                rect = QRectF(-w / 2, -h / 2, w, h)
                stripe = QGraphicsRectItem(rect, self)
                stripe.setPos(x, y)
                stripe.setPen(QPen(QColor(0, 0, 0)))
                stripe.setBrush(QBrush(QColor(0, 0, 0)))
                stripe.setZValue(1.8)
                angle = float(sh.get("angle", 0.0))
                if angle:
                    stripe.setRotation(angle)

            elif kind == "polarity_sign":
                w = float(sh.get("w", 0.6)) * sf
                h = float(sh.get("h", 0.6)) * sf
                x = float(sh.get("x", 0.0)) * sf
                y = float(sh.get("y", 0.0)) * sf
                sign = sh.get("sign", "+")
                thickness = max(1.0, min(w, h) * 0.18)

                h_bar = QGraphicsRectItem(-w / 2, -thickness / 2, w, thickness, self)
                h_bar.setPos(x, y)
                h_bar.setPen(QPen(Qt.NoPen))
                h_bar.setBrush(QBrush(QColor(0, 0, 0)))
                h_bar.setZValue(2.0)

                if sign == "+":
                    v_bar = QGraphicsRectItem(-thickness / 2, -h / 2,
                                              thickness, h, self)
                    v_bar.setPos(x, y)
                    v_bar.setPen(QPen(Qt.NoPen))
                    v_bar.setBrush(QBrush(QColor(0, 0, 0)))
                    v_bar.setZValue(2.0)

    def _create_body_path(self, w, h, shape_dict):
        """Создать QPainterPath для тела корпуса с учётом скруглений/срезов."""
        # w и h уже масштабированы
        rect = QRectF(-w/2, -h/2, w, h)
    
        # Проверяем наличие индивидуальных углов
        corners = shape_dict.get("corners", {})
        if corners:
            # Индивидуальные углы (приоритет над общими)
            tl_r = corners.get("tl", {}).get("radius", 0.0) * self.scale_factor
            tl_c = corners.get("tl", {}).get("chamfer", 0.0) * self.scale_factor
            tr_r = corners.get("tr", {}).get("radius", 0.0) * self.scale_factor
            tr_c = corners.get("tr", {}).get("chamfer", 0.0) * self.scale_factor
            bl_r = corners.get("bl", {}).get("radius", 0.0) * self.scale_factor
            bl_c = corners.get("bl", {}).get("chamfer", 0.0) * self.scale_factor
            br_r = corners.get("br", {}).get("radius", 0.0) * self.scale_factor
            br_c = corners.get("br", {}).get("chamfer", 0.0) * self.scale_factor

            # Ограничиваем максимальным значением
            max_w = w / 2
            max_h = h / 2
            tl_r = min(tl_r, max_w, max_h)
            tr_r = min(tr_r, max_w, max_h)
            bl_r = min(bl_r, max_w, max_h)
            br_r = min(br_r, max_w, max_h)
            tl_c = min(tl_c, max_w, max_h)
            tr_c = min(tr_c, max_w, max_h)
            bl_c = min(bl_c, max_w, max_h)
            br_c = min(br_c, max_w, max_h)

            path = QPainterPath()
            # Верхняя сторона
            start_x = rect.left() + (tl_r if tl_r > 0 else tl_c)
            path.moveTo(start_x, rect.top())
            end_x = rect.right() - (tr_r if tr_r > 0 else tr_c)
            path.lineTo(end_x, rect.top())
            # Правый верхний угол
            if tr_r > 0:
                path.arcTo(rect.right() - 2*tr_r, rect.top(), 2*tr_r, 2*tr_r, 90, -90)
            elif tr_c > 0:
                path.lineTo(rect.right(), rect.top() + tr_c)
            else:
                path.lineTo(rect.right(), rect.top())
            # Правая сторона
            end_y = rect.bottom() - (br_r if br_r > 0 else br_c)
            path.lineTo(rect.right(), end_y)
            # Правый нижний угол
            if br_r > 0:
                path.arcTo(rect.right() - 2*br_r, rect.bottom() - 2*br_r, 2*br_r, 2*br_r, 0, -90)
            elif br_c > 0:
                path.lineTo(rect.right() - br_c, rect.bottom())
            else:
                path.lineTo(rect.right(), rect.bottom())
            # Нижняя сторона
            start_x = rect.left() + (bl_r if bl_r > 0 else bl_c)
            path.lineTo(start_x, rect.bottom())
            # Левый нижний угол
            if bl_r > 0:
                path.arcTo(rect.left(), rect.bottom() - 2*bl_r, 2*bl_r, 2*bl_r, -90, -90)
            elif bl_c > 0:
                path.lineTo(rect.left(), rect.bottom() - bl_c)
            else:
                path.lineTo(rect.left(), rect.bottom())
            # Левая сторона
            start_y = rect.top() + (tl_r if tl_r > 0 else tl_c)
            path.lineTo(rect.left(), start_y)
            # Левый верхний угол
            if tl_r > 0:
                path.arcTo(rect.left(), rect.top(), 2*tl_r, 2*tl_r, 180, -90)
            elif tl_c > 0:
                path.lineTo(rect.left() + tl_c, rect.top())
            else:
                path.lineTo(rect.left(), rect.top())
            path.closeSubpath()
            return path
        else:
            # Общие настройки
            radius = shape_dict.get("corner_radius", 0.0) * self.scale_factor
            chamfer = shape_dict.get("chamfer", 0.0) * self.scale_factor
            if radius > 0:
                path = QPainterPath()
                path.addRoundedRect(rect, radius, radius)
                return path
            elif chamfer > 0:
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

    def _build_shape_from_library(self, width_mm, height_mm):
        sf = self.scale_factor
        w = width_mm * sf
        h = height_mm * sf
        rect = QRectF(-w / 2, -h / 2, w, h)
        path = QPainterPath()
        path.addRect(rect)
        body = QGraphicsPathItem(path, self)
        body.setPen(QPen(QColor(30, 144, 255)))
        body.setBrush(QBrush(QColor(30, 144, 255, 40)))
        body.setZValue(0.0)

        pkg_type = (self.pkg_info.get("type") or "chip").lower()
        pins = int(self.pkg_info.get("pins", 2))

        if pkg_type in ("chip", "led", "sod", "do214"):
            pad_len = w * 0.2
            pad_th = h * 0.5
            for side in (-1, 1):
                if side < 0:
                    x0 = -w / 2 - pad_len
                    x1 = -w / 2
                else:
                    x0 = w / 2
                    x1 = w / 2 + pad_len
                y0 = -pad_th / 2
                y1 = pad_th / 2
                leg_rect = QRectF(x0, y0, x1 - x0, y1 - y0)
                leg_path = QPainterPath()
                leg_path.addRect(leg_rect)
                leg = QGraphicsPathItem(leg_path, self)
                leg.setPen(QPen(QColor(30, 144, 255)))
                leg.setBrush(QBrush(QColor(30, 144, 255, 80)))
                leg.setZValue(0.5)

        elif pkg_type in ("soic", "sop", "tssop"):
            total_pins = pins
            pins_each_side = max(total_pins // 2, 1)
            pad_len = h * 0.3
            pad_th = w / (pins_each_side * 3.0)
            for side in ("top", "bottom"):
                for i in range(pins_each_side):
                    tx = -w / 2 + (i + 1) * (w / (pins_each_side + 1))
                    if side == "top":
                        y0 = h / 2
                        y1 = h / 2 + pad_len
                    else:
                        y0 = -h / 2 - pad_len
                        y1 = -h / 2
                    x0 = tx - pad_th / 2
                    x1 = tx + pad_th / 2
                    leg_rect = QRectF(x0, y0, x1 - x0, y1 - y0)
                    leg_path = QPainterPath()
                    leg_path.addRect(leg_rect)
                    leg = QGraphicsPathItem(leg_path, self)
                    leg.setPen(QPen(QColor(30, 144, 255)))
                    leg.setBrush(QBrush(QColor(30, 144, 255, 80)))
                    leg.setZValue(0.5)

        elif pkg_type in ("qfp", "qfn"):
            total_pins = pins
            pins_side = max(total_pins // 4, 1)
            pad_len = min(w, h) * 0.15
            pad_th = min(w, h) / (pins_side * 3.0)
            sides = ("top", "right", "bottom", "left")
            for side in sides:
                for i in range(pins_side):
                    if side in ("top", "bottom"):
                        tx = -w / 2 + (i + 1) * (w / (pins_side + 1))
                        if side == "top":
                            y0 = h / 2
                            y1 = h / 2 + pad_len
                        else:
                            y0 = -h / 2 - pad_len
                            y1 = -h / 2
                        x0 = tx - pad_th / 2
                        x1 = tx + pad_th / 2
                    else:
                        ty = -h / 2 + (i + 1) * (h / (pins_side + 1))
                        if side == "right":
                            x0 = w / 2
                            x1 = w / 2 + pad_len
                        else:
                            x0 = -w / 2 - pad_len
                            x1 = -w / 2
                        y0 = ty - pad_th / 2
                        y1 = ty + pad_th / 2
                    leg_rect = QRectF(x0, y0, x1 - x0, y1 - y0)
                    leg_path = QPainterPath()
                    leg_path.addRect(leg_rect)
                    leg = QGraphicsPathItem(leg_path, self)
                    leg.setPen(QPen(QColor(30, 144, 255)))
                    leg.setBrush(QBrush(QColor(30, 144, 255, 80)))
                    leg.setZValue(0.5)

        # pin1 marker
        pin1_radius = min(w, h) * 0.15
        cx = -w / 2 + pin1_radius * 1.4
        cy = h / 2 - pin1_radius * 1.4
        pin1 = QGraphicsEllipseItem(-pin1_radius, -pin1_radius,
                                    2 * pin1_radius, 2 * pin1_radius, self)
        pin1.setPos(cx, cy)
        pin1.setPen(QPen(QColor(255, 80, 80)))
        pin1.setBrush(QBrush(QColor(255, 80, 80)))
        pin1.setZValue(1.5)

    def _build_shape_from_dxf(self, paths, width_mm, height_mm):
        sf = self.scale_factor
        color = QColor(0, 120, 220)
        for poly in paths:
            if len(poly) < 2:
                continue
            path = QPainterPath()
            x0, y0 = poly[0]
            path.moveTo(x0 * sf, y0 * sf)
            for (x, y) in poly[1:]:
                path.lineTo(x * sf, y * sf)
            path.closeSubpath()
            item = QGraphicsPathItem(path, self)
            item.setPen(QPen(color))
            item.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 40)))
            item.setZValue(0.0)

    # ----- misc -----

    def mousePressEvent(self, event):
        """Обработчик клика по компоненту на сцене"""
        if self.editor:
            self.editor.select_component_in_table(self)
        super().mousePressEvent(event)

    def update_tooltip(self):
        tt = (
            f"{self.designator}\n"
            f"Component: {self.comp_name}\n"
            f"Footprint: {self.footprint}\n"
            f"Rotation (CSV): {self.csv_rotation:.1f}°\n"
            f"Lib zero angle: {self.lib_angle:.1f}°\n"
            f"Bottom view: {self.bottom_view}"
        )
        self.setToolTip(tt)

    def contextMenuEvent(self, event):
        menu = QMenu()
        rotate_left = menu.addAction("Повернуть на 90°")  # +90
        rotate_right = menu.addAction("Повернуть на -90°")  # -90
        rotate_180 = menu.addAction("Повернуть на 180°")
        set_angle = menu.addAction("Задать угол…")
        assign_fp = menu.addAction("Назначить корпус из библиотеки…")
        res = menu.exec_(event.screenPos())
        if res == rotate_left:
            self.editor.change_component_rotation(self, self.csv_rotation + 90.0)
        elif res == rotate_right:
            self.editor.change_component_rotation(self, self.csv_rotation - 90.0)
        elif res == rotate_180:
            self.editor.change_component_rotation(self, self.csv_rotation + 180.0)
        elif res == set_angle:
            angle, ok = QInputDialog.getDouble(
                None, "Угол", "Rotation, ° (по часовой = отрицательный):",
                self.csv_rotation, -360.0, 360.0, 2
            )
            if ok:
                self.editor.change_component_rotation(self, angle)
        elif res == assign_fp:
            self.editor.assign_footprint_to_component(self)


# -------------------- Table model --------------------


class CsvTableModel(QAbstractTableModel):
    def __init__(self, header, rows, parent=None):
        super().__init__(parent)
        self.header = header
        self.rows = rows

    def rowCount(self, parent=QModelIndex()):
        return len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return len(self.header)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        row = index.row()
        col = index.column()
        if row >= len(self.rows) or col >= len(self.header):
            return QVariant()
        value = self.rows[row][col]
        if role in (Qt.DisplayRole, Qt.EditRole):
            return value
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if 0 <= section < len(self.header):
                return self.header[section]
        else:
            return section + 1
        return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole or not index.isValid():
            return False
        row = index.row()
        col = index.column()
        if row >= len(self.rows) or col >= len(self.header):
            return False
        self.rows[row][col] = str(value)
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
        return True

    def update_all(self):
        self.layoutChanged.emit()


class RotationDelegate(QStyledItemDelegate):
    """Чтобы отлавливать изменение Rotation."""

    def __init__(self, mainwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mainwindow = mainwindow

    def setModelData(self, editor, model, index):
        super().setModelData(editor, model, index)
        self.mainwindow.update_component_rotation_from_table(index)

class DXFItemGroup(QGraphicsItemGroup):
    """Интерактивная DXF-группа с ручным масштабом и перемещением."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItemGroup.ItemIsMovable, True)
        self.setFlag(QGraphicsItemGroup.ItemIsSelectable, True)
        self.setFlag(QGraphicsItemGroup.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)
        self.scale_factor = 1.0

    def wheelEvent(self, event):
        """Игнорируем событие колеса мыши – масштабирование DXF только с клавиатуры."""
        # Убрано масштабирование при Ctrl+колесо.
        event.ignore()

class InteractiveDXF(QGraphicsObject):
    """Полностью интерактивный DXF-объект: можно перемещать и масштабировать."""
    def keyPressEvent(self, event):
        """Обработка Ctrl + '+' / '-' для масштабирования DXF."""
        if hasattr(self, "board_dxf_item") and self.board_dxf_item:
            if event.modifiers() & Qt.ControlModifier:
                key = event.key()

                # --- инициализируем масштаб, если ещё не создан ---
                if not hasattr(self, "dxf_scale_factor"):
                    self.dxf_scale_factor = self.board_dxf_item.scale() if self.board_dxf_item else 1.0

                # --- обработка клавиш ---
                if key in (Qt.Key_Plus, Qt.Key_Equal):
                    self.dxf_scale_factor *= 1.02
                    self.board_dxf_item.setScale(self.dxf_scale_factor)
                    print(f"[DXF] Scale increased: {self.dxf_scale_factor:.2f}")
                    event.accept()
                    return

                elif key in (Qt.Key_Minus, Qt.Key_Underscore):
                    self.dxf_scale_factor /= 1.02
                    self.board_dxf_item.setScale(self.dxf_scale_factor)
                    print(f"[DXF] Scale decreased: {self.dxf_scale_factor:.2f}")
                    event.accept()
                    return

                elif key == Qt.Key_0:
                    self.dxf_scale_factor = 1.0
                    self.board_dxf_item.setScale(self.dxf_scale_factor)
                    print(f"[DXF] Scale reset to 1.00")
                    event.accept()
                    return

        # передаём событие дальше, если не наши клавиши
        super().keyPressEvent(event)

    def __init__(self, polylines, color=QColor(140, 140, 140), scale=25.4, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsObject.ItemIsFocusable, True)
        self.paths = []
        self.scale_factor = 1.0
        self.color = color
        self.scale_base = scale
        self._is_dragging = False
        self._drag_start = None
        self.setFlags(
            QGraphicsObject.ItemIsMovable
            | QGraphicsObject.ItemIsSelectable
            | QGraphicsObject.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)

        for poly in polylines:
            if len(poly) < 2:
                continue
            path = QPainterPath()
            x0, y0 = poly[0]
            path.moveTo(x0 * scale, -y0 * scale)
            for (x, y) in poly[1:]:
                path.lineTo(x * scale, -y * scale)
            if abs(poly[0][0] - poly[-1][0]) < 1e-6 and abs(poly[0][1] - poly[-1][1]) < 1e-6:
                path.closeSubpath()

            item = QGraphicsPathItem(path, self)
            pen = QPen(color, 3)
            pen.setCosmetic(True)
            item.setPen(pen)
            item.setBrush(QBrush(Qt.NoBrush))
            item.setOpacity(1)
            self.paths.append(item)

        self.update_bounding_rect()

    def update_bounding_rect(self):
        rect = QRectF()
        for item in self.paths:
            rect = rect.united(item.boundingRect().translated(item.pos()))
        self._bounding_rect = rect

    def boundingRect(self):
        return self._bounding_rect

    def paint(self, painter, option, widget):
        # не рисуем вручную, всё делают path items
        pass

    def wheelEvent(self, event):
        """Передаём событие колеса мыши в виджет (стандартный зум сцены)."""
        # Блок, отвечающий за масштабирование DXF при Ctrl+колесо, удалён.
        # Теперь событие всегда передаётся в BoardView для масштабирования всей сцены.
        super().wheelEvent(event)

# -------------------- CSV import dialog --------------------


class CsvImportDialog(QDialog):
    """Диалог универсального импорта CSV:
       выбор кодировки, разделителя, пропуска строк и маппинга столбцов."""

    FIELD_DEFS = [
        ("comp_name",  "Component Name", True),
        ("designator", "Designator",     True),
        ("x",          "X (мм)",         True),
        ("y",          "Y (мм)",         True),
        ("rotation",   "Rotation",       True),
        ("footprint",  "Footprint",      False),
        ("comment",    "Comment",        False),
        ("layer",      "Layer",          False),
    ]

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
        self.setWindowTitle("Импорт CSV")
        self.resize(960, 740)

        self.file_path = file_path
        self.raw_data = None
        self.column_combos = {}   # field_name -> QComboBox

        layout = QVBoxLayout(self)

        # ---------- Заголовок с именем файла ----------
        lbl_file = QLabel(f"<b>Файл:</b> {os.path.basename(file_path)}")
        lbl_file.setWordWrap(True)
        layout.addWidget(lbl_file)

        # ---------- Параметры чтения ----------
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

        # ---------- Превью ----------
        layout.addWidget(QLabel(
            "Превью (первая не пропущенная строка считается заголовком, показана жирным):"
        ))
        self.table_preview = QTableWidget()
        self.table_preview.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_preview.setSelectionMode(QTableWidget.NoSelection)
        self.table_preview.setAlternatingRowColors(True)
        self.table_preview.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_preview.setMinimumHeight(260)
        layout.addWidget(self.table_preview)

        # ---------- Маппинг столбцов ----------
        layout.addWidget(QLabel("Назначение столбцов (поля со звёздочкой обязательны):"))
        map_form = QFormLayout()
        for field_name, label, required in self.FIELD_DEFS:
            combo = QComboBox()
            self.column_combos[field_name] = combo
            star = " *" if required else ""
            map_form.addRow(f"{label}{star}:", combo)
        layout.addLayout(map_form)

        # ---------- Нижний ряд кнопок ----------
        bottom_row = QHBoxLayout()
        self.btn_load_map = QPushButton("Загрузить маппинг…")
        self.btn_save_map = QPushButton("Сохранить маппинг…")
        bottom_row.addWidget(self.btn_load_map)
        bottom_row.addWidget(self.btn_save_map)
        bottom_row.addStretch(1)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bottom_row.addWidget(btn_box)
        layout.addLayout(bottom_row)

        # ---------- Сигналы ----------
        self.combo_encoding.currentIndexChanged.connect(self._reload)
        self.combo_delim.currentIndexChanged.connect(self._on_delim_changed)
        self.edit_custom_delim.editingFinished.connect(self._reload)
        self.spin_skip.valueChanged.connect(self._reload)
        self.btn_reload.clicked.connect(self._reload)
        self.btn_load_map.clicked.connect(self._load_mapping)
        self.btn_save_map.clicked.connect(self._save_mapping)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)

        # ---------- Первичная загрузка ----------
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
        # Сохраняем текущий маппинг как имена столбцов (для восстановления)
        old_mapping_by_name = {}
        if self.raw_data is not None:
            old_mapping_by_name = self._collect_mapping_by_name()

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
        self._populate_column_combos(header)

        if old_mapping_by_name:
            restored = {}
            for field, name in old_mapping_by_name.items():
                idx = -1
                for i, h in enumerate(header):
                    if h.strip() == name:
                        idx = i
                        break
                restored[field] = idx
            self._apply_mapping(restored)
        else:
            auto = self._auto_match(header)
            self._apply_mapping(auto)

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

    def _populate_column_combos(self, header):
        for field_name, combo in self.column_combos.items():
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("-- не использовать --", -1)
            for i, h in enumerate(header):
                combo.addItem(f"#{i}: {h}", i)
            combo.blockSignals(False)

    def _auto_match(self, header):
        return {
            "comp_name":  find_column(header, ["CN", "component_name", "name",
                                               "description", "Component Name"]),
            "designator": find_column(header, ["designator", "refdes", "ref", "id"]),
            "x":          find_column(header, ["center-x(mm)", "x", "coord-x",
                                               "posx"]),
            "y":          find_column(header, ["center-y(mm)", "y", "coord-y",
                                               "posy"]),
            "rotation":   find_column(header, ["rotation", "angle", "rot"]),
            "footprint":  find_column(header, ["footprint", "package"]),
            "comment":    find_column(header, ["comment", "description"]),
            "layer":      find_column(header, ["layer"]),
        }

    def _apply_mapping(self, mapping):
        for field, combo in self.column_combos.items():
            idx = mapping.get(field, -1)
            if idx is None:
                idx = -1
            combo.blockSignals(True)
            found = False
            if idx >= 0:
                for i in range(combo.count()):
                    if combo.itemData(i) == idx:
                        combo.setCurrentIndex(i)
                        found = True
                        break
            if not found:
                combo.setCurrentIndex(0)
            combo.blockSignals(False)

    def _collect_mapping(self):
        return {f: c.currentData() for f, c in self.column_combos.items()}

    def _collect_mapping_by_name(self):
        """Собрать маппинг {field: header_name}, используя текущие значения combo."""
        result = {}
        if self.raw_data is None:
            return result
        skip = self.spin_skip.value()
        if skip >= len(self.raw_data):
            return result
        header = self.raw_data[skip]
        for field, combo in self.column_combos.items():
            idx = combo.currentData()
            if idx is not None and idx >= 0 and idx < len(header):
                result[field] = header[idx]
        return result

    def _validate(self):
        mapping = self._collect_mapping()
        missing = []
        used = {}
        for field, label, required in self.FIELD_DEFS:
            idx = mapping.get(field, -1)
            if idx is None:
                idx = -1
            if required and idx < 0:
                missing.append(f"{label} — не выбран столбец")
                continue
            if idx >= 0:
                if idx in used and required:
                    missing.append(f"{label} — тот же столбец, что и «{used[idx]}»")
                else:
                    used[idx] = label
        if missing:
            QMessageBox.warning(
                self, "Не все обязательные поля заданы",
                "Исправьте следующее:\n\n • " + "\n • ".join(missing)
            )
            return False
        return True

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
        if not self._validate():
            return
        super().accept()

    def get_result(self):
        return {
            "delimiter":  self._get_delimiter(),
            "encoding":   self.combo_encoding.currentData(),
            "skip_lines": self.spin_skip.value(),
            "raw_data":   self.raw_data,
            "column_map": self._collect_mapping(),
        }

    # ---------- сохранение / загрузка маппинга ----------

    def _save_mapping(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить маппинг", "",
            "Mapping files (*.json);;All files (*)"
        )
        if not path:
            return
        if not path.lower().endswith(".json"):
            path += ".json"
        payload = {
            "delimiter":        self.combo_delim.currentData(),
            "custom_delimiter": self.edit_custom_delim.text(),
            "encoding":         self.combo_encoding.currentData(),
            "skip_lines":       self.spin_skip.value(),
            "columns":          self._collect_mapping_by_name(),
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Сохранено",
                                    f"Маппинг сохранён:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось сохранить маппинг:\n{e}")

    def _load_mapping(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Загрузить маппинг", "",
            "Mapping files (*.json);;All files (*)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось прочитать маппинг:\n{e}")
            return

        delim        = payload.get("delimiter", ";")
        custom_delim = payload.get("custom_delimiter", "")
        encoding     = payload.get("encoding", "utf-8")
        skip         = int(payload.get("skip_lines", 0))
        columns_by_name = payload.get("columns", {})

        # кодировка
        i = self.combo_encoding.findData(encoding)
        if i >= 0:
            self.combo_encoding.blockSignals(True)
            self.combo_encoding.setCurrentIndex(i)
            self.combo_encoding.blockSignals(False)

        # разделитель
        presets = [d for d, _ in self.DELIMITER_PRESETS]
        if delim in presets:
            i = self.combo_delim.findData(delim)
            if i >= 0:
                self.combo_delim.blockSignals(True)
                self.combo_delim.setCurrentIndex(i)
                self.combo_delim.blockSignals(False)
        else:
            i = self.combo_delim.findData(self.CUSTOM_DELIM)
            if i >= 0:
                self.combo_delim.blockSignals(True)
                self.combo_delim.setCurrentIndex(i)
                self.combo_delim.blockSignals(False)
            self.edit_custom_delim.setText(custom_delim or delim)
            self.edit_custom_delim.setEnabled(True)

        # пропуск строк
        self.spin_skip.blockSignals(True)
        self.spin_skip.setValue(skip)
        self.spin_skip.blockSignals(False)

        # перечитываем файл
        self._reload()

        # применяем маппинг по именам
        header = self.raw_data[self.spin_skip.value()] if self.raw_data else []
        resolved = {}
        for field, name in columns_by_name.items():
            idx_col = -1
            for i2, h in enumerate(header):
                if h.strip() == str(name).strip():
                    idx_col = i2
                    break
            resolved[field] = idx_col
        self._apply_mapping(resolved)

        QMessageBox.information(self, "Маппинг загружен",
                                f"Маппинг применён из файла:\n{path}")


# -------------------- Main window --------------------


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        print("MainWindow __init__ started")

        self.setWindowTitle("Visual Editor by Dudka and Mishutka, version pre-release 0.2.4")

        # window icon (optional)
        left_icon_path = os.path.join(get_app_dir(), "icon_right.ico")
        if os.path.exists(left_icon_path):
            self.setWindowIcon(QIcon(left_icon_path))

        # CSV data
        self.current_file = None
        self.delimiter = ","
        self.header = []
        self.rows = []

        # column indices (will be set after load)
        self.col_comp_name = -1
        self.col_mpn = -1
        self.col_comment = -1
        self.col_designator = -1
        self.col_footprint = -1
        self.col_rotation = -1
        self.col_x = -1
        self.col_y = -1
        self.col_layer = -1

        # graphics scene / view
        print("Creating scene and view...")
        self.scene = QGraphicsScene()
        self.view = BoardView(self.scene)
        self.view.setCursor(Qt.ArrowCursor)
        # scale factor: mm -> px
        self.scale_factor = 10.0
        # --- фоновая картинка при первом запуске ---
        self.bg_item = None
        self._show_startup_background()

        # component items
        self.component_items = []
        self.board_dxf_item = None

        # --- Загрузка библиотеки футпринтов ---
        self.library = load_footprint_library()

        # bottom view flag
        self.bottom_view = False
        self.bot_file_loaded = False          # был ли загружен BOT-файл
        self.pending_bot_rebuild = False      # ожидание перестроения сцены


        # footprint library + dxf
        print("Loading footprint library...")
        self.footprint_library = load_footprint_library()
        self.dxf_footprints = {}  # footprint_name -> list of polylines

        # build UI
        print("Building UI...")
        self._build_ui()
        print("MainWindow __init__ completed")


    def wheelEvent(self, event):
        """Передаём событие колеса мыши в виджет (стандартный зум сцены)."""
        # Блок, отвечающий за масштабирование DXF при Ctrl+колесо, удалён.
        # Теперь событие всегда передаётся в BoardView для масштабирования всей сцены.
        super().wheelEvent(event)

    def _show_startup_background(self):
        """Показать back.png на рабочем поле при запуске программы."""
        script_dir = get_app_dir()
        img_path = os.path.join(script_dir, "back.png")
        if not os.path.exists(img_path):
            print(f"[BG] Файл не найден: {img_path}")
            return
        pixmap = QPixmap(img_path)
        if pixmap.isNull():
            print("[BG] Не удалось загрузить back.png")
            return
        self.bg_item = QGraphicsPixmapItem(pixmap)
        self.bg_item.setZValue(-1000)   # уводим на самый дальний план
        self.scene.addItem(self.bg_item)
        # Границы сцены равны размеру картинки
        self.scene.setSceneRect(self.bg_item.boundingRect())
        # Вписываем картинку в окно целиком
        self.view.fitInView(self.bg_item.boundingRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        """При растягивании окна — подгоняем картинку под новые размеры."""
        super().resizeEvent(event)
        if (self.bg_item is not None
                and self.bg_item.scene() is not None
                and not self.component_items):
            self.view.fitInView(self.bg_item.boundingRect(), Qt.KeepAspectRatio)

    # ----- UI -----

    def _build_ui(self):
        central = QWidget()
        vlayout = QVBoxLayout(central)
        self.setCentralWidget(central)

        # title toolbar with icons & label
        title_bar = QToolBar()
        title_bar.setMovable(False)
        title_widget = QWidget()
        h = QHBoxLayout(title_widget)
        h.setContentsMargins(5, 2, 5, 2)

        left_icon_label = QLabel()
        right_icon_label = QLabel()
        txt_label = QLabel("Visual Editor by Dudka and Mishutka, version pre-release 0.2.4")
        font = txt_label.font()
        font.setBold(True)
        txt_label.setFont(font)

        script_dir = get_app_dir()
        left_path = os.path.join(script_dir, "icon_left.ico")
        right_path = os.path.join(script_dir, "icon_right.ico")

        if os.path.exists(left_path):
            left_icon_label.setPixmap(QPixmap(left_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if os.path.exists(right_path):
            right_icon_label.setPixmap(QPixmap(right_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        h.addWidget(left_icon_label)
        h.addWidget(txt_label, 1, Qt.AlignCenter)
        h.addWidget(right_icon_label)

        title_bar.addWidget(title_widget)
        self.addToolBar(Qt.TopToolBarArea, title_bar)

        # main toolbar
        self.toolbar = QToolBar()
        self.toolbar.setVisible(True)
        self.addToolBar(self.toolbar)

        act_open = QAction("Открыть CSV", self)
        act_save = QAction("Сохранить CSV", self)
        act_save_cock = QAction("Сохранить как", self)
        act_reload_csv = QAction("Обновить CSV", self)
        act_reload_lib = QAction("Обновить библиотеки", self)
        act_bottom_view = QAction("Bottom", self)
        act_bottom_view.setCheckable(True)
        self.act_bottom_view = act_bottom_view
        act_load_dxf = QAction("Загрузить DXF фон", self)
        act_open_lib_editor = QAction("Открыть Library Editor", self)

        self.toolbar.addAction(act_open)
        print("DXF button added")
        self.toolbar.addAction(act_save)
        self.toolbar.addAction(act_save_cock)
        self.toolbar.addAction(act_reload_csv)
        self.toolbar.addAction(act_reload_lib)
        self.toolbar.addSeparator()
        self.toolbar.addAction(act_bottom_view)
        self.toolbar.addSeparator()
        self.toolbar.addAction(act_load_dxf)
        self.toolbar.addSeparator()
        self.toolbar.addAction(act_open_lib_editor)

        act_open.triggered.connect(self.open_csv)
        act_save.triggered.connect(self.save_csv)
        act_save_cock.triggered.connect(self.save_csv_cock)
        act_reload_csv.triggered.connect(self.reload_csv)
        act_reload_lib.triggered.connect(self.reload_library)
        act_bottom_view.toggled.connect(self.toggle_bottom_view)
        act_load_dxf.triggered.connect(self.load_board_dxf)
        act_open_lib_editor.triggered.connect(self.open_library_editor)

        # splitter: scene + table
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.view)

        # table
        self.table_model = CsvTableModel(self.header, self.rows)
        self.table = QTableView()
        self.table.setModel(self.table_model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)
        self.table.setItemDelegateForColumn(
            0, QStyledItemDelegate(self)
        )  # временно, потом заменим на RotationDelegate, когда узнаем колонку

        splitter.addWidget(self.table)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        self.table.selectionModel().selectionChanged.connect(self.on_table_selection_changed)

        vlayout.addWidget(splitter)

        self.statusBar().showMessage("Готово")

    def _connect_scene_signals(self):
        """Подключить сигналы сцены для обработки выбора"""
        # Сигналы уже подключены через mousePressEvent в ComponentItem
        pass

    def on_table_selection_changed(self, selected, deselected):
        """Обработчик изменения выделения в таблице"""
        indexes = selected.indexes()
        if not indexes:
            return

        row = indexes[0].row()
        self.select_component_on_scene(row)

    # ----- CSV load/save -----

    def open_csv(self):
        default_dir = r"C:\S20\Programs"
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть CSV", "", "CSV files (*.csv);;All files (*)"
        )
        if not path:
            return
        self.load_csv(path)

    def load_csv(self, path):
        """Открыть CSV Pick&Place и отобразить компоненты."""
        print(f"Loading CSV from: {path}")

        # ----- Диалог универсального импорта -----
        dlg = CsvImportDialog(path, self)
        if dlg.exec_() != QDialog.Accepted:
            return
        result = dlg.get_result()

        raw = result["raw_data"]
        skip = result["skip_lines"]
        if not raw or skip >= len(raw):
            QMessageBox.warning(self, "Пусто", "Файл не содержит данных.")
            return

        self.current_file = path
        self.delimiter = result["delimiter"]

        # Формируем заголовок и строки
        self.header = [str(h).strip() for h in raw[skip]]
        self.rows = []
        for row in raw[skip + 1:]:
            if not any(cell and str(cell).strip() for cell in row):
                continue
            if len(row) < len(self.header):
                row = row + [""] * (len(self.header) - len(row))
            elif len(row) > len(self.header):
                row = row[:len(self.header)]
            self.rows.append(row)

        # Применяем маппинг столбцов из диалога
        cmap = result["column_map"]
        self.col_comp_name      = cmap.get("comp_name", -1) if cmap.get("comp_name", -1) is not None else -1
        self.col_designator     = cmap.get("designator", -1) if cmap.get("designator", -1) is not None else -1
        self.col_x              = cmap.get("x", -1) if cmap.get("x", -1) is not None else -1
        self.col_y              = cmap.get("y", -1) if cmap.get("y", -1) is not None else -1
        self.col_rotation       = cmap.get("rotation", -1) if cmap.get("rotation", -1) is not None else -1
        self.col_footprint      = cmap.get("footprint", -1) if cmap.get("footprint", -1) is not None else -1
        self.col_comment        = cmap.get("comment", -1) if cmap.get("comment", -1) is not None else -1
        self.col_layer          = cmap.get("layer", -1) if cmap.get("layer", -1) is not None else -1
        self.col_mpn            = -1
        self.col_used_footprint = -1

        print(f"Header: {self.header}")
        print(f"Rows: {len(self.rows)}")
        print(f"Mapping: comp={self.col_comp_name}, desig={self.col_designator}, "
              f"x={self.col_x}, y={self.col_y}, rot={self.col_rotation}, "
              f"fp={self.col_footprint}, layer={self.col_layer}")

        if "Used Footprint" not in self.header:
            self.header.append("Used Footprint")
            for row in self.rows:
                row.append("")

        self.table_model.header = self.header
        self.table_model.rows = self.rows
        print("Updating table model...")
        self.table_model.update_all()

        if 0 <= self.col_rotation < len(self.header):
            self.table.setItemDelegateForColumn(
                self.col_rotation, RotationDelegate(self)
            )

        print("Rebuilding scene...")
        
        # Проверка, является ли файл BOT
        is_bot = "bot" in os.path.basename(path).lower()
        if is_bot:
            self.bot_file_loaded = True
            self.pending_bot_rebuild = True
            # Кнопку Bottom НЕ блокируем — DXF может отсутствовать
            self.act_bottom_view.setEnabled(True)
            # Если Bottom был включен, выключаем его
            if self.bottom_view:
                self.bottom_view = False
                self.act_bottom_view.setChecked(False)
            QMessageBox.warning(self, "Внимание BOT-плата",
                "Обнаружена BOT-плата.\n\n"
                "Для отображения компонентов включите режим Bottom (кнопка 'Bottom' на панели).\n"
                "DXF фон — опционально, но рекомендуется загрузить для удобства.")
            self.statusBar().showMessage("BOT-файл загружен. Требуется DXF и Bottom view.", 5000)
            # не строим сцену
        else:
            self.act_bottom_view.setEnabled(True)
            self.bot_file_loaded = False
            self.pending_bot_rebuild = False
            success = self.rebuild_scene()
            if success:
                self.statusBar().showMessage(f"Загружен файл: {path}")
                print("CSV loading completed")
            else:
                QMessageBox.warning(self, "Предупреждение",
                                    "Файл загружен, но некоторые компоненты не отображены из-за ошибок в данных.")
        def load_board_dxf(self):
            """Загрузить DXF-файл платы и добавить как интерактивный фон под компонентами."""
            from PyQt5.QtWidgets import QFileDialog, QMessageBox
            from PyQt5.QtGui import QColor

            default_dir = r"C:\S20\Programs"
            path, _ = QFileDialog.getOpenFileName(
                self, "Выбрать DXF-файл платы", "", "DXF файлы (*.dxf)"
            )
            if not path:
                return

            print(f"[DXF] Loading board DXF from: {path}")

            # Загружаем полилинии из DXF
            polylines = load_dxf_polylines(path)
            if not polylines:
                QMessageBox.warning(self, "Ошибка DXF", "Не удалось прочитать DXF файл.")
                return

            # Если фон уже есть — удаляем старый
            if hasattr(self, "board_dxf_item") and self.board_dxf_item:
                try:
                    self.scene.removeItem(self.board_dxf_item)
                    print("[DXF] Removed previous DXF background.")
                except Exception as e:
                    print(f"[DXF] Warning: could not remove old DXF: {e}")
                self.board_dxf_item = None

            # --- Создаём новый интерактивный DXF ---
            try:
                dxf_item = InteractiveDXF(polylines, QColor(140, 140, 140))
                dxf_item.setZValue(-10)
                self.scene.addItem(dxf_item)
                dxf_item.setFocus()

                # Центрируем DXF относительно компонентов (если они уже есть)
                if hasattr(self, "component_items") and self.component_items:
                    comp_rect = self.scene.itemsBoundingRect()
                    dxf_rect = dxf_item.boundingRect()
                    dx = comp_rect.center().x() - dxf_rect.center().x()
                    dy = comp_rect.center().y() - dxf_rect.center().y()
                    dxf_item.setPos(dx, dy)
                    print(f"[DXF] Centered DXF relative to components ({dx:.1f}, {dy:.1f}).")
                else:
                    rect = dxf_item.boundingRect()
                    dxf_item.setPos(-rect.center().x(), -rect.center().y())
                    print("[DXF] Centered DXF in scene (no components yet).")

                # Разрешаем получение клавиатурных событий
                dxf_item.setFocus()
                print("[DXF] Focus set for keyboard control (Ctrl + + / -).")

                # Сохраняем DXF как текущий фон
                self.board_dxf_item = dxf_item
                self.current_dxf_path = path

                print(f"[DXF] DXF background loaded and interactive from: {path}")
                QMessageBox.information(
                    self,
                    "DXF загружен",
                    f"Файл '{os.path.basename(path)}' добавлен как интерактивный фон.\n\n"
                    "💡 Управление:\n"
                    " • Перемещение — мышкой (зажать ЛКМ)\n"
                    " • Масштабирование — Ctrl + '+' или Ctrl + '-'\n"
                    " • Ctrl + NumPad '+' / '-' также работают."
                )
                self.check_and_rebuild()

            except Exception as e:
                print(f"[DXF ERROR] Ошибка при создании DXF: {e}")
                QMessageBox.critical(
                    self, "Ошибка DXF", f"Не удалось создать интерактивный DXF:\n{e}"
                )

    def check_and_rebuild(self):
        """Если ожидалась BOT-плата и включён Bottom — строим сцену (DXF не обязателен)."""
        if self.pending_bot_rebuild and self.bottom_view:
            self.pending_bot_rebuild = False
            self.rebuild_scene()
            self.statusBar().showMessage("BOT-плата отображена (Bottom включен).", 5000)


    def _update_column_indices(self):
        print("Updating column indices...")
        try:
            h = self.header
            self.col_comp_name = find_column(h, ["CN", "component_name", "name", "description", "Component Name"])
            self.col_mpn = find_column(h, ["manufacturer part", "mpn", "part number", "part number"])
            self.col_comment = find_column(h, ["comment", "description"])
            self.col_designator = find_column(h, ["designator", "refdes", "ref", "id"])
            self.col_footprint = find_column(h, ["footprint", "package"])
            self.col_rotation = find_column(h, ["rotation", "angle", "rot"])
            self.col_x = find_column(h, ["center-x(mm)", "x", "coord-x", "posx", "center-x(mm)"])
            self.col_y = find_column(h, ["center-y(mm)", "y", "coord-y", "posy", "center-y(mm)"])
            self.col_layer = find_column(h, ["layer"])
            self.col_used_footprint = -1

            print(
                f"Column indices: X={self.col_x}, Y={self.col_y}, Rotation={self.col_rotation}, Designator={self.col_designator}")

        except Exception as e:
            print(f"Error in _update_column_indices: {e}")
            # Устанавливаем значения по умолчанию
            self.col_comp_name = -1
            self.col_mpn = -1
            self.col_comment = -1
            self.col_designator = -1
            self.col_footprint = -1
            self.col_rotation = -1
            self.col_x = -1
            self.col_y = -1
            self.col_layer = -1
            self.col_used_footprint = -1

    def _get_board_outline_rect(self):
        """
        Найти в CSV компоненты с CN = 'krug' и CN = 'romb',
        вернуть кортеж (left, top, right, bottom) в мм или None.
        """
        if not self.rows:
            return None
        if self.col_comp_name < 0 or self.col_x < 0 or self.col_y < 0:
            return None

        krug_xy = None
        romb_xy = None

        for row in self.rows:
            if self.col_comp_name >= len(row):
                continue
            cn = str(row[self.col_comp_name]).strip().lower()
            if cn not in ("krug", "romb"):
                continue
            if self.col_x >= len(row) or self.col_y >= len(row):
                continue
            try:
                x = float(str(row[self.col_x]).strip())
                y = float(str(row[self.col_y]).strip())
            except (ValueError, TypeError):
                continue
            if cn == "krug" and krug_xy is None:
                krug_xy = (x, y)
            elif cn == "romb" and romb_xy is None:
                romb_xy = (x, y)

        if krug_xy is None or romb_xy is None:
            return None

        x1, y1 = krug_xy
        x2, y2 = romb_xy
        left = min(x1, x2)
        right = max(x1, x2)
        top = max(y1, y2)        # Y в модели идёт вверх
        bottom = min(y1, y2)
        return (left, top, right, bottom)

    def _add_outline_to_scene(self):
        """Построить и добавить на сцену контур платы по krug/romb. Вернуть item или None."""
        rect_mm = self._get_board_outline_rect()
        if rect_mm is None:
            return None

        left, top, right, bottom = rect_mm
        sf = self.scale_factor

        # Учитываем bottom_view (инверсия X)
        if self.bottom_view:
            x1 = -right * sf
            x2 = -left * sf
        else:
            x1 = left * sf
            x2 = right * sf
        y1 = -top * sf           # в Qt Y растёт вниз
        y2 = -bottom * sf

        rect = QRectF(x1, y1, x2 - x1, y2 - y1)
        path = QPainterPath()
        path.addRect(rect)

        item = QGraphicsPathItem(path)
        pen = QPen(QColor(80, 80, 80))
        pen.setWidthF(2.0)
        pen.setCosmetic(True)
        item.setPen(pen)
        item.setBrush(QBrush(Qt.NoBrush))
        item.setZValue(-5)       # выше DXF (-10), ниже компонентов (0 и выше)
        item.setData(0, "board_outline")
        self.scene.addItem(item)
        return item

    def save_csv(self):
        if not self.current_file:
            path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить CSV", "", "CSV files (*.csv);;All files (*)"
            )
            if not path:
                return
            self.current_file = path

        try:
            with open(self.current_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, delimiter=self.delimiter)
                writer.writerow(self.header)
                # Вставляем пустую строку (все ячейки пустые)
                writer.writerow([''] * len(self.header))
                for row in self.rows:
                    writer.writerow(row)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить CSV:\n{e}")
            return

        self.statusBar().showMessage(f"CSV сохранён: {self.current_file}")

    def save_csv_cock(self):
        """Сохранить CSV файл с выбором имени и места"""
        # Определяем начальную директорию и имя файла
        initial_dir = ""
        initial_file = ""

        if self.current_file:
            # Если файл уже открыт, используем его директорию и имя
            initial_dir = os.path.dirname(self.current_file)
            initial_file = os.path.basename(self.current_file)
        else:
            # Иначе используем домашнюю директорию и предлагаем имя по умолчанию
            initial_dir = os.path.expanduser("~")
            initial_file = "board_layout.csv"

        # Открываем диалог "Сохранить как"
        path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Сохранить CSV как",
            os.path.join(initial_dir, initial_file),
            "CSV files (*.csv);;All files (*)"
        )

        if not path:
            return  # Пользователь отменил сохранение

        # Добавляем расширение .csv если его нет
        if not path.lower().endswith('.csv'):
            path += '.csv'

        try:
            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, delimiter=self.delimiter)
                writer.writerow(self.header)
                # Вставляем пустую строку
                writer.writerow([''] * len(self.header))
                for row in self.rows:
                    writer.writerow(row)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить CSV:\n{e}")
            return

        # Обновляем текущий файл
        self.current_file = path
        self.statusBar().showMessage(f"CSV сохранён как: {self.current_file}")

    def reload_csv(self):
        if not self.current_file:
            QMessageBox.warning(self, "Нет файла", "Сначала откройте CSV.")
            return
        self.load_csv(self.current_file)

    def open_library_editor(self):
        """Запустить Library_Editor (exe или .py) отдельным процессом."""
        script_dir = get_app_dir()

        # 1) Пытаемся найти Library_Editor.exe рядом с Visual_Editor
        exe_path = os.path.join(script_dir, "Library_Editor.exe")
        if os.path.exists(exe_path):
            try:
                subprocess.Popen([exe_path], cwd=script_dir)
                self.statusBar().showMessage(
                    "Library Editor запущен в отдельном окне.", 4000
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка запуска",
                    f"Не удалось запустить Library_Editor.exe:\n{e}"
                )
            return

        # 2) Если exe нет — пытаемся найти Library_Editor.py и запустить через Python
        py_path = os.path.join(script_dir, "Library_Editor.py")
        if os.path.exists(py_path):
            try:
                subprocess.Popen([sys.executable, py_path], cwd=script_dir)
                self.statusBar().showMessage(
                    "Library Editor запущен в отдельном окне.", 4000
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка запуска",
                    f"Не удалось запустить Library_Editor.py:\n{e}"
                )
            return

        QMessageBox.warning(
            self, "Файл не найден",
            f"Рядом с Visual_Editor не найден ни Library_Editor.exe,\n"
            f"ни Library_Editor.py.\n"
            f"Ожидалось в папке:\n{script_dir}"
        )

    # ----- library reload -----

    def reload_library(self):
        # Загружаем новую библиотеку
        self.footprint_library = load_footprint_library()

        # Если нет компонентов – выходим
        if not self.component_items:
            self.statusBar().showMessage("Библиотека обновлена, но нет компонентов для обновления.", 3000)
            return

        # Обновляем компоненты на сцене
        for item in self.component_items:
            comp_name = item.comp_name
            footprint = item.footprint
            # Получаем новую информацию о корпусе
            new_pkg_info, used_key = self._match_footprint_info(comp_name, footprint)

            # Если корпус не изменился, пропускаем
            if new_pkg_info == item.pkg_info:
                continue

            # Обновляем компонент
            item.pkg_info = new_pkg_info
            item.lib_angle = float(new_pkg_info.get("zero_angle_tape", 0.0)) if new_pkg_info else 0.0
            size = new_pkg_info.get("size", [1.0, 0.5])
            item.width_mm = float(size[0]) if size else 1.0
            item.height_mm = float(size[1]) if size else 0.5
            # Обновляем DXF-пути для нового footprint (если есть)
            item.dxf_paths = self.dxf_footprints.get(footprint, None)
            # Перестраиваем геометрию
            item.rebuild_geometry()
            # Обновляем поворот (чтобы учесть новый библиотечный угол)
            visual_angle = -item.csv_rotation + item.lib_angle
            item.setRotation(visual_angle)
            item.update_tooltip()
            item.update_text_position()

            # Обновляем столбец "Used Footprint" в CSV
            used_fp_col = -1
            if "Used Footprint" in self.header:
                used_fp_col = self.header.index("Used Footprint")
            if used_fp_col >= 0 and 0 <= item.row_index < len(self.rows):
                self.rows[item.row_index][used_fp_col] = used_key if used_key else ""
                idx = self.table_model.index(item.row_index, used_fp_col)
                self.table_model.dataChanged.emit(idx, idx, [Qt.DisplayRole, Qt.EditRole])

        # Обновляем таблицу (на случай, если добавились новые строки, но их нет)
        self.table_model.update_all()
        # Обновляем границы сцены (возможно, изменились размеры компонентов)
        self.update_scene_bounds()
        self.statusBar().showMessage("Библиотека корпусов обновлена из footprints.json", 5000)

    # ----- DXF -----

    def load_board_dxf(self):
        """Загрузить DXF-файл платы и добавить как интерактивный фон под компонентами."""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        from PyQt5.QtGui import QColor

        path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать DXF-файл платы", "", "DXF файлы (*.dxf)"
        )
        if not path:
            return

        print(f"[DXF] Loading board DXF from: {path}")

        polylines = load_dxf_polylines(path)
        if not polylines:
            QMessageBox.warning(self, "Ошибка DXF", "Не удалось прочитать DXF файл.")
            return

        # Если фон уже есть — удаляем старый
        if hasattr(self, "board_dxf_item") and self.board_dxf_item:
            try:
                self.scene.removeItem(self.board_dxf_item)
                print("[DXF] Removed previous DXF background.")
            except Exception as e:
                print(f"[DXF] Warning: could not remove old DXF: {e}")
            self.board_dxf_item = None
            self.view.dxf_item = None

        try:
            dxf_item = InteractiveDXF(polylines, QColor(140, 140, 140))
            dxf_item.setZValue(-10)
            self.scene.addItem(dxf_item)
            dxf_item.setFocus()

            # Центрируем DXF относительно компонентов (если они уже есть)
            if hasattr(self, "component_items") and self.component_items:
                comp_rect = self.scene.itemsBoundingRect()
                dxf_rect = dxf_item.boundingRect()
                dx = comp_rect.center().x() - dxf_rect.center().x()
                dy = comp_rect.center().y() - dxf_rect.center().y()
                dxf_item.setPos(dx, dy)
                print(f"[DXF] Centered DXF relative to components ({dx:.1f}, {dy:.1f}).")
            else:
                rect = dxf_item.boundingRect()
                dxf_item.setPos(-rect.center().x(), -rect.center().y())
                print("[DXF] Centered DXF in scene (no components yet).")

            dxf_item.setFocus()
            self.board_dxf_item = dxf_item
            self.view.dxf_item = dxf_item
            self.current_dxf_path = path

            # Кнопка Bottom всегда активна — просто сообщаем, что DXF добавлен
            if self.bot_file_loaded:
                self.statusBar().showMessage("DXF загружен.", 3000)

            print(f"[DXF] DXF background loaded and interactive from: {path}")
            QMessageBox.information(
                self,
                "DXF загружен",
                f"Файл '{os.path.basename(path)}' добавлен как интерактивный фон.\n\n"
                "💡 Управление:\n"
                " • Перемещение — мышкой (зажать ЛКМ)\n"
                " • Масштабирование — Ctrl + '+' или Ctrl + '-'\n"
                " • Ctrl + NumPad '+' / '-' также работают."
            )
            self.check_and_rebuild()
        except Exception as e:
            print(f"[DXF ERROR] Ошибка при создании DXF: {e}")
            QMessageBox.critical(
                self, "Ошибка DXF", f"Не удалось создать интерактивный DXF:\n{e}"
            )

    def load_dxf_for_footprint(self):
        if not self.header:
            QMessageBox.warning(self, "Нет данных", "Сначала откройте CSV.")
            return

        dxf_path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать DXF", "", "DXF files (*.dxf);;All files (*)"
        )
        if not dxf_path:
            return

        footprint_name, ok = QInputDialog.getText(
            self, "Имя footprint",
            "Введите имя footprint, к которому относится этот DXF:"
        )
        if not ok or not footprint_name.strip():
            return
        footprint_name = footprint_name.strip()

        polys = load_dxf_polylines(dxf_path)
        if not polys:
            QMessageBox.warning(self, "DXF", "Не удалось извлечь полилинии из DXF.")
            return

        self.dxf_footprints[footprint_name] = polys
        self.rebuild_scene()
        self.statusBar().showMessage(
            f"DXF загружен и назначен для footprint '{footprint_name}'", 5000
        )

    def update_scene_bounds(self):
        """Обновить границы сцены с учетом bottom view"""
        if not self.component_items:
            self.view.reset_view(QRectF(-100, -100, 200, 200))
            return

        minx = miny = 1e9
        maxx = maxy = -1e9

        for item in self.component_items:
            # Получаем отображаемые координаты компонента
            if self.bottom_view:
                display_x = -item.original_x_mm
            else:
                display_x = item.original_x_mm
            display_y = item.display_y_mm

            # Учитываем размер компонента для правильных границ
            half_width = item.width_mm / 2
            half_height = item.height_mm / 2

            # Также учитываем позицию текста
            if hasattr(item, 'text_item') and item.text_item:
                text_rect = item.text_item.boundingRect()
                text_pos = item.text_item.pos()
                text_left = text_pos.x() / self.scale_factor
                text_right = (text_pos.x() + text_rect.width()) / self.scale_factor
                text_top = text_pos.y() / self.scale_factor
                text_bottom = (text_pos.y() + text_rect.height()) / self.scale_factor

                minx = min(minx, display_x - half_width, text_left)
                maxx = max(maxx, display_x + half_width, text_right)
                miny = min(miny, display_y - half_height, text_top)
                maxy = max(maxy, display_y + half_height, text_bottom)
            else:
                minx = min(minx, display_x - half_width)
                maxx = max(maxx, display_x + half_width)
                miny = min(miny, display_y - half_height)
                maxy = max(maxy, display_y + half_height)

        # Устанавливаем границы сцены с отступом
        padding = 2000  # отступ в пикселях
        rect = QRectF(
            minx * self.scale_factor - padding,
            miny * self.scale_factor - padding,
            (maxx - minx) * self.scale_factor + 2 * padding,
            (maxy - miny) * self.scale_factor + 2 * padding
        )

        self.scene.setSceneRect(rect)
        if hasattr(self, 'view') and self.view:
            self.view.reset_view(rect)

    # ----- bottom view -----

    def toggle_bottom_view(self, checked):

        self.bottom_view = checked

        # --- Обновляем компоненты ---
        self.update_bottom_view_for_all_components()
        self.update_scene_bounds()

        # --- Зеркалим DXF при переключении ---
        if hasattr(self, "board_dxf_item") and self.board_dxf_item:
            try:
                from PyQt5.QtGui import QTransform
                current_scale = self.board_dxf_item.scale()
                transform = QTransform()
                if checked:
                    transform.scale(-current_scale, current_scale)
                else:
                    transform.scale(current_scale, current_scale)
                center = self.board_dxf_item.boundingRect().center()
                self.board_dxf_item.setTransformOriginPoint(center)
                self.board_dxf_item.setTransform(transform)
                print(f"[DXF] Mirrored horizontally (bottom_view={checked}) with scale={current_scale:.2f}")
            except Exception as e:
                print(f"[DXF ERROR] Failed to mirror DXF: {e}")

        # --- Перестраиваем контур платы (для корректной инверсии X) ---
        try:
            # удаляем старые контуры (если есть)
            for item in self.scene.items():
                if item.data(0) == "board_outline":
                    self.scene.removeItem(item)
            # и добавляем новый
            outline_item = self._add_outline_to_scene()
            if outline_item is not None:
                outline_item.setData(0, "board_outline")
        except Exception as e:
            print(f"Outline refresh failed: {e}")

        # --- Обновляем статус в строке состояния ---
        if checked:
            self.statusBar().showMessage("Bottom view включен (X инвертирован, DXF зеркален)")
        else:
            self.statusBar().showMessage("Bottom view выключен (DXF в обычном положении)")

        # Проверяем, нужно ли перестроить сцену для BOT
        self.check_and_rebuild()

    def update_bottom_view_for_all_components(self):
        """Обновить bottom view для всех компонентов"""
        for item in self.component_items:
            item.update_bottom_view(self.bottom_view)

    # ----- scene build -----

    def safe_clear_scene(self):
        """Безопасная очистка сцены"""
        try:
            # Сначала удаляем все текстовые элементы
            for item in self.component_items:
                if hasattr(item, 'text_item') and item.text_item:
                    try:
                        if item.text_item.scene():
                            self.scene.removeItem(item.text_item)
                    except Exception as e:
                        print(f"Error removing text item: {e}")

            # Затем очищаем основной список
            self.component_items.clear()

            # Если сцена очищается — обнуляем ссылку на DXF-группу (Qt сам удалит объект)
            if hasattr(self, "board_dxf_item") and self.board_dxf_item:
                if self.board_dxf_item.scene():
                    self.scene.removeItem(self.board_dxf_item)            
            # Стартовый фон удаляется вместе со сценой — сбрасываем ссылку
            self.bg_item = None
            # И наконец очищаем сцену
            self.scene.clear()

            # --- Восстановление DXF фона после очистки ---
            if hasattr(self, "board_dxf_item") and self.board_dxf_item:
                # Проверяем, не добавлен ли уже DXF в сцену
                if self.board_dxf_item.scene() is None:
                    self.scene.addItem(self.board_dxf_item)
                    self.board_dxf_item.setZValue(-10)

        except Exception as e:
            print(f"Error in safe_clear_scene: {e}")
            # В случае ошибки создаем новую сцену
            try:
                self.scene = QGraphicsScene()
                self.view.setScene(self.scene)
                self.component_items = []

                # --- Возвращаем DXF фон, если он есть ---
                if hasattr(self, "board_dxf_item") and self.board_dxf_item:
                    if self.board_dxf_item.scene() is None:
                        self.scene.addItem(self.board_dxf_item)
                        self.board_dxf_item.setZValue(-10)

            except Exception as e2:
                print(f"Critical error recreating scene: {e2}")

    def rebuild_scene(self):
        self.view.zoom_enabled = True
         # Блокировка для BOT-платы без необходимых условий
         # Блокировка для BOT-платы: пока не включён Bottom — не строим
        if self.bot_file_loaded and not self.bottom_view:
                self.scene.clear()
                self.statusBar().showMessage("Для BOT-платы включите Bottom view", 3000)
                return False
        if hasattr(self, "current_dxf_path"):
            print(f"[DEBUG] DXF path at rebuild start: {self.current_dxf_path}")
        else:
            print("[DEBUG] DXF path variable does not exist yet.")
        print("rebuild_scene started")
        try:
            # Безопасная очистка предыдущих элементов
            print("Clearing old items...")
            self.safe_clear_scene()
            print("Scene cleared")

            if not self.rows:
                print("No rows, setting default view")
                self.view.reset_view(QRectF(-100, -100, 200, 200))
                return True

            minx = miny = 1e9
            maxx = maxy = -1e9

            # Находим индекс столбца Used Footprint
            used_footprint_col = -1
            try:
                if "Used Footprint" in self.header:
                    used_footprint_col = self.header.index("Used Footprint")
                    print(f"Used Footprint column: {used_footprint_col}")
            except Exception as e:
                print(f"Error finding Used Footprint column: {e}")

            print(f"Processing {len(self.rows)} rows...")
            processed_count = 0
            error_count = 0

            for i, row in enumerate(self.rows):
                if i % 50 == 0:  # Выводим прогресс каждые 50 строк
                    print(f"Processing row {i}/{len(self.rows)}")

                try:
                    # Безопасное получение координат
                    x_mm = 0.0
                    y_mm = 0.0

                    if self.col_x >= 0 and self.col_x < len(row):
                        x_val = row[self.col_x]
                        if x_val and str(x_val).strip():
                            try:
                                x_mm = float(str(x_val).strip())
                            except (ValueError, TypeError):
                                x_mm = 0.0
                                print(f"Warning: Invalid X coordinate in row {i}: '{x_val}'")

                    if self.col_y >= 0 and self.col_y < len(row):
                        y_val = row[self.col_y]
                        if y_val and str(y_val).strip():
                            try:
                                y_mm = float(str(y_val).strip())
                            except (ValueError, TypeError):
                                y_mm = 0.0
                                print(f"Warning: Invalid Y coordinate in row {i}: '{y_val}'")

                    # Безопасное получение rotation
                    rotation_deg = 0.0
                    if self.col_rotation >= 0 and self.col_rotation < len(row):
                        rot_val = row[self.col_rotation]
                        if rot_val and str(rot_val).strip():
                            try:
                                rotation_deg = float(str(rot_val).strip())
                            except (ValueError, TypeError):
                                rotation_deg = 0.0
                                print(f"Warning: Invalid rotation in row {i}: '{rot_val}'")

                    # Безопасное получение текстовых данных
                    designator = f"U{i + 1}"  # значение по умолчанию
                    if self.col_designator >= 0 and self.col_designator < len(row):
                        desig_val = row[self.col_designator]
                        if desig_val and str(desig_val).strip():
                            designator = str(desig_val).strip()
                        else:
                            designator = f"U{i + 1}"

                    comp_name = ""
                    if self.col_comp_name >= 0 and self.col_comp_name < len(row):
                        comp_val = row[self.col_comp_name]
                        if comp_val:
                            comp_name = str(comp_val).strip()

                    footprint = ""
                    if self.col_footprint >= 0 and self.col_footprint < len(row):
                        fp_val = row[self.col_footprint]
                        if fp_val:
                            footprint = str(fp_val).strip()

                    # Пропускаем компоненты без координат
                    if x_mm == 0.0 and y_mm == 0.0:
                        print(f"Skipping component {designator} at (0,0)")
                        continue

                    print(f"Row {i}: {designator} at ({x_mm}, {y_mm})")

                    # Получаем информацию о корпусе
                    pkg_info, used_key = self._match_footprint_info(comp_name, footprint)

                    # Определяем используемый footprint (только если точно совпадает)
                    used_footprint = used_key if used_key else ""

                    # Заполняем столбец Used Footprint
                    if used_footprint_col >= 0 and used_footprint_col < len(row):
                        row[used_footprint_col] = used_footprint

                    dxf_paths = None
                    if footprint in self.dxf_footprints:
                        dxf_paths = self.dxf_footprints[footprint]

                    # Создаем компонент с учетом текущего состояния bottom_view
                    item = ComponentItem(
                        editor=self,
                        row_index=i,
                        designator=designator,
                        comp_name=comp_name,
                        footprint=footprint,
                        x_mm=x_mm,
                        y_mm=y_mm,
                        rotation_deg=rotation_deg,
                        pkg_info=pkg_info,
                        scale_factor=self.scale_factor,
                        dxf_paths=dxf_paths,
                        bottom_view=self.bottom_view
                    )

                    self.scene.addItem(item)
                    self.component_items.append(item)

                    # Обновляем границы сцены (учитываем bottom_view и размер компонента)
                    display_x = -x_mm if self.bottom_view else x_mm
                    display_y = -y_mm

                    # Учитываем размер компонента для правильных границ
                    half_width = item.width_mm / 2
                    half_height = item.height_mm / 2

                    minx = min(minx, display_x - half_width)
                    maxx = max(maxx, display_x + half_width)
                    miny = min(miny, display_y - half_height)
                    maxy = max(maxy, display_y + half_height)

                    processed_count += 1

                except Exception as e:
                    print(f"Error processing row {i}: {e}")
                    traceback.print_exc()
                    error_count += 1
                    continue

            print(f"Successfully processed {processed_count} components, {error_count} errors")
            print(f"Scene bounds: ({minx}, {miny}) to ({maxx}, {maxy})")

            # Устанавливаем границы сцены с помощью отдельного метода
            self.update_scene_bounds()

            # Обновляем таблицу
            if hasattr(self, 'table_model') and self.table_model:
                try:
                    self.table_model.update_all()
                except Exception as e:
                    print(f"Error updating table: {e}")

            # Подключаем сигналы
            self._connect_scene_signals()

            # --- Восстанавливаем DXF фон после загрузки CSV ---
            try:
                if hasattr(self, "board_dxf_item") and self.board_dxf_item:
                    # Добавляем обратно в сцену, если был удалён
                    if self.board_dxf_item.scene() is None:
                        self.scene.addItem(self.board_dxf_item)

                    # Разрешаем ручное управление DXF
                    self.board_dxf_item.setFlag(QGraphicsItemGroup.ItemIsMovable, True)
                    self.board_dxf_item.setFlag(QGraphicsItemGroup.ItemIsSelectable, True)
                    self.board_dxf_item.setFlag(QGraphicsItemGroup.ItemSendsGeometryChanges, True)
                    self.board_dxf_item.setFiltersChildEvents(True)
                    self.board_dxf_item.setZValue(-10)

                    print("DXF background restored (movable).")
                else:
                    print("No DXF background to restore.")
            except Exception as e:
                print(f"DXF restore failed: {e}")

            # --- Контур платы по krug/romb ---
            try:
                self._add_outline_to_scene()
                print("Board outline (krug/romb) added to scene.")
            except Exception as e:
                print(f"Outline build failed: {e}")

            # --- Восстанавливаем DXF фон после загрузки CSV ---
        
        finally:
                print("rebuild_scene completed successfully")
        return True

    def _match_footprint_info(self, comp_name, footprint):
        """
        Подбор записи из библиотеки корпусов по имени компонента (comp_name).
        Возвращает кортеж (pkg_info, key), где key — ключ из библиотеки,
        по которому был найден корпус.
        Параметр footprint не используется.
        """
        lib = self.footprint_library
        if not comp_name:
            return None, None

        comp_upper = comp_name.upper()

        # 1. Точное совпадение по ключу библиотеки
        for key in lib:
            if key.upper() == comp_upper:
                return lib[key], key

        # 2. Поиск по известным шаблонам в имени компонента
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
                # Сначала ищем точный ключ, равный шаблону
                if p in lib:
                    return lib[p], p
                # Если нет, ищем любой ключ, содержащий этот шаблон
                for key in lib:
                    if p in key.upper():
                        return lib[key], key

        # 3. Частичное совпадение: ключ содержится в имени компонента или наоборот
        sorted_keys = sorted(lib.keys(), key=len, reverse=True)
        for key in sorted_keys:
            key_upper = key.upper()
            if key_upper in comp_upper or comp_upper in key_upper:
                return lib[key], key

        # 4. Общие категории (резисторы, конденсаторы и т.п.)
        if any(word in comp_upper for word in ['RESISTOR', 'RES', 'R']):
            for size in ['0402', '0603', '0805', '1206']:
                if size in lib:
                    return lib[size], size
        if any(word in comp_upper for word in ['CAPACITOR', 'CAP', 'C']):
            for size in ['0402', '0603', '0805', '1206']:
                if size in lib:
                    return lib[size], size
        if any(word in comp_upper for word in ['INDUCTOR', 'IND', 'L']):
            for size in ['0402', '0603', '0805', '1206']:
                key = f"L{size}"
                if key in lib:
                    return lib[key], key
                elif size in lib:
                    return lib[size], size
        if any(word in comp_upper for word in ['DIODE', 'D']):
            if 'SOD123' in lib:
                return lib['SOD123'], 'SOD123'
            elif 'SOD323' in lib:
                return lib['SOD323'], 'SOD323'
        if any(word in comp_upper for word in ['LED', 'LIGHT']):
            if 'LED0603' in lib:
                return lib['LED0603'], 'LED0603'

        return None, None

    # ----- rotation handling -----

    def change_component_rotation(self, item: ComponentItem, new_angle: float):
        """Меняем CSV-угол компонента (по часовой – отрицательный)."""
        # Нормализуем угол к диапазону -180 до 180 градусов
        angle = (new_angle + 180) % 360 - 180
        angle = int(angle)  # Округляем до 2 знаков

        # Для визуального отображения инвертируем угол (зеркально)
        visual_angle = -angle

        # Обновляем компонент с визуальным углом
        item.setRotation(visual_angle + item.lib_angle)
        item.csv_rotation = angle  # Сохраняем исходный угол для CSV
        item.update_tooltip()
        item.update_text_position()

        if 0 <= item.row_index < len(self.rows) and self.col_rotation >= 0:
            self.rows[item.row_index][self.col_rotation] = f"{angle}"
            idx = self.table_model.index(item.row_index, self.col_rotation)
            self.table_model.dataChanged.emit(idx, idx, [Qt.DisplayRole, Qt.EditRole])

    def update_component_rotation_from_table(self, index: QModelIndex):
        if not index.isValid() or index.column() != self.col_rotation:
            return
        row = index.row()
        if row < 0 or row >= len(self.component_items):
            return
        value_str = self.rows[row][self.col_rotation]
        try:
            angle = float(value_str)
        except ValueError:
            angle = 0.0
        item = self.component_items[row]

        # Используем update_rotation который сам инвертирует угол
        item.update_rotation(angle)
        item.update_tooltip()

    # ----- manual footprint assignment -----

    def assign_footprint_to_component(self, item: ComponentItem):
        if not self.footprint_library:
            QMessageBox.warning(self, "Библиотека пуста", "footprints.json не содержит корпусов.")
            return
        names = sorted(self.footprint_library.keys())
        name, ok = QInputDialog.getItem(
            self, "Назначить корпус",
            "Выберите корпус из библиотеки:", names, 0, False
        )
        if not ok or not name:
            return
        pkg_info = self.footprint_library[name]

        # обновим данные в CSV – столбец Footprint
        if self.col_footprint >= 0 and 0 <= item.row_index < len(self.rows):
            self.rows[item.row_index][self.col_footprint] = name
            idx = self.table_model.index(item.row_index, self.col_footprint)
            self.table_model.dataChanged.emit(idx, idx, [Qt.DisplayRole, Qt.EditRole])

        # Обновляем атрибуты компонента
        item.footprint = name
        item.pkg_info = pkg_info
        item.lib_angle = float(pkg_info.get("zero_angle_tape", 0.0)) if pkg_info else 0.0
        size = pkg_info.get("size", [1.0, 0.5])
        item.width_mm = float(size[0]) if size else 1.0
        item.height_mm = float(size[1]) if size else 0.5
        # Обновляем DXF-пути для нового footprint (если есть)
        item.dxf_paths = self.dxf_footprints.get(name, None)

        # Перестраиваем геометрию компонента
        item.rebuild_geometry()

        # Обновляем поворот с учётом нового библиотечного угла
        visual_angle = -item.csv_rotation + item.lib_angle
        item.setRotation(visual_angle)
        item.update_tooltip()
        item.update_text_position()

    def select_component_in_table(self, item: ComponentItem):
        """Выделить строку в таблице, соответствующую компоненту"""
        if not hasattr(item, 'row_index'):
            return

        # Получаем модель выделения
        selection_model = self.table.selectionModel()

        # Создаем выделение для всей строки
        selection = QItemSelection()
        first_index = self.table_model.index(item.row_index, 0)
        last_index = self.table_model.index(item.row_index, self.table_model.columnCount() - 1)
        selection.select(first_index, last_index)

        # Очищаем предыдущее выделение и устанавливаем новое
        selection_model.clearSelection()
        selection_model.select(selection, QItemSelectionModel.Select)

        # Прокручиваем таблицу к выделенной строке
        self.table.scrollTo(first_index, QAbstractItemView.PositionAtTop)

    def select_component_on_scene(self, row_index):
        """Выделить компонент на сцене и прокрутить к нему view"""
        if row_index < 0 or row_index >= len(self.component_items):
            return

        item = self.component_items[row_index]

        for comp_item in self.component_items:
            comp_item.setSelected(False)
            for child in comp_item.childItems():
                child.setSelected(False)

        item.setSelected(True)
        for child in item.childItems():
            child.setSelected(True)

        self.view.centerOn(item)

        item.setFocus()

    def keyPressEvent(self, event):
        """Обработка Ctrl + '+' / '-' для масштабирования DXF."""
        if hasattr(self, "board_dxf_item") and self.board_dxf_item:
            if event.modifiers() & Qt.ControlModifier:
                key = event.key()

                # --- обработка клавиш (масштаб всегда берём у самого объекта) ---
                if key in (Qt.Key_Plus, Qt.Key_Equal):
                    new_scale = self.board_dxf_item.scale() * 1.01
                    self.board_dxf_item.setScale(new_scale)
                    print(f"[DXF] Scale increased: {new_scale:.2f}")
                    event.accept()
                    return

                elif key in (Qt.Key_Minus, Qt.Key_Underscore):
                    new_scale = self.board_dxf_item.scale() / 1.01
                    self.board_dxf_item.setScale(new_scale)
                    print(f"[DXF] Scale decreased: {new_scale:.2f}")
                    event.accept()
                    return

                elif key == Qt.Key_0:
                    self.board_dxf_item.setScale(1.0)
                    print("[DXF] Scale reset to 1.00")
                    event.accept()
                    return

        # передаём событие дальше, если не наши клавиши
        super().keyPressEvent(event)


def main():
    print("Starting application...")

    app = QApplication(sys.argv)
    print("QApplication created")

    try:
        win = MainWindow()
        print("MainWindow created")

        # Открываем окно развёрнутым на весь экран
        win.showMaximized()
        print("Window shown maximized - entering main loop")

        result = app.exec_()
        print(f"Application finished with result: {result}")
        sys.exit(result)

    except Exception as e:
        print(f"Error creating MainWindow: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
