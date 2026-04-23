class Meter:
    def __init__(self, meter_id, meter_type, source, var):
        self.type, self.data = meter_type, None
        self.meter_id = meter_id
        self.sourceid = source
        self.variableid = var

    def set_meters(self, meter_id, meter_type, meter_data):
        self.type, self.data = meter_type, meter_data
        self.meter_id = meter_id

    def add_data(self, meter_data):
        self.meter_data = meter_data
