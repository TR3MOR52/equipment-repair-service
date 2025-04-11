ACCESS_MATRIX = {
    'manager': {
        'client': ['C', 'R', 'U', 'D'],
        'storage': ['C', 'R', 'U', 'D'],
        'employee': ['C', 'R', 'U', 'D'],
        'supplier': ['C', 'R', 'U', 'D'],
        'equipment': ['C', 'R', 'U', 'D'],
        'repair_request': ['C', 'R', 'U', 'D'],
        'repair': ['C', 'R', 'U', 'D'],
        'diagnosis': ['C', 'R', 'U', 'D'],
        'quality_control': ['C', 'R', 'U', 'D'],
        'component': ['C', 'R', 'U', 'D'],
        'component_order': ['C', 'R', 'U', 'D'],
        'order_detail': ['C', 'R', 'U', 'D'],
        'equipment_report': ['C', 'R', 'U', 'D'],
        'audit_log': ['C', 'R', 'U', 'D']
    },
    'db_admin': {
        'client': ['R'],
        'storage': ['R'],
        'employee': ['R'],
        'supplier': ['R'],
        'equipment': ['R'],
        'repair_request': ['R'],
        'repair': ['R'],
        'diagnosis': ['R'],
        'quality_control': ['R'],
        'component': ['R'],
        'component_order': ['R'],
        'order_detail': ['R'],
        'equipment_report': ['R'],
        'audit_log': ['C', 'R', 'U', 'D']
    },
    'technician': {
        'equipment': ['R'],
        'repair_request': ['R'],
        'repair': ['C', 'R', 'U'],
        'diagnosis': ['R'],
        'quality_control': ['R']
    },
    'quality_control': {
        'equipment': ['R'],
        'repair': ['R'],
        'quality_control': ['C', 'R', 'U']
    },
    'diagnostics': {
        'equipment': ['R'],
        'repair_request': ['R'],
        'diagnosis': ['C', 'R', 'U']
    },
    'storage_operator': {
        'storage': ['C', 'R', 'U'],
        'component': ['C', 'R', 'U'],
        'component_order': ['C', 'R', 'U'],
        'order_detail': ['C', 'R', 'U']
    },
    'intake_operator': {
        'client': ['C', 'R', 'U'],
        'equipment': ['C', 'R', 'U'],
        'repair_request': ['C', 'R', 'U']
    },
    'outtake_operator': {
        'client': ['R'],
        'equipment': ['R'],
        'equipment_report': ['C', 'R', 'U']
    }
}

def is_action_allowed(role, entity, action):
    actions = ACCESS_MATRIX.get(role, {}).get(entity, [])
    return action in actions
