# src/modules/function_library.py

import inspect
import importlib

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea,
    QPlainTextEdit, QSizePolicy,
)
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal
from PyQt5.QtGui import QDrag, QFont, QColor

from .library.definitions import LIBRARY_FUNCTIONS
from .translations import STRINGS

# Mapping from English category names in LIBRARY_FUNCTIONS → translation keys
_CAT_KEY_MAP = {
    "Camera": "CAT_CAMERA",
    "Image Processing": "CAT_IMAGE_PROCESSING",
    "AI Vision Core": "CAT_AI_VISION_CORE",
    "Display & Dashboard": "CAT_DISPLAY_DASHBOARD",
    "Logic Operations": "CAT_LOGIC_OPERATIONS",
    "Variables": "CAT_VARIABLES",
    "Robotics": "CAT_ROBOTICS",
}

# Categories that are ALWAYS unlocked (no lesson required)
ALWAYS_UNLOCKED_CATEGORIES = {"Logic Operations", "Variables"}

# Categories that are LOCKED by default – functions unlock via lessons
LOCKED_CATEGORIES = {"Camera", "Image Processing", "AI Vision Core", "Display & Dashboard", "Robotics"}

# Mapping from function IDs → description translation keys
_FN_DESC_KEY_MAP = {
    "Init_Camera": "FN_INIT_CAMERA",
    "Get_Camera_Frame": "FN_GET_CAMERA_FRAME",
    "Close_Camera": "FN_CLOSE_CAMERA",
    "convert_to_gray": "FN_CONVERT_TO_GRAY",
    "resize_image": "FN_RESIZE_IMAGE",
    "apply_blur": "FN_APPLY_BLUR",
    "detect_edges": "FN_DETECT_EDGES",
    "flip_image": "FN_FLIP_IMAGE",
    "Load_YuNet_Model": "FN_LOAD_YUNET_MODEL",
    "Run_YuNet_Model": "FN_RUN_YUNET_MODEL",
    "Load_ONNX_Model": "FN_LOAD_ONNX_MODEL",
    "Run_ONNX_Model": "FN_RUN_ONNX_MODEL",
    "Load_Engine_Model": "FN_LOAD_ENGINE_MODEL",
    "Run_Engine_Model": "FN_RUN_ENGINE_MODEL",
    "Draw_Detections": "FN_DRAW_DETECTIONS",
    "Draw_Detections_Multiclass": "FN_DRAW_DETECTIONS_MULTICLASS",
    "Draw_Engine_Detections": "FN_DRAW_ENGINE_DETECTIONS",
    "Update_Dashboard": "FN_UPDATE_DASHBOARD",
    "Loop_Forever": "FN_LOOP_FOREVER",
    "If_Condition": "FN_IF_CONDITION",
    "If_Else_Control": "FN_IF_ELSE_CONTROL",
    "DC_Run": "FN_DC_RUN",
    "DC_Stop": "FN_DC_STOP",
    "Get_Speed": "FN_GET_SPEED",
    "Set_Servo": "FN_SET_SERVO",
    "Define_Classes": "FN_DEFINE_CLASSES",
}


def _darken_hex(hex_color, factor=0.82):
    """Return a solid darker shade of a hex color (no alpha tricks)."""
    h = hex_color.lstrip("#")
    r = int(int(h[0:2], 16) * factor)
    g = int(int(h[2:4], 16) * factor)
    b = int(int(h[4:6], 16) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"



# ────────────────────────────────────────────────────────────
#  Inline Info Panel  —  simplified flat design
# ────────────────────────────────────────────────────────────

class FunctionInfoPanel(QFrame):
    """
    Expandable panel shown below the function block row.
    Flat design: Snippet → Parameters → Returns → Source Code.
    """

    def __init__(self, func_id, info, category_color, is_small=False, lang="en"):
        super().__init__()
        s = STRINGS.get(lang, STRINGS["en"])
        self._lang = lang
        self._is_small = is_small
        self.setObjectName("InfoPanel")
        self.setStyleSheet(f"""
            QFrame#InfoPanel {{
                background: #fafafa;
                border: 1px solid #e2e8f0;
                border-top: 2px solid {category_color};
                border-radius: 0 0 10px 10px;
                margin: 0 12px 6px 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(10)

        usage  = info.get("usage", "")
        params = info.get("params", [])
        returns = info.get("returns")

        # 1. Snippet (dragged)
        if usage:
            layout.addWidget(self._bold_label(s.get("INFO_SNIPPET", "Snippet (Dragged):")))
            lines_estimate = usage.count('\n') + 1 + (len(usage) // 50)
            h = (50 if is_small else 84) if lines_estimate > 1 else (28 if is_small else 42)
            layout.addWidget(self._code_block(usage, height=h))

        # 2. Parameters
        if params:
            layout.addWidget(self._bold_label(s.get("INFO_PARAMETERS", "Parameters:")))
            for p in params:
                name = p.get("name", "")
                ptype = p.get("type", "")
                pdesc = p.get("desc_vi", p.get("desc", "")) if self._lang == "vi" else p.get("desc", "")
                choices = p.get("choices")
                choices_html = ""
                if choices:
                    chips = " ".join(
                        f"<span style='background:#dbeafe; color:#1e40af; border-radius:4px; padding:1px 6px; font-weight:bold;'>{c}</span>"
                        for c in choices
                    )
                    choices_html = f" &nbsp;{chips}"
                line = QLabel(f"  <b style='color:#7c3aed;'>{name}</b>"
                              f" <span style='color:#64748b;'>({ptype})</span>"
                              f" – {pdesc}{choices_html}")
                line.setWordWrap(True)
                line.setTextFormat(Qt.RichText)
                f_size = 10 if is_small else 16
                line.setStyleSheet(
                    f"color: #334155; font-size: {f_size}px; background: transparent;"
                )
                layout.addWidget(line)

        # 3. Returns
        if returns:
            layout.addWidget(self._bold_label(s.get("INFO_RETURNS", "Returns:")))
            rtype = returns.get("type", "")
            rdesc = returns.get("desc_vi", returns.get("desc", "")) if self._lang == "vi" else returns.get("desc", "")
            ret_line = QLabel(
                f"  <b style='color:#059669;'>{rtype}</b> – {rdesc}"
            )
            ret_line.setWordWrap(True)
            ret_line.setTextFormat(Qt.RichText)
            f_size = 10 if is_small else 16
            ret_line.setStyleSheet(
                f"color: #334155; font-size: {f_size}px; background: transparent;"
            )
            layout.addWidget(ret_line)

        # 4. Source Code
        layout.addWidget(self._bold_label(s.get("INFO_SOURCE_CODE", "Source Code:")))
        source_text = self._load_source(info)
        if source_text:
            src_h = 120 if is_small else 200
            src_fs = 5 if is_small else 7
            layout.addWidget(self._code_block(source_text, height=src_h, dark=True, font_size=src_fs))
        else:
            no_src_fs = 9 if is_small else 13
            no_src = QLabel(s.get("INFO_NO_SOURCE", "Source code not available."))
            no_src.setStyleSheet(f"color: #94a3b8; font-size: {no_src_fs}px; background: transparent;")
            layout.addWidget(no_src)

    # ── Helpers ────────────────────────────────────────────

    def _bold_label(self, text):
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        f_size = 10 if self._is_small else 14
        lbl.setStyleSheet(
            f"color: #1e293b; font-size: {f_size}px; font-weight: 700; background: transparent;"
        )
        return lbl

    def _code_block(self, text, height=42, dark=False, font_size=8):
        box = QPlainTextEdit(text)
        box.setReadOnly(True)
        fs = max(5, font_size - 2) if self._is_small else font_size
        box.setFont(QFont("JetBrains Mono, Consolas, Courier New", fs))
        box.setFixedHeight(height)
        box.setMinimumWidth(50)  # Bypass NoWrap enforcing wide columns
        box.setLineWrapMode(
            QPlainTextEdit.NoWrap if dark
            else QPlainTextEdit.WidgetWidth
        )
        if dark:
            box.setStyleSheet("""
                QPlainTextEdit {
                    background: #0f172a;
                    color: #e2e8f0;
                    border: 1px solid #1e293b;
                    border-radius: 6px;
                    padding: 8px;
                    selection-background-color: #3b82f6;
                }
                QScrollBar:vertical { background:#1e293b; width:5px; border-radius:3px; }
                QScrollBar::handle:vertical { background:#334155; border-radius:3px; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
            """)
        else:
            box.setStyleSheet("""
                QPlainTextEdit {
                    background: #ede9fe;
                    color: #5b21b6;
                    border: 1px solid #ddd6fe;
                    border-radius: 6px;
                    padding: 6px 10px;
                }
            """)
        return box

    def _load_source(self, info):
        module_path = info.get("source_module")
        func_name   = info.get("source_func")
        if not module_path or not func_name:
            return None
        try:
            mod  = importlib.import_module(module_path)
            func = getattr(mod, func_name)
            return inspect.getsource(func)
        except Exception:
            return None


# ────────────────────────────────────────────────────────────
#  Toggle Arrow  —  gray, direction-only, darker bg on hover
# ────────────────────────────────────────────────────────────

class ToggleLabel(QLabel):
    """
    A QLabel arrow toggle (▼ / ▲).
    Gray at rest; slightly darker background on hover.
    Uses enterEvent/leaveEvent to avoid Qt platform hover override.
    """
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("▼", parent)
        self.setFixedSize(26, 26)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Show / hide details")
        self._expanded = False
        self._refresh(hovered=False)

    def set_expanded(self, expanded):
        self._expanded = expanded
        self.setText("▲" if expanded else "▼")
        self._refresh(hovered=False)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self._refresh(hovered=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._refresh(hovered=False)
        super().leaveEvent(event)

    def _refresh(self, hovered):
        bg = "rgba(0,0,0,0.10)" if hovered else "transparent"
        self.setStyleSheet(f"""
            background: {bg};
            color: #94a3b8;
            border-radius: 5px;
            font-size: 11px;
        """)


# ────────────────────────────────────────────────────────────
#  Draggable Function Block  (header row + dropdown)
# ────────────────────────────────────────────────────────────

class DraggableFunctionBlock(QFrame):
    expandRequested = pyqtSignal(object)

    def __init__(self, func_id, info, category_color, category_icon="🌣", is_small=False, lang="en", is_locked=False):
        super().__init__()
        self.func_id        = func_id
        self.info           = info
        self.category_color = category_color
        self.category_icon  = category_icon
        self._expanded      = False
        self._lang          = lang
        self._is_locked     = is_locked

        # Resolve translated description
        s = STRINGS.get(lang, STRINGS["en"])
        desc_key = _FN_DESC_KEY_MAP.get(func_id)
        if lang == "vi":
            translated_desc = info.get("desc_vi", info.get("desc", ""))
        elif desc_key:
            translated_desc = s.get(desc_key, info.get("desc", ""))
        else:
            translated_desc = info.get("desc", "")

        self.setObjectName("FunctionCard")
        self.setStyleSheet("""
            QFrame#FunctionCard { background: transparent; margin: 2px 8px; }
        """)

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)

        # ── Header row ──────────────────────────────────────
        self._header = QFrame()
        self._header.setObjectName("FunctionBlock")
        self._set_header_style(expanded=False)
        # Locked functions are not expandable (cursor stays arrow)
        if not is_locked:
            self._header.setCursor(Qt.PointingHandCursor)
        else:
            self._header.setCursor(Qt.ForbiddenCursor)

        row = QHBoxLayout(self._header)
        _rm = 6 if is_small else 10
        _rv = 6 if is_small else 12
        row.setContentsMargins(_rm, _rv, _rm, _rv)
        row.setSpacing(6 if is_small else 8)
        row.setAlignment(Qt.AlignTop)

        # Icon badge
        icon_lbl = QLabel(self.category_icon)
        icon_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        i_box = 24 if is_small else 36
        i_font = 12 if is_small else 18
        icon_lbl.setFixedSize(i_box, i_box)
        icon_lbl.setAlignment(Qt.AlignCenter)
        if is_locked:
            icon_lbl.setStyleSheet(f"""
                background-color: #94a3b8;
                color: #cbd5e1;
                border-radius: {'6px' if is_small else '10px'};
                font-size: {i_font}px;
                font-weight: bold;
            """)
        else:
            icon_lbl.setStyleSheet(f"""
                background-color: {category_color};
                color: #ffffff;
                border-radius: {'6px' if is_small else '10px'};
                font-size: {i_font}px;
                font-weight: bold;
            """)
        row.addWidget(icon_lbl, 0, Qt.AlignTop)

        # Name + desc
        text_box = QVBoxLayout()
        text_box.setSpacing(1)
        name_lbl = QLabel(func_id)
        name_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        n_size = 11 if is_small else 16
        if is_locked:
            name_lbl.setStyleSheet(
                f"font-weight: 700; color: #94a3b8; font-size: {n_size}px; background: transparent;"
            )
        else:
            name_lbl.setStyleSheet(
                f"font-weight: 700; color: #1e293b; font-size: {n_size}px; background: transparent;"
            )
        short_desc = QLabel(translated_desc)
        short_desc.setAttribute(Qt.WA_TransparentForMouseEvents)
        d_size = 9 if is_small else 14
        short_desc.setStyleSheet(
            f"color: #cbd5e1; font-size: {d_size}px; background: transparent;"
            if is_locked else
            f"color: #94a3b8; font-size: {d_size}px; background: transparent;"
        )
        short_desc.setWordWrap(True)
        text_box.addWidget(name_lbl)
        text_box.addWidget(short_desc)
        row.addLayout(text_box, stretch=1)

        if is_locked:
            # Show lock icon instead of expand arrow
            lock_lbl = QLabel("🔒")
            lock_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
            _lock_fs = 12 if is_small else 16
            lock_lbl.setStyleSheet(
                f"font-size: {_lock_fs}px; background: transparent; color: #94a3b8;"
            )
            row.addWidget(lock_lbl, 0, Qt.AlignTop)
        else:
            self._arrow = ToggleLabel()
            self._arrow.setAttribute(Qt.WA_TransparentForMouseEvents)
            row.addWidget(self._arrow, 0, Qt.AlignTop)

        if not is_locked:
            # 🖱️ Make the whole header clickable for smooth interaction
            self._header.mousePressEvent = self._on_header_pressed
            self._header.mouseReleaseEvent = self._on_header_released

        self._root.addWidget(self._header)

        # ── Info panel (hidden, not shown for locked functions) ──
        if not is_locked:
            self._panel = FunctionInfoPanel(func_id, info, category_color, is_small=is_small, lang=lang)
            self._panel.setVisible(False)
            self._root.addWidget(self._panel)

    def _on_header_pressed(self, event):
        self._drag_start_pos = event.pos()

    def _on_header_released(self, event):
        if hasattr(self, '_drag_start_pos'):
            # Only toggle if the mouse didn't move much (distinguishing click from drag)
            if (event.pos() - self._drag_start_pos).manhattanLength() < 5:
                self._toggle()

    # ── Toggle ──────────────────────────────────────────────

    def collapse(self):
        """Force-close this block if it's expanded."""
        if self._is_locked:
            return
        if self._expanded:
            self._expanded = False
            self._panel.setVisible(False)
            self._arrow.set_expanded(False)
            self._set_header_style(False)

    def _toggle(self):
        if self._is_locked:
            return
        # If we are about to expand, notify others to collapse
        if not self._expanded:
            self.expandRequested.emit(self)

        self._expanded = not self._expanded
        self._panel.setVisible(self._expanded)
        self._arrow.set_expanded(self._expanded)
        self._set_header_style(self._expanded)

    def _set_header_style(self, expanded):
        c = self.category_color
        if self._is_locked:
            # Locked: muted grey style, no hover effect
            self._header.setStyleSheet("""
                QFrame#FunctionBlock {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 10px;
                    opacity: 0.6;
                }
            """)
        elif expanded:
            self._header.setStyleSheet(f"""
                QFrame#FunctionBlock {{
                    background: white;
                    border: 1px solid {c};
                    border-bottom: none;
                    border-radius: 10px 10px 0 0;
                }}
            """)
        else:
            self._header.setStyleSheet("""
                QFrame#FunctionBlock {
                    background: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 10px;
                }
                QFrame#FunctionBlock:hover {
                    border-color: #c4b5fd;
                    background: #f3f0ff;
                }
            """)

    # ── Drag ────────────────────────────────────────────────

    def mouseMoveEvent(self, event):
        # Locked functions cannot be dragged into editor
        if self._is_locked:
            return
        if event.buttons() != Qt.LeftButton:
            return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(self.func_id)
        drag.setMimeData(mime)
        drag.setPixmap(self._header.grab())
        drag.setHotSpot(event.pos())
        drag.exec_(Qt.CopyAction)


# ────────────────────────────────────────────────────────────
#  Category Header
# ────────────────────────────────────────────────────────────

class CategoryHeader(QPushButton):
    def __init__(self, title, count, color, icon="📂", is_small=False, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(False)
        self.setFixedHeight(30 if is_small else 52)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 8px;
                padding-right: 0px;
                margin: 4px 8px 2px 8px;
            }}
            QPushButton:hover {{ background-color: {_darken_hex(color)}; }}
            QPushButton:checked:hover {{ background-color: {_darken_hex(color)}; }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 4, 0)
        layout.setSpacing(12)

        # 🚀 Icon Block (Left Side Tab)
        icon_box = QLabel(icon)
        i_h = 30 if is_small else 52
        i_font = 14 if is_small else 24
        icon_box.setFixedSize(34 if is_small else 50, i_h)
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setStyleSheet(f"""
            background: rgba(0, 0, 0, 0); 
            border-top-left-radius: 8px; 
            border-bottom-left-radius: 8px;
            font-size: {i_font}px;
        """)
        icon_box.setAttribute(Qt.WA_TransparentForMouseEvents)

        # 🏞️ Title Label
        title_lbl = QLabel(title)
        title_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        t_font = 12 if is_small else 18
        title_lbl.setStyleSheet(
            f"color: white; background: transparent; font-weight: 900; font-size: {t_font}px; letter-spacing: 1px;"
        )
        title_lbl.setAlignment(Qt.AlignVCenter)

        # Count badge - Fixed width for alignment
        count_lbl = QLabel(str(count))
        count_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        c_font = 10 if is_small else 14
        c_width = 45 if is_small else 65
        count_lbl.setFixedWidth(c_width)
        count_lbl.setAlignment(Qt.AlignCenter)
        count_lbl.setStyleSheet(f"""
            background: rgba(255,255,255,0.25);
            border-radius: 6px;
            padding: 4px 8px;
            font-size: {c_font}px;
            font-weight: bold;
            color: white;
        """)

        layout.addWidget(icon_box)
        layout.addWidget(title_lbl)
        layout.addStretch()
        layout.addWidget(count_lbl)


# ────────────────────────────────────────────────────────────
#  Populate the Functions Tab
# ────────────────────────────────────────────────────────────

def populate_functions_tab(running_mode_widget, is_small=False, lang="en", unlocked_functions=None):
    """Populate the functions tab with lock-aware function blocks.
    
    Args:
        running_mode_widget: The widget containing functionsListLayout
        is_small: Whether to use compact sizing
        lang: Language code ('en' or 'vi')
        unlocked_functions: Set of unlocked function IDs for LOCKED_CATEGORIES.
                            Functions in ALWAYS_UNLOCKED_CATEGORIES are always shown.
                            If None, ALL functions are unlocked (no lock system).
    """
    layout = running_mode_widget.findChild(QVBoxLayout, "functionsListLayout")

    # Remove all existing items (widgets + spacers) and disconnect signals
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            widget = item.widget()
            # Disconnect all signals to prevent memory leaks and duplicate connections
            try:
                widget.clicked.disconnect()
            except:
                pass
            widget.setParent(None)
            widget.deleteLater()

    # Pin content to top — critical so collapsed headers sit at top, not center
    layout.setAlignment(Qt.AlignTop)

    s = STRINGS.get(lang, STRINGS["en"])

    # 🤝 ACCORDION MANAGERS
    all_blocks = []
    all_category_containers = []
    all_category_buttons = []

    def collapse_all_blocks(except_block):
        for block in all_blocks:
            if block != except_block:
                block.collapse()

    def on_category_clicked(checked, clicked_header, clicked_container):
        print(f"🔍 Category clicked: checked={checked}, header={clicked_header.text() if hasattr(clicked_header, 'text') else 'unknown'}")
        if checked:
            # 1. Collapse all other categories (ACCORDION BEHAVIOR)
            for btn, cont in zip(all_category_buttons, all_category_containers):
                if btn != clicked_header:
                    btn.setChecked(False)
                    cont.setVisible(False)
                    print(f"  ✅ Collapsed: {btn.text() if hasattr(btn, 'text') else 'unknown'}")
            # 2. Collapse all function blocks for a fresh start
            collapse_all_blocks(None)
            clicked_container.setVisible(True)
            print(f"  ✅ Opened clicked container")
        else:
            clicked_container.setVisible(False)
            print(f"  ✅ Closed clicked container")

    for cat_name, cat_data in LIBRARY_FUNCTIONS.items():
        color = cat_data["color"]
        icon  = cat_data.get("icon", "📂")
        functions = cat_data["functions"]

        # Determine lock state for this category
        cat_always_open = cat_name in ALWAYS_UNLOCKED_CATEGORIES
        cat_locked = cat_name in LOCKED_CATEGORIES

        # Translate category name
        cat_key = _CAT_KEY_MAP.get(cat_name)
        display_name = s.get(cat_key, cat_name) if cat_key else cat_name

        # Count unlocked functions for badge
        if unlocked_functions is None or cat_always_open:
            unlocked_count = len(functions)
        else:
            unlocked_count = sum(
                1 for fid in functions if fid in (unlocked_functions or set())
            )
        total_count = len(functions)
        
        # Show lock indicator on category header if some functions are locked
        # Always show "X/Y" format for consistency and visual alignment
        if cat_locked and unlocked_functions is not None:
            # Show count as "unlocked/total" to show progress
            display_count = f"{unlocked_count}/{total_count}"
        elif cat_always_open:
            # For always-unlocked categories, show "total/total" (e.g., "8/8", "5/5")
            display_count = f"{total_count}/{total_count}"
        else:
            # Fallback: just show total
            display_count = f"{total_count}/{total_count}"

        header = CategoryHeader(display_name, display_count, color, icon=icon, is_small=is_small, parent=running_mode_widget)
        layout.addWidget(header)
        all_category_buttons.append(header)

        container = QWidget(running_mode_widget)
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 2, 0, 6)
        container_layout.setSpacing(4)
        container.setVisible(False)  # IMPORTANT: Start hidden
        container.setWindowFlags(Qt.Widget)  # Ensure it's not a separate window
        all_category_containers.append(container)

        # FIX: Use default arguments to capture current values in closure
        header.clicked.connect(lambda chk, h=header, c=container: on_category_clicked(chk, h, c))

        for func_id, info in functions.items():
            # Determine if this specific function is locked
            if unlocked_functions is None or cat_always_open:
                is_locked = False
            elif cat_locked:
                is_locked = func_id not in unlocked_functions
            else:
                is_locked = False

            block = DraggableFunctionBlock(
                func_id=func_id,
                info=info,
                category_color=color,
                category_icon=icon,
                is_small=is_small,
                lang=lang,
                is_locked=is_locked
            )
            all_blocks.append(block)
            if not is_locked:
                block.expandRequested.connect(collapse_all_blocks)
            container_layout.addWidget(block)

        # Add container to layout AFTER it's fully populated
        layout.addWidget(container)
    
    # ✅ SIMPLE APPROACH: No auto-expand, just unlock functions
    # Users can manually open categories to see unlocked functions
    print(f"✅ Function sidebar populated. {len(unlocked_functions) if unlocked_functions else 0} functions unlocked.")