# utils/validation.py - CREATE THIS FILE
from marshmallow import Schema, fields, ValidationError
import re

class AgentRegistrationSchema(Schema):
    agent_id = fields.Str(required=True, validate=lambda x: re.match(r'^[a-zA-Z0-9\-_]+$', x))
    name = fields.Str(required=True, validate=fields.Length(min=1, max=100))
    host = fields.Str(required=True)
    version = fields.Str(required=True)
    agent_type = fields.Str(missing="ultimate", validate=fields.OneOf(["ultimate", "standard", "lite"]))
    capabilities = fields.List(fields.Str(), missing=[])

class HeartbeatSchema(Schema):
    agent_id = fields.Str(required=True)
    status = fields.Str(validate=fields.OneOf(["online", "offline", "busy", "maintenance"]))
    cpu_percent = fields.Float(validate=fields.Range(min=0, max=100))
    memory_percent = fields.Float(validate=fields.Range(min=0, max=100))

def validate_data(schema_class, data):
    schema = schema_class()
    try:
        return schema.load(data)
    except ValidationError as err:
        raise ValueError(f"Validation error: {err.messages}")