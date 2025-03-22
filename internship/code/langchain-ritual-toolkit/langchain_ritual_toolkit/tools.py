from collections import OrderedDict
from typing import Dict, List

from pydantic import ConfigDict, create_model

from langchain_ritual_toolkit.configuration import RitualConfig
from langchain_ritual_toolkit.prompts import (
    CANCEL_SCHEDULED_TRANSACTION_PROMPT,
    SCHEDULE_TRANSACTION_PROMPT,
)


def create_type_model(components, name="NestedStruct"):
    field_definitions = {}
    for component in components:
        field_type = get_field_type(component)
        field_definitions[component.name] = (field_type, ...)
    return create_model(name, **field_definitions)

def get_field_type(input):
    if hasattr(input, 'components') and input.components:
        return create_type_model(input.components, f"{input.name.capitalize()}Struct")
    
    if input.type.startswith("uint") or input.type.startswith("int"):
        return int
    elif input.type == "bool":
        return bool
    elif input.type == "address":
        return str
    elif input.type.startswith("bytes"):
        return bytes
    elif input.type == "string":
        return str
    return str  # Default to str for unknown types

def generate_schedule_transaction_tool(ritual_config: RitualConfig) -> Dict:
    schedule_fn = ritual_config.schedule_fn
    # find scheduled function by name from config abi

    schedule_abi_item = None
    for item in ritual_config.abi:
        if item.name == schedule_fn:
            schedule_abi_item = item
            break
    
    if schedule_abi_item is None:
        raise ValueError(f"Schedule function {schedule_fn} not found in ABI")

    field_definitions = OrderedDict()
    for input in schedule_abi_item.inputs:
        field_type = get_field_type(input)
        field_definitions[input.name] = (field_type, ...)

    ScheduleTransactionArgs = create_model(
        'ScheduleTransactionArgs',
        __config__=ConfigDict(frozen=True),  # This ensures order preservation
        **field_definitions
    )

    schema = ScheduleTransactionArgs.schema()
    args_description = "\n".join([f"- {prop} ({schema['properties'][prop]['type']})" for prop in schema['properties']])
    schedule_transaction_prompt = SCHEDULE_TRANSACTION_PROMPT.replace("{{args}}", args_description)

    return {
        "method": "schedule_transaction",
        "name": "Schedule Transaction",
        "description": schedule_transaction_prompt,
        "args_schema": ScheduleTransactionArgs,
    }

def generate_cancel_scheduled_transaction_tool(ritual_config: RitualConfig) -> Dict:
    cancel_fn = ritual_config.cancel_fn
    # find cancel function by name from config abi
    cancel_abi_item = None
    for item in ritual_config.abi:
        if item.name == cancel_fn:
            cancel_abi_item = item
            break
    
    if cancel_abi_item is None:
        raise ValueError(f"Cancel function {cancel_fn} not found in ABI")

    field_definitions = OrderedDict()
    for input in cancel_abi_item.inputs:
        field_type = get_field_type(input)
        field_definitions[input.name] = (field_type, ...)

    CancelScheduledTransactionArgs = create_model(
        'CancelScheduledTransactionArgs',
        __config__=ConfigDict(frozen=True),  # This ensures order preservation
        **field_definitions
    )

    schema = CancelScheduledTransactionArgs.schema()
    args_description = "\n".join([f"- {prop} ({schema['properties'][prop]['type']})" for prop in schema['properties']])
    cancel_scheduled_transaction_prompt = CANCEL_SCHEDULED_TRANSACTION_PROMPT.replace("{{args}}", args_description)

    return {
        "method": "cancel_scheduled_transaction",
        "name": "Cancel Scheduled Transaction",
        "description": cancel_scheduled_transaction_prompt,
        "args_schema": CancelScheduledTransactionArgs,
    }

def generate_tools(ritual_config: RitualConfig) -> List[Dict]:
    return [
        generate_schedule_transaction_tool(ritual_config),
        generate_cancel_scheduled_transaction_tool(ritual_config),
    ]