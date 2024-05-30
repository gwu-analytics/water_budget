class Customer:
    def __init__(self, name, footage):
        self.name, self.footage, self.allowance, self.meters = name, footage, None, None
        self.mon_viol, self.mid_viol, self.bug_viol, self.irrig_viol = 0, 0, 0, 0
        self.meters = []
        self.__acc_party = None
        self.usage = 0

    def set_acc_party(self, acc_party):
        self.__acc_party = acc_party

    def set_allowance(self, allowance):
        self.allowance = allowance

    def add_meter(self, current_meter_obj):
        self.meters.append(current_meter_obj)

    def add_usage(self, usage):
        self.usage += usage

    def get_acc_party(self):
        return self.__acc_party