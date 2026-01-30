"""Table view widget for displaying business cards.

This module provides a table view where columns are defined by the template
fields and rows are individual card data entries.
"""

from typing import Optional

from PySide6.QtCore import (
    QItemSelection,
    Signal,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableView,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QMessageBox,
    QInputDialog,
    QMenu,
    QFileDialog,
)

from ..core.card_data_model import CardDataModel
from ..models.card import FieldType


class CardTableWidget(QWidget):
    """Container widget with table view and management buttons.
    
    Provides buttons for:
    - Adding/removing rows (cards)
    - Adding/removing columns (fields)
    """
    
    row_selected = Signal(str)  # row_id
    row_added = Signal(str)  # row_id
    row_removed = Signal(str)  # row_id
    image_selected = Signal(str, int, str)  # file_path, row_index, field_id
    
    def __init__(self, model: CardDataModel, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._model = model
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        self.setToolTip("Business card data table - manage cards and fields")
        
        # Row management buttons
        row_bar = QFrame()
        row_layout = QHBoxLayout(row_bar)
        row_layout.setContentsMargins(5, 5, 5, 5)
        row_layout.setSpacing(5)
        
        self._add_row_btn = QPushButton("+ Add Card")
        self._add_row_btn.setToolTip("Add a new business card row")
        self._add_row_btn.clicked.connect(self._on_add_row)
        row_layout.addWidget(self._add_row_btn)
        
        self._remove_row_btn = QPushButton("- Remove Card")
        self._remove_row_btn.setToolTip("Remove the selected card")
        self._remove_row_btn.clicked.connect(self._on_remove_row)
        self._remove_row_btn.setEnabled(False)
        row_layout.addWidget(self._remove_row_btn)
        
        row_layout.addStretch()
        
        # Column/field management buttons
        self._add_field_btn = QPushButton("+ Add Field")
        self._add_field_btn.setToolTip("Add a new field/column")
        add_field_menu = QMenu(self)
        add_field_menu.addAction("Text Field", lambda: self._on_add_field(FieldType.TEXT))
        add_field_menu.addAction("Image Field", lambda: self._on_add_field(FieldType.IMAGE))
        self._add_field_btn.setMenu(add_field_menu)
        row_layout.addWidget(self._add_field_btn)
        
        self._remove_field_btn = QPushButton("- Remove Field")
        self._remove_field_btn.setToolTip("Remove a field/column")
        self._remove_field_btn.clicked.connect(self._on_remove_field)
        row_layout.addWidget(self._remove_field_btn)
        
        layout.addWidget(row_bar)
        
        # Table view
        self._table_view = CardTableView(self._model, self)
        self._table_view.row_selected.connect(self._on_row_selected)
        self._table_view.image_selected.connect(self.image_selected.emit)
        layout.addWidget(self._table_view)
    
    def _on_add_row(self) -> None:
        row_id = self._model.add_row()
        self._table_view.select_row_by_id(row_id)
        self.row_added.emit(row_id)
    
    def _on_remove_row(self) -> None:
        row_id = self._table_view.get_selected_row_id()
        if row_id:
            reply = QMessageBox.question(
                self, "Remove Card",
                "Are you sure you want to remove this card?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._model.remove_row(row_id)
                self.row_removed.emit(row_id)
                self._remove_row_btn.setEnabled(False)
    
    def _on_add_field(self, field_type: FieldType) -> None:
        name, ok = QInputDialog.getText(
            self, "Add Field",
            "Enter field name:"
        )
        if ok and name.strip():
            self._model.add_field(name.strip(), field_type)
    
    def _on_remove_field(self) -> None:
        fields = self._model.get_all_fields()
        if not fields:
            return
        
        field_names = [f.name for f in fields]
        name, ok = QInputDialog.getItem(
            self, "Remove Field",
            "Select field to remove:",
            field_names, 0, False
        )
        if ok and name:
            field = self._model.get_template().get_field_by_name(name)
            if field:
                reply = QMessageBox.question(
                    self, "Remove Field",
                    f"Remove field '{name}'? This will delete data in this column.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self._model.remove_field(field.id)
    
    def _on_row_selected(self, row_id: str) -> None:
        self._remove_row_btn.setEnabled(True)
        self.row_selected.emit(row_id)
    
    def get_selected_row_id(self) -> Optional[str]:
        return self._table_view.get_selected_row_id()
    
    def select_row_by_id(self, row_id: str) -> bool:
        return self._table_view.select_row_by_id(row_id)
    
    def clear_selection(self) -> None:
        self._table_view.clearSelection()
        self._remove_row_btn.setEnabled(False)
    
    def viewport(self):
        return self._table_view.viewport()


class CardTableView(QTableView):
    """Table view displaying card data rows.
    
    Columns are defined by the template fields.
    Rows are individual card data entries.
    """
    
    row_selected = Signal(str)  # row_id
    image_selected = Signal(str, int, str)  # file_path, row_index, field_id
    
    def __init__(self, model: CardDataModel, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._model = model
        
        self.setModel(model)
        self.setToolTip("Card data - double-click to edit, click image cells to select file")
        
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setShowGrid(True)
        
        # Connect selection
        sel_model = self.selectionModel()
        if sel_model:
            sel_model.selectionChanged.connect(self._on_selection_changed)
        
        # Connect to template changes to reconfigure headers
        model.template_changed.connect(self._configure_headers)
        self._configure_headers()
        
        # Handle clicks on image columns
        self.clicked.connect(self._on_cell_clicked)
    
    def _configure_headers(self) -> None:
        h_header = self.horizontalHeader()
        if h_header:
            h_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        v_header = self.verticalHeader()
        if v_header:
            v_header.setDefaultSectionSize(30)
    
    def _on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        indexes = selected.indexes()
        if indexes:
            row_idx = indexes[0].row()
            row_id = self._model.get_row_id_at_index(row_idx)
            if row_id:
                self.row_selected.emit(row_id)
    
    def _on_cell_clicked(self, index) -> None:
        """Handle cell click - open file dialog for image fields."""
        col = index.column()
        field = self._model.get_field_at_column(col)
        if field and field.field_type == FieldType.IMAGE:
            file_path, _ = QFileDialog.getOpenFileName(
                self, f"Select {field.name}",
                "", "Images (*.png *.jpg *.jpeg *.gif *.bmp)"
            )
            if file_path:
                # Store the path - MainWindow will handle copying to project folder
                self._model.setData(index, file_path)
                self.image_selected.emit(file_path, index.row(), field.id)
    
    def get_selected_row_id(self) -> Optional[str]:
        indexes = self.selectedIndexes()
        if indexes:
            row_idx = indexes[0].row()
            return self._model.get_row_id_at_index(row_idx)
        return None
    
    def select_row_by_id(self, row_id: str) -> bool:
        for idx in range(self._model.rowCount()):
            if self._model.get_row_id_at_index(idx) == row_id:
                self.selectRow(idx)
                return True
        return False
