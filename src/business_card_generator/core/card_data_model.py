"""Qt table model for template-based business card data.

This module provides a QAbstractTableModel where columns are defined
by the CardTemplate's fields, and rows are CardRow instances.
"""

from typing import Any, Optional
import uuid

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    Qt,
    Signal,
)

from ..models.card import CardTemplate, CardRow, FieldDefinition, FieldType


class CardDataModel(QAbstractTableModel):
    """Qt model for template-based card data.
    
    Columns are dynamically defined by the CardTemplate's fields.
    Rows are CardRow instances containing data for each field.
    
    Signals:
        template_changed: Emitted when the template structure changes.
        field_added: Emitted when a new field is added (field_id).
        field_removed: Emitted when a field is removed (field_id).
    """
    
    template_changed = Signal()
    field_added = Signal(str)  # field_id
    field_removed = Signal(str)  # field_id
    
    def __init__(self, parent: Optional[QObject] = None):
        """Initialize with empty template and no rows."""
        super().__init__(parent)
        self._template = CardTemplate()
        self._rows: list[CardRow] = []
        
        # Add default fields
        self._add_default_fields()
    
    def _add_default_fields(self) -> None:
        """Add default fields to a new template."""
        defaults = [
            ("Name", FieldType.TEXT, 10, 10, 150, 25),
            ("Title", FieldType.TEXT, 10, 40, 150, 20),
            ("Company", FieldType.TEXT, 10, 65, 150, 20),
            ("Email", FieldType.TEXT, 10, 95, 150, 18),
            ("Phone", FieldType.TEXT, 10, 118, 150, 18),
            ("Photo", FieldType.IMAGE, 220, 10, 80, 80),
        ]
        for name, ftype, x, y, w, h in defaults:
            field_def = FieldDefinition(
                name=name, field_type=ftype,
                x=x, y=y, width=w, height=h,
                font_size=12 if ftype == FieldType.TEXT else 12
            )
            self._template.fields.append(field_def)
    
    # Qt Model Interface
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._rows)
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._template.fields)
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        
        row_idx = index.row()
        col_idx = index.column()
        
        if row_idx < 0 or row_idx >= len(self._rows):
            return None
        if col_idx < 0 or col_idx >= len(self._template.fields):
            return None
        
        row = self._rows[row_idx]
        field_def = self._template.fields[col_idx]
        
        if role in (Qt.DisplayRole, Qt.EditRole):
            return row.get_value(field_def.id)
        
        return None
    
    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if not index.isValid() or role != Qt.EditRole:
            return False
        
        row_idx = index.row()
        col_idx = index.column()
        
        if row_idx < 0 or row_idx >= len(self._rows):
            return False
        if col_idx < 0 or col_idx >= len(self._template.fields):
            return False
        
        row = self._rows[row_idx]
        field_def = self._template.fields[col_idx]
        row.set_value(field_def.id, value)
        
        self.dataChanged.emit(index, index, [role])
        return True
    
    def headerData(self, section: int, orientation: Qt.Orientation, 
                   role: int = Qt.DisplayRole) -> Any:
        if orientation == Qt.Horizontal:
            if 0 <= section < len(self._template.fields):
                field_def = self._template.fields[section]
                if role == Qt.DisplayRole:
                    return field_def.name
                elif role == Qt.ToolTipRole:
                    type_str = "text" if field_def.field_type == FieldType.TEXT else "image"
                    return f"{field_def.name} ({type_str} field)"
        elif orientation == Qt.Vertical:
            if role == Qt.DisplayRole:
                return str(section + 1)
        return None
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
    
    # Template Management
    def get_template(self) -> CardTemplate:
        """Return the current template."""
        return self._template
    
    def set_template(self, template: CardTemplate) -> None:
        """Set a new template, resetting the model."""
        self.beginResetModel()
        self._template = template
        self._rows.clear()
        self.endResetModel()
        self.template_changed.emit()
    
    def add_field(self, name: str, field_type: FieldType = FieldType.TEXT) -> str:
        """Add a new field/column to the template.
        
        Returns the new field's ID.
        """
        col = len(self._template.fields)
        
        # Default dimensions based on field type
        width = 100 if field_type == FieldType.TEXT else 80
        height = 25 if field_type == FieldType.TEXT else 80
        
        # Center the field in the card preview
        from src.business_card_generator.ui.card_designer import CARD_WIDTH, CARD_HEIGHT
        x = (CARD_WIDTH - width) // 2
        y = (CARD_HEIGHT - height) // 2
        
        # Set z_index to be on top
        z_index = self.get_max_z_index() + 1 if self._template.fields else 0
        
        field_def = FieldDefinition(
            name=name,
            field_type=field_type,
            x=x, y=y,
            width=width, height=height,
            z_index=z_index
        )
        
        self.beginInsertColumns(QModelIndex(), col, col)
        self._template.fields.append(field_def)
        self.endInsertColumns()
        
        self.field_added.emit(field_def.id)
        self.template_changed.emit()
        return field_def.id
    
    def remove_field(self, field_id: str) -> bool:
        """Remove a field/column from the template."""
        for idx, field_def in enumerate(self._template.fields):
            if field_def.id == field_id:
                self.beginRemoveColumns(QModelIndex(), idx, idx)
                self._template.fields.pop(idx)
                # Remove data from all rows
                for row in self._rows:
                    row.data.pop(field_id, None)
                self.endRemoveColumns()
                
                self.field_removed.emit(field_id)
                self.template_changed.emit()
                return True
        return False
    
    def get_field_at_column(self, col: int) -> Optional[FieldDefinition]:
        """Get the field definition at a column index."""
        if 0 <= col < len(self._template.fields):
            return self._template.fields[col]
        return None
    
    def get_field_by_id(self, field_id: str) -> Optional[FieldDefinition]:
        """Get a field definition by ID."""
        return self._template.get_field_by_id(field_id)
    
    def update_field_position(self, field_id: str, x: int, y: int) -> None:
        """Update a field's position on the card preview."""
        field_def = self._template.get_field_by_id(field_id)
        if field_def:
            field_def.x = x
            field_def.y = y
            self.template_changed.emit()
    
    def update_field_size(self, field_id: str, width: int, height: int) -> None:
        """Update a field's size on the card preview."""
        field_def = self._template.get_field_by_id(field_id)
        if field_def:
            field_def.width = width
            field_def.height = height
            self.template_changed.emit()
    
    # Row Management
    def add_row(self) -> str:
        """Add a new empty row. Returns the row ID."""
        row = CardRow()
        row_idx = len(self._rows)
        
        self.beginInsertRows(QModelIndex(), row_idx, row_idx)
        self._rows.append(row)
        self.endInsertRows()
        
        return row.id
    
    def remove_row(self, row_id: str) -> bool:
        """Remove a row by ID."""
        for idx, row in enumerate(self._rows):
            if row.id == row_id:
                self.beginRemoveRows(QModelIndex(), idx, idx)
                self._rows.pop(idx)
                self.endRemoveRows()
                return True
        return False
    
    def get_row(self, row_id: str) -> Optional[CardRow]:
        """Get a row by ID."""
        for row in self._rows:
            if row.id == row_id:
                return row
        return None
    
    def get_row_at_index(self, idx: int) -> Optional[CardRow]:
        """Get a row by index."""
        if 0 <= idx < len(self._rows):
            return self._rows[idx]
        return None
    
    def get_row_id_at_index(self, idx: int) -> Optional[str]:
        """Get the row ID at an index."""
        if 0 <= idx < len(self._rows):
            return self._rows[idx].id
        return None
    
    def get_all_rows(self) -> list[CardRow]:
        """Return all rows."""
        return list(self._rows)
    
    def get_all_fields(self) -> list[FieldDefinition]:
        """Return all field definitions."""
        return list(self._template.fields)
    
    def get_fields_sorted_by_z_index(self) -> list[FieldDefinition]:
        """Return all field definitions sorted by z_index (lowest first)."""
        return sorted(self._template.fields, key=lambda f: f.z_index)
    
    def get_max_z_index(self) -> int:
        """Get the maximum z_index among all fields."""
        if not self._template.fields:
            return 0
        return max(f.z_index for f in self._template.fields)
    
    def get_min_z_index(self) -> int:
        """Get the minimum z_index among all fields."""
        if not self._template.fields:
            return 0
        return min(f.z_index for f in self._template.fields)
    
    def bring_to_front(self, field_id: str) -> None:
        """Move field to the front (highest z_index)."""
        field = self.get_field_by_id(field_id)
        if field:
            field.z_index = self.get_max_z_index() + 1
            self.template_changed.emit()
    
    def send_to_back(self, field_id: str) -> None:
        """Move field to the back (lowest z_index)."""
        field = self.get_field_by_id(field_id)
        if field:
            field.z_index = self.get_min_z_index() - 1
            self.template_changed.emit()
    
    def bring_forward(self, field_id: str) -> None:
        """Move field one step forward in z-order."""
        field = self.get_field_by_id(field_id)
        if not field:
            return
        
        # Find the next field above this one
        sorted_fields = self.get_fields_sorted_by_z_index()
        current_idx = next((i for i, f in enumerate(sorted_fields) if f.id == field_id), -1)
        
        if current_idx >= 0 and current_idx < len(sorted_fields) - 1:
            # Swap z_index with the next field
            next_field = sorted_fields[current_idx + 1]
            field.z_index, next_field.z_index = next_field.z_index, field.z_index
            # Ensure they're different if they were the same
            if field.z_index == next_field.z_index:
                field.z_index += 1
            self.template_changed.emit()
    
    def send_backward(self, field_id: str) -> None:
        """Move field one step backward in z-order."""
        field = self.get_field_by_id(field_id)
        if not field:
            return
        
        # Find the previous field below this one
        sorted_fields = self.get_fields_sorted_by_z_index()
        current_idx = next((i for i, f in enumerate(sorted_fields) if f.id == field_id), -1)
        
        if current_idx > 0:
            # Swap z_index with the previous field
            prev_field = sorted_fields[current_idx - 1]
            field.z_index, prev_field.z_index = prev_field.z_index, field.z_index
            # Ensure they're different if they were the same
            if field.z_index == prev_field.z_index:
                field.z_index -= 1
            self.template_changed.emit()
    
    def add_field_definition(self, field_def: FieldDefinition) -> str:
        """Add an existing field definition to the template.
        
        Returns the field's ID.
        """
        col = len(self._template.fields)
        
        self.beginInsertColumns(QModelIndex(), col, col)
        self._template.fields.append(field_def)
        self.endInsertColumns()
        
        self.field_added.emit(field_def.id)
        self.template_changed.emit()
        return field_def.id
    
    def get_unique_field_name(self, base_name: str) -> str:
        """Generate a unique field name by adding _1, _2, etc. suffix."""
        existing_names = {f.name for f in self._template.fields}
        
        if base_name not in existing_names:
            return base_name
        
        counter = 1
        while f"{base_name}_{counter}" in existing_names:
            counter += 1
        
        return f"{base_name}_{counter}"
    
    def update_field_name(self, field_id: str, new_name: str) -> bool:
        """Update a field's name."""
        field = self.get_field_by_id(field_id)
        if field:
            field.name = new_name
            self.template_changed.emit()
            return True
        return False
