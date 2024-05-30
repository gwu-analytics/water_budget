class Meter:
    def __init__(self, meter_id, meter_type, meter_data):
        self.type, self.data = meter_type, meter_data
        self.meter_id = meter_id

    def set_meters(self, meter_id, meter_type, meter_data):
        self.type, self.data = meter_type, meter_data
        self.meter_id = meter_id