class Customer:
    def __init__(self, name, footage, cust_type, acc_party):
        self.name, self.footage, self.ap, self.allowance, self.meters = name, footage, acc_party, None, None
        self.mon_viol, self.mid_viol, self.bug_viol, self.irrig_viol, self.usage = 0, 0, 0, 0, 0
        self.meters, self.mid_days = [], []
        self.type = cust_type

    def set_allowance(self, allowance):
        self.allowance = allowance

    def add_meter(self, current_meter_obj):
        self.meters.append(current_meter_obj)

    def add_usage(self, usage):
        self.usage += usage

    def get_acc_party(self):
        return self.ap

    def add_days(self, days):
        self.mid_days.append(days)