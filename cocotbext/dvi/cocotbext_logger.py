import logging

class CocoTBExtLogger:
    def __init__(self, name="default"):
        self.name = name
        self.log = logging.getLogger(f"cocotb.{self.name}")

    def enable_logging(self):
        self.log.setLevel(logging.DEBUG)
    
    def disable_logging(self):
        self.log.setLevel(logging.WARNING)
