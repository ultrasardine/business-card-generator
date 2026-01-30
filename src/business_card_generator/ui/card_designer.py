"""Card designer canvas widget for visual card editing.

This module provides the CardDesigner widget that displays a card preview
based on the template layout and selected row data.
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPixmap, QAction
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QLabel, QMenu
)

from src.business_card_generator.models.card import FieldDefinition, FieldType, CardRow
from src.business_card_generator.core.card_data_model import CardDataModel


# Standard business card dimensions (in pixels at 96 DPI)
# Standard card is 3.5" x 2" = 336 x 192 pixels
CARD_WIDTH = 336
CARD_HEIGHT = 192


class FieldWidget(QLabel):
    """Widget representing a field on the card preview.
    
    Can be dragged to reposition the field in the template.
    """
    
    position_changed = Signal(str, int, int)  # field_id, x, y
    selected = Signal(str)  # field_id
    context_menu_requested = Signal(str, object)  # field_id, QPoint (global pos)
    
    def __init__(self, field_def: FieldDefinition, parent: QWidget = None):
        super().__init__(parent)
        self._field_def = field_def
        self._dragging = False
        self._drag_start = None
        
        self.setGeometry(field_def.x, field_def.y, field_def.width, field_def.height)
        self._update_style()
        self.setToolTip(f"{field_def.name} - drag to reposition, right-click for options")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
    
    @property
    def field_def(self) -> FieldDefinition:
        return self._field_def
    
    def _on_context_menu(self, pos) -> None:
        """Handle context menu request."""
        self.selected.emit(self._field_def.id)
        self.context_menu_requested.emit(self._field_def.id, self.mapToGlobal(pos))
    
    def set_value(self, value: str) -> None:
        """Set the displayed value."""
        if self._field_def.field_type == FieldType.IMAGE:
            if value:
                pixmap = QPixmap(value)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        self._field_def.width, self._field_def.height,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.setPixmap(scaled)
                else:
                    self.setText(f"[{self._field_def.name}]")
            else:
                self.setText(f"[{self._field_def.name}]")
        else:
            self.setText(value if value else f"[{self._field_def.name}]")
    
    def _update_style(self) -> None:
        """Update widget style based on field definition."""
        fd = self._field_def
        font = QFont(fd.font_family, fd.font_size)
        font.setBold(fd.font_bold)
        font.setItalic(fd.font_italic)
        self.setFont(font)
        
        self.setStyleSheet(f"""
            QLabel {{
                color: {fd.font_color};
                background-color: transparent;
                border: 1px dashed #cccccc;
                padding: 2px;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    
    def set_selected(self, selected: bool) -> None:
        """Set selection state."""
        fd = self._field_def
        border = "2px solid #0078d4" if selected else "1px dashed #cccccc"
        self.setStyleSheet(f"""
            QLabel {{
                color: {fd.font_color};
                background-color: transparent;
                border: {border};
                padding: 2px;
            }}
        """)
    
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start = event.pos()
            self.selected.emit(self._field_def.id)
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event) -> None:
        if self._dragging and self._drag_start:
            delta = event.pos() - self._drag_start
            new_x = max(0, min(self.x() + delta.x(), CARD_WIDTH - self.width()))
            new_y = max(0, min(self.y() + delta.y(), CARD_HEIGHT - self.height()))
            self.move(new_x, new_y)
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event) -> None:
        if self._dragging:
            self._dragging = False
            self._field_def.x = self.x()
            self._field_def.y = self.y()
            self.position_changed.emit(self._field_def.id, self.x(), self.y())
        super().mouseReleaseEvent(event)


class CardCanvas(QFrame):
    """The card preview area where fields are displayed."""
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setFixedSize(CARD_WIDTH, CARD_HEIGHT)
        self.setStyleSheet("""
            CardCanvas {
                background-color: #FFFFFF;
                border: 1px solid #cccccc;
            }
        """)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        self.setToolTip("Business card preview - drag fields to reposition")
    
    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw subtle grid
        pen = QPen(QColor(240, 240, 240))
        pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen)
        
        for x in range(50, CARD_WIDTH, 50):
            painter.drawLine(x, 0, x, CARD_HEIGHT)
        for y in range(50, CARD_HEIGHT, 50):
            painter.drawLine(0, y, CARD_WIDTH, y)
        
        painter.end()


class CardDesigner(QWidget):
    """Visual card preview showing template layout with row data.
    
    Displays fields from the template positioned on a card canvas.
    When a row is selected, shows that row's data in each field.
    Fields can be dragged to reposition them in the template.
    
    Signals:
        field_position_changed: Emitted when a field is repositioned (field_id, x, y).
        field_selected: Emitted when a field is clicked (field_id).
        field_added: Emitted when a field is added via paste (field_id).
    """
    
    field_position_changed = Signal(str, int, int)
    field_selected = Signal(str)
    field_added = Signal(str)
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        
        self._model: Optional[CardDataModel] = None
        self._current_row: Optional[CardRow] = None
        self._field_widgets: dict[str, FieldWidget] = {}
        self._selected_field_id: Optional[str] = None
        self._project_path: Optional[str] = None  # For resolving relative image paths
        self._clipboard: Optional[FieldDefinition] = None  # For copy/paste
        
        self._setup_ui()
    
    def set_project_path(self, path: Optional[str]) -> None:
        """Set the project path for resolving relative image paths."""
        self._project_path = path
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Info label
        self._info_label = QLabel("Select a row to preview the card")
        self._info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._info_label.setStyleSheet("color: #888888; font-style: italic;")
        layout.addWidget(self._info_label)
        
        # Card canvas
        self._canvas = CardCanvas(self)
        layout.addWidget(self._canvas, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setStyleSheet("CardDesigner { background-color: #f0f0f0; }")
        self.setMinimumSize(400, 300)
        self.setToolTip("Card Designer - preview and arrange fields on the card")
    
    def set_model(self, model: CardDataModel) -> None:
        """Set the data model and rebuild field widgets."""
        if self._model:
            self._model.template_changed.disconnect(self._on_template_changed)
        
        self._model = model
        self._model.template_changed.connect(self._on_template_changed)
        self._rebuild_field_widgets()
    
    def _on_template_changed(self) -> None:
        """Handle template structure changes."""
        self._rebuild_field_widgets()
        if self._current_row:
            self._update_field_values()
    
    def _rebuild_field_widgets(self) -> None:
        """Rebuild all field widgets from the template."""
        # Clear existing widgets
        for widget in self._field_widgets.values():
            widget.deleteLater()
        self._field_widgets.clear()
        self._selected_field_id = None
        
        if not self._model:
            return
        
        # Create widget for each field, sorted by z_index
        sorted_fields = self._model.get_fields_sorted_by_z_index()
        for field_def in sorted_fields:
            widget = FieldWidget(field_def, self._canvas)
            widget.position_changed.connect(self._on_field_position_changed)
            widget.selected.connect(self._on_field_selected)
            widget.context_menu_requested.connect(self._show_context_menu)
            widget.show()
            self._field_widgets[field_def.id] = widget
        
        # Ensure z-order is correct by raising widgets in order
        for field_def in sorted_fields:
            if field_def.id in self._field_widgets:
                self._field_widgets[field_def.id].raise_()
    
    def _show_context_menu(self, field_id: str, global_pos) -> None:
        """Show context menu for a field."""
        menu = QMenu(self)
        
        # Copy/Cut/Paste actions
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(lambda: self._copy_field(field_id))
        menu.addAction(copy_action)
        
        cut_action = QAction("Cut", self)
        cut_action.triggered.connect(lambda: self._cut_field(field_id))
        menu.addAction(cut_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setEnabled(self._clipboard is not None)
        paste_action.triggered.connect(self._paste_field)
        menu.addAction(paste_action)
        
        menu.addSeparator()
        
        # Z-order actions
        bring_front_action = QAction("Bring to Front", self)
        bring_front_action.triggered.connect(lambda: self._bring_to_front(field_id))
        menu.addAction(bring_front_action)
        
        bring_forward_action = QAction("Bring Forward", self)
        bring_forward_action.triggered.connect(lambda: self._bring_forward(field_id))
        menu.addAction(bring_forward_action)
        
        send_backward_action = QAction("Send Backward", self)
        send_backward_action.triggered.connect(lambda: self._send_backward(field_id))
        menu.addAction(send_backward_action)
        
        send_back_action = QAction("Send to Back", self)
        send_back_action.triggered.connect(lambda: self._send_to_back(field_id))
        menu.addAction(send_back_action)
        
        menu.exec(global_pos)
    
    def _copy_field(self, field_id: str) -> None:
        """Copy a field to clipboard."""
        field = self._model.get_field_by_id(field_id)
        if field:
            self._clipboard = field.copy()
    
    def _cut_field(self, field_id: str) -> None:
        """Cut a field (copy and remove)."""
        field = self._model.get_field_by_id(field_id)
        if field:
            self._clipboard = field.copy()
            self._model.remove_field(field_id)
    
    def _paste_field(self) -> None:
        """Paste a field from clipboard, centered in the preview."""
        if not self._clipboard or not self._model:
            return
        
        # Create a copy of the clipboard field
        new_field = self._clipboard.copy()
        
        # Generate unique name
        new_field.name = self._model.get_unique_field_name(self._clipboard.name)
        
        # Center the field in the preview
        new_field.x = (CARD_WIDTH - new_field.width) // 2
        new_field.y = (CARD_HEIGHT - new_field.height) // 2
        
        # Set z_index to be on top
        new_field.z_index = self._model.get_max_z_index() + 1
        
        # Add to model
        self._model.add_field_definition(new_field)
        
        # Select the new field
        self._on_field_selected(new_field.id)
        self.field_added.emit(new_field.id)
    
    def _bring_to_front(self, field_id: str) -> None:
        """Bring field to front."""
        if self._model:
            self._model.bring_to_front(field_id)
    
    def _bring_forward(self, field_id: str) -> None:
        """Bring field one step forward."""
        if self._model:
            self._model.bring_forward(field_id)
    
    def _send_backward(self, field_id: str) -> None:
        """Send field one step backward."""
        if self._model:
            self._model.send_backward(field_id)
    
    def _send_to_back(self, field_id: str) -> None:
        """Send field to back."""
        if self._model:
            self._model.send_to_back(field_id)
    
    def set_row(self, row: Optional[CardRow]) -> None:
        """Set the current row to display."""
        self._current_row = row
        self._update_field_values()
        
        if row:
            self._info_label.hide()
        else:
            self._info_label.show()
    
    def _update_field_values(self) -> None:
        """Update field widgets with current row data."""
        for field_id, widget in self._field_widgets.items():
            if self._current_row:
                value = self._current_row.get_value(field_id)
                # Resolve relative paths for images
                if value and self._project_path and widget.field_def.field_type == FieldType.IMAGE:
                    if not Path(value).is_absolute():
                        value = str(Path(self._project_path) / value)
                widget.set_value(str(value) if value else "")
            else:
                widget.set_value("")
    
    def _on_field_position_changed(self, field_id: str, x: int, y: int) -> None:
        """Handle field widget position change."""
        if self._model:
            self._model.update_field_position(field_id, x, y)
        self.field_position_changed.emit(field_id, x, y)
    
    def _on_field_selected(self, field_id: str) -> None:
        """Handle field selection."""
        # Deselect previous
        if self._selected_field_id and self._selected_field_id in self._field_widgets:
            self._field_widgets[self._selected_field_id].set_selected(False)
        
        # Select new
        self._selected_field_id = field_id
        if field_id in self._field_widgets:
            self._field_widgets[field_id].set_selected(True)
        
        self.field_selected.emit(field_id)
    
    def get_selected_field_id(self) -> Optional[str]:
        """Return the currently selected field ID."""
        return self._selected_field_id
    
    def clear_selection(self) -> None:
        """Clear field selection."""
        if self._selected_field_id and self._selected_field_id in self._field_widgets:
            self._field_widgets[self._selected_field_id].set_selected(False)
        self._selected_field_id = None
    
    def clear(self) -> None:
        """Clear the current row display."""
        self._current_row = None
        self._update_field_values()
        self._info_label.show()
    
    @property
    def card_width(self) -> int:
        return CARD_WIDTH
    
    @property
    def card_height(self) -> int:
        return CARD_HEIGHT
