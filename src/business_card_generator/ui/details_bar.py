"""Details bar widget for editing field properties.

This module provides the DetailsBar widget that displays and allows editing
of the selected field's styling properties (font, color, size, etc.).
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QGroupBox,
    QPushButton,
    QColorDialog,
    QFrame,
    QScrollArea,
    QComboBox,
    QCheckBox,
    QHBoxLayout,
)

from src.business_card_generator.models.card import FieldDefinition, FieldType


class ColorButton(QPushButton):
    """A button that displays and allows selection of a color."""
    
    color_changed = Signal(str)
    
    def __init__(self, initial_color: str = "#000000", parent: QWidget = None):
        super().__init__(parent)
        self._color = initial_color
        self._update_style()
        self.clicked.connect(self._on_clicked)
        self.setFixedSize(60, 25)
        self.setToolTip("Click to select a color")
    
    @property
    def color(self) -> str:
        return self._color
    
    @color.setter
    def color(self, value: str) -> None:
        self._color = value
        self._update_style()
    
    def _update_style(self) -> None:
        qcolor = QColor(self._color)
        luminance = (0.299 * qcolor.red() + 0.587 * qcolor.green() + 0.114 * qcolor.blue()) / 255
        text_color = "#000000" if luminance > 0.5 else "#FFFFFF"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                color: {text_color};
                border: 1px solid #888888;
                border-radius: 3px;
            }}
            QPushButton:hover {{ border: 2px solid #0078d4; }}
        """)
        self.setText(self._color)
    
    def _on_clicked(self) -> None:
        color = QColorDialog.getColor(QColor(self._color), self, "Select Color")
        if color.isValid():
            self._color = color.name()
            self._update_style()
            self.color_changed.emit(self._color)


class DetailsBar(QWidget):
    """Property editor panel for selected field.
    
    Displays and allows editing of field styling properties.
    
    Signals:
        field_changed: Emitted when a field property is changed (field_id).
    """
    
    field_changed = Signal(str)  # field_id
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._current_field: Optional[FieldDefinition] = None
        self._updating = False
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Title
        title_label = QLabel("Field Properties")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        main_layout.addWidget(title_label)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        main_layout.addWidget(separator)
        
        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(15)
        
        # Placeholder
        self._placeholder = QLabel("Select a field on the card to edit its properties.")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet("color: #888888; font-style: italic; padding: 20px;")
        self._placeholder.setWordWrap(True)
        content_layout.addWidget(self._placeholder)
        
        # Form container
        self._form = QWidget()
        form_layout = QVBoxLayout(self._form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(15)
        
        # Field info group
        info_group = QGroupBox("Field Info")
        info_layout = QFormLayout(info_group)
        
        self._name_edit = QLineEdit()
        self._name_edit.setToolTip("Field name (editable)")
        self._name_edit.editingFinished.connect(self._on_name_changed)
        info_layout.addRow("Name:", self._name_edit)
        
        self._type_label = QLabel()
        info_layout.addRow("Type:", self._type_label)
        
        form_layout.addWidget(info_group)
        
        # Position group
        pos_group = QGroupBox("Position & Size")
        pos_layout = QFormLayout(pos_group)
        
        self._x_spin = QSpinBox()
        self._x_spin.setRange(0, 336)
        self._x_spin.setToolTip("X position on card")
        self._x_spin.valueChanged.connect(lambda v: self._on_property_changed("x", v))
        pos_layout.addRow("X:", self._x_spin)
        
        self._y_spin = QSpinBox()
        self._y_spin.setRange(0, 192)
        self._y_spin.setToolTip("Y position on card")
        self._y_spin.valueChanged.connect(lambda v: self._on_property_changed("y", v))
        pos_layout.addRow("Y:", self._y_spin)
        
        self._width_spin = QSpinBox()
        self._width_spin.setRange(10, 336)
        self._width_spin.setToolTip("Field width")
        self._width_spin.valueChanged.connect(lambda v: self._on_property_changed("width", v))
        pos_layout.addRow("Width:", self._width_spin)
        
        self._height_spin = QSpinBox()
        self._height_spin.setRange(10, 192)
        self._height_spin.setToolTip("Field height")
        self._height_spin.valueChanged.connect(lambda v: self._on_property_changed("height", v))
        pos_layout.addRow("Height:", self._height_spin)
        
        form_layout.addWidget(pos_group)
        
        # Text styling group (only for text fields)
        self._style_group = QGroupBox("Text Styling")
        style_layout = QFormLayout(self._style_group)
        
        self._font_family = QComboBox()
        self._font_family.addItems([
            "Arial", "Helvetica", "Times New Roman", "Georgia",
            "Verdana", "Courier New", "Trebuchet MS"
        ])
        self._font_family.setToolTip("Font family")
        self._font_family.currentTextChanged.connect(
            lambda v: self._on_property_changed("font_family", v)
        )
        style_layout.addRow("Font:", self._font_family)
        
        self._font_size = QSpinBox()
        self._font_size.setRange(6, 72)
        self._font_size.setSuffix(" pt")
        self._font_size.setToolTip("Font size")
        self._font_size.valueChanged.connect(
            lambda v: self._on_property_changed("font_size", v)
        )
        style_layout.addRow("Size:", self._font_size)
        
        style_widget = QWidget()
        style_h_layout = QHBoxLayout(style_widget)
        style_h_layout.setContentsMargins(0, 0, 0, 0)
        
        self._bold_check = QCheckBox("Bold")
        self._bold_check.stateChanged.connect(
            lambda s: self._on_property_changed("font_bold", s == 2)
        )
        style_h_layout.addWidget(self._bold_check)
        
        self._italic_check = QCheckBox("Italic")
        self._italic_check.stateChanged.connect(
            lambda s: self._on_property_changed("font_italic", s == 2)
        )
        style_h_layout.addWidget(self._italic_check)
        style_h_layout.addStretch()
        
        style_layout.addRow("Style:", style_widget)
        
        self._font_color = ColorButton("#000000")
        self._font_color.color_changed.connect(
            lambda c: self._on_property_changed("font_color", c)
        )
        style_layout.addRow("Color:", self._font_color)
        
        form_layout.addWidget(self._style_group)
        form_layout.addStretch()
        
        self._form.hide()
        content_layout.addWidget(self._form)
        
        scroll_area.setWidget(content)
        main_layout.addWidget(scroll_area)
        
        self.setMinimumWidth(250)
        self.setToolTip("Edit properties of the selected field")
        self.setStyleSheet("""
            DetailsBar { background-color: #f8f8f8; }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
    
    def set_field(self, field: FieldDefinition) -> None:
        """Display and edit the given field's properties."""
        self._current_field = field
        self._updating = True
        
        try:
            self._name_edit.setText(field.name)
            self._type_label.setText("Text" if field.field_type == FieldType.TEXT else "Image")
            
            self._x_spin.setValue(field.x)
            self._y_spin.setValue(field.y)
            self._width_spin.setValue(field.width)
            self._height_spin.setValue(field.height)
            
            self._font_family.setCurrentText(field.font_family)
            self._font_size.setValue(field.font_size)
            self._bold_check.setChecked(field.font_bold)
            self._italic_check.setChecked(field.font_italic)
            self._font_color.color = field.font_color
            
            # Show/hide text styling based on field type
            self._style_group.setVisible(field.field_type == FieldType.TEXT)
            
            self._placeholder.hide()
            self._form.show()
        finally:
            self._updating = False
    
    def _on_name_changed(self) -> None:
        """Handle name field editing finished."""
        if self._updating or not self._current_field:
            return
        
        new_name = self._name_edit.text().strip()
        if new_name and new_name != self._current_field.name:
            self._current_field.name = new_name
            self.field_changed.emit(self._current_field.id)
    
    def clear(self) -> None:
        """Clear the form and show placeholder."""
        self._current_field = None
        self._form.hide()
        self._placeholder.show()
    
    def _on_property_changed(self, prop: str, value) -> None:
        if self._updating or not self._current_field:
            return
        
        setattr(self._current_field, prop, value)
        self.field_changed.emit(self._current_field.id)
    
    def get_current_field(self) -> Optional[FieldDefinition]:
        return self._current_field
