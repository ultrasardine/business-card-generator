"""Data models for business cards.

This module contains the core data structures for representing business cards,
their fields, and layout templates.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any
import uuid


class FieldType(Enum):
    """Types of fields that can be added to a card template."""
    TEXT = "text"
    IMAGE = "image"


@dataclass
class FieldDefinition:
    """Definition of a field/column in the card template.
    
    This defines what data can be entered (appears as a column in the table)
    and how it appears on the card preview.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    field_type: FieldType = FieldType.TEXT
    x: int = 0
    y: int = 0
    width: int = 100
    height: int = 30
    font_size: int = 12
    font_color: str = "#000000"
    font_family: str = "Arial"
    font_bold: bool = False
    font_italic: bool = False
    z_index: int = 0  # Z-order for layering (higher = on top)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "field_type": self.field_type.value,
            "x": self.x, "y": self.y,
            "width": self.width, "height": self.height,
            "font_size": self.font_size,
            "font_color": self.font_color,
            "font_family": self.font_family,
            "font_bold": self.font_bold,
            "font_italic": self.font_italic,
            "z_index": self.z_index
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FieldDefinition":
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            field_type=FieldType(data["field_type"]),
            x=data.get("x", 0), y=data.get("y", 0),
            width=data.get("width", 100), height=data.get("height", 30),
            font_size=data.get("font_size", 12),
            font_color=data.get("font_color", "#000000"),
            font_family=data.get("font_family", "Arial"),
            font_bold=data.get("font_bold", False),
            font_italic=data.get("font_italic", False),
            z_index=data.get("z_index", 0)
        )
    
    def copy(self) -> "FieldDefinition":
        """Create a copy of this field with a new ID."""
        return FieldDefinition(
            id=str(uuid.uuid4()),
            name=self.name,
            field_type=self.field_type,
            x=self.x, y=self.y,
            width=self.width, height=self.height,
            font_size=self.font_size,
            font_color=self.font_color,
            font_family=self.font_family,
            font_bold=self.font_bold,
            font_italic=self.font_italic,
            z_index=self.z_index
        )


@dataclass 
class CardTemplate:
    """Template defining the structure and layout of business cards."""
    fields: list[FieldDefinition] = field(default_factory=list)
    background_color: str = "#FFFFFF"
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "fields": [f.to_dict() for f in self.fields],
            "background_color": self.background_color
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CardTemplate":
        """Deserialize from dictionary."""
        return cls(
            fields=[FieldDefinition.from_dict(f) for f in data.get("fields", [])],
            background_color=data.get("background_color", "#FFFFFF")
        )
    
    def get_field_by_id(self, field_id: str) -> Optional[FieldDefinition]:
        """Get a field definition by its ID."""
        for f in self.fields:
            if f.id == field_id:
                return f
        return None
    
    def get_field_by_name(self, name: str) -> Optional[FieldDefinition]:
        """Get a field definition by its name."""
        for f in self.fields:
            if f.name == name:
                return f
        return None


@dataclass
class CardRow:
    """A single row of card data (one business card's content)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "data": self.data
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CardRow":
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            data=data.get("data", {})
        )
    
    def get_value(self, field_id: str) -> Any:
        """Get the value for a field."""
        return self.data.get(field_id, "")
    
    def set_value(self, field_id: str, value: Any) -> None:
        """Set the value for a field."""
        self.data[field_id] = value
