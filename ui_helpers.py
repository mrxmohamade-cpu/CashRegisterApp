"""Shared UI helper classes for CashRegisterApp."""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import QPoint, QRect, QSize, Qt
from PyQt6.QtWidgets import QLayout, QLayoutItem, QStyle


class FlowLayout(QLayout):
    """A Qt layout that arranges child widgets like text in a paragraph.

    Widgets flow from right-to-left or left-to-right depending on the
    alignment that is provided. When there isn't enough horizontal space,
    widgets wrap automatically to the next row. This is useful for creating
    responsive button rows and statistic card sections that adapt to window
    size changes.
    """

    def __init__(
        self,
        parent=None,
        margin: int = 0,
        spacing: int = -1,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
    ) -> None:
        super().__init__(parent)
        self._items: List[QLayoutItem] = []
        self._alignment: Qt.AlignmentFlag = alignment
        self._hspacing: int = spacing
        self._vspacing: int = spacing
        self.setContentsMargins(margin, margin, margin, margin)

    # --- QLayout API -------------------------------------------------
    def addItem(self, item: QLayoutItem) -> None:  # type: ignore[override]
        self._items.append(item)

    def count(self) -> int:  # type: ignore[override]
        return len(self._items)

    def itemAt(self, index: int) -> Optional[QLayoutItem]:  # type: ignore[override]
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index: int) -> Optional[QLayoutItem]:  # type: ignore[override]
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self) -> Qt.Orientations:  # type: ignore[override]
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self) -> bool:  # type: ignore[override]
        return True

    def heightForWidth(self, width: int) -> int:  # type: ignore[override]
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect: QRect) -> None:  # type: ignore[override]
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self) -> QSize:  # type: ignore[override]
        return self.minimumSize()

    def minimumSize(self) -> QSize:  # type: ignore[override]
        size = QSize()
        for item in self._items:
            item_size = item.minimumSize()
            size = size.expandedTo(item_size)
        left, top, right, bottom = self.getContentsMargins()
        size += QSize(left + right, top + bottom)
        return size

    # --- Customisation helpers --------------------------------------
    def setAlignment(self, alignment: Qt.AlignmentFlag) -> None:
        self._alignment = alignment
        self.invalidate()

    def setSpacing(self, spacing: int) -> None:  # type: ignore[override]
        self._hspacing = spacing
        self._vspacing = spacing
        super().setSpacing(spacing)

    # --- Internal helpers -------------------------------------------
    def _horizontal_spacing(self) -> int:
        if self._hspacing >= 0:
            return self._hspacing
        spacing = self.spacing()
        if spacing >= 0:
            return spacing
        return self._smart_spacing(QStyle.PixelMetric.PM_LayoutHorizontalSpacing)

    def _vertical_spacing(self) -> int:
        if self._vspacing >= 0:
            return self._vspacing
        spacing = self.spacing()
        if spacing >= 0:
            return spacing
        return self._smart_spacing(QStyle.PixelMetric.PM_LayoutVerticalSpacing)

    def _smart_spacing(self, pm: QStyle.PixelMetric) -> int:
        parent = self.parent()
        if parent is None:
            return 8
        if isinstance(parent, QLayout):
            spacing = parent.spacing()
            return spacing if spacing >= 0 else 8
        if hasattr(parent, "style"):
            style = parent.style()  # type: ignore[attr-defined]
            if style is not None:
                return style.pixelMetric(pm, None, parent)  # type: ignore[arg-type]
        return 8

    def _do_layout(self, rect: QRect, *, test_only: bool) -> int:
        if not self._items:
            left, top, right, bottom = self.getContentsMargins()
            return top + bottom

        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(+left, +top, -right, -bottom)
        max_width = effective_rect.width()
        if max_width <= 0:
            max_width = 10 ** 9

        space_x = self._horizontal_spacing()
        space_y = self._vertical_spacing()

        rows: List[tuple[List[QLayoutItem], int, int]] = []
        current_row: List[QLayoutItem] = []
        row_width = 0
        row_height = 0

        for item in self._items:
            hint = item.sizeHint()
            item_width = hint.width()
            item_height = hint.height()

            proposed_width = item_width if not current_row else row_width + space_x + item_width
            if current_row and proposed_width > max_width:
                rows.append((current_row, row_width, row_height))
                current_row = []
                row_width = 0
                row_height = 0

            if current_row:
                row_width += space_x + item_width
            else:
                row_width += item_width
            row_height = max(row_height, item_height)
            current_row.append(item)

        if current_row:
            rows.append((current_row, row_width, row_height))

        y = effective_rect.y()
        for row_index, (items, row_width, row_height) in enumerate(rows):
            if self._alignment & Qt.AlignmentFlag.AlignRight:
                start_x = effective_rect.x() + max(0, effective_rect.width() - row_width)
            elif self._alignment & Qt.AlignmentFlag.AlignHCenter:
                start_x = effective_rect.x() + max(0, (effective_rect.width() - row_width) // 2)
            else:
                start_x = effective_rect.x()

            x = start_x
            for item in items:
                hint = item.sizeHint()
                if not test_only:
                    item.setGeometry(QRect(QPoint(int(x), int(y)), hint))
                x += hint.width() + space_x

            y += row_height
            if row_index != len(rows) - 1:
                y += space_y

        total_height = (y - effective_rect.y()) + top + bottom
        return total_height

