"""Tests for data models."""

import pytest
from src.business_card_generator.models.card import (
    FieldDefinition,
    FieldType,
    CardTemplate,
    CardRow,
)


class TestFieldDefinition:
    """Tests for FieldDefinition model."""

    def test_create_text_field(self):
        """Test creating a text field."""
        field = FieldDefinition(name="Name", field_type=FieldType.TEXT)
        assert field.name == "Name"
        assert field.field_type == FieldType.TEXT
        assert field.id is not None

    def test_create_image_field(self):
        """Test creating an image field."""
        field = FieldDefinition(name="Photo", field_type=FieldType.IMAGE)
        assert field.name == "Photo"
        assert field.field_type == FieldType.IMAGE

    def test_field_to_dict(self):
        """Test serialization to dictionary."""
        field = FieldDefinition(
            name="Email",
            field_type=FieldType.TEXT,
            x=10,
            y=20,
            width=100,
            height=30,
        )
        data = field.to_dict()
        assert data["name"] == "Email"
        assert data["field_type"] == "text"
        assert data["x"] == 10
        assert data["y"] == 20

    def test_field_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "id": "test-id",
            "name": "Phone",
            "field_type": "text",
            "x": 50,
            "y": 100,
            "width": 150,
            "height": 25,
            "font_size": 14,
            "font_color": "#333333",
            "font_family": "Helvetica",
            "font_bold": True,
            "font_italic": False,
            "z_index": 5,
        }
        field = FieldDefinition.from_dict(data)
        assert field.id == "test-id"
        assert field.name == "Phone"
        assert field.font_bold is True
        assert field.z_index == 5

    def test_field_copy(self):
        """Test copying a field creates new ID."""
        original = FieldDefinition(name="Title", x=10, y=20)
        copied = original.copy()
        assert copied.name == original.name
        assert copied.x == original.x
        assert copied.id != original.id


class TestCardTemplate:
    """Tests for CardTemplate model."""

    def test_create_empty_template(self):
        """Test creating an empty template."""
        template = CardTemplate()
        assert len(template.fields) == 0
        assert template.background_color == "#FFFFFF"

    def test_template_with_fields(self):
        """Test template with fields."""
        field1 = FieldDefinition(name="Name")
        field2 = FieldDefinition(name="Email")
        template = CardTemplate(fields=[field1, field2])
        assert len(template.fields) == 2

    def test_get_field_by_id(self):
        """Test getting field by ID."""
        field = FieldDefinition(name="Company")
        template = CardTemplate(fields=[field])
        found = template.get_field_by_id(field.id)
        assert found is not None
        assert found.name == "Company"

    def test_get_field_by_name(self):
        """Test getting field by name."""
        field = FieldDefinition(name="Title")
        template = CardTemplate(fields=[field])
        found = template.get_field_by_name("Title")
        assert found is not None
        assert found.id == field.id

    def test_template_serialization(self):
        """Test template to/from dict."""
        field = FieldDefinition(name="Name", x=10, y=20)
        template = CardTemplate(fields=[field], background_color="#EEEEEE")
        
        data = template.to_dict()
        restored = CardTemplate.from_dict(data)
        
        assert restored.background_color == "#EEEEEE"
        assert len(restored.fields) == 1
        assert restored.fields[0].name == "Name"


class TestCardRow:
    """Tests for CardRow model."""

    def test_create_empty_row(self):
        """Test creating an empty row."""
        row = CardRow()
        assert row.id is not None
        assert len(row.data) == 0

    def test_set_and_get_value(self):
        """Test setting and getting values."""
        row = CardRow()
        row.set_value("field-1", "John Doe")
        assert row.get_value("field-1") == "John Doe"

    def test_get_missing_value(self):
        """Test getting a missing value returns empty string."""
        row = CardRow()
        assert row.get_value("nonexistent") == ""

    def test_row_serialization(self):
        """Test row to/from dict."""
        row = CardRow()
        row.set_value("name", "Jane")
        row.set_value("email", "jane@example.com")
        
        data = row.to_dict()
        restored = CardRow.from_dict(data)
        
        assert restored.id == row.id
        assert restored.get_value("name") == "Jane"
        assert restored.get_value("email") == "jane@example.com"
