class Alert:
    def __init__(self, node_id, alert_id, alert_type):
        self.alert_id = alert_id
        self.alert_type = alert_type
        self.node_id = node_id
        self.resolved = False
        self.resolver_employee_id = None
