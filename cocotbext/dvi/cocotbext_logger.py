import logging

class CocoTBExtLogger:
    def __init__(self, name="default", enable=True):
        self.name = name
        self.log = logging.getLogger(f"cocotb.{self.name}")
        if enable:
            self.enable_logging()

    def enable_logging(self):
        self.log.setLevel(logging.DEBUG)
    
    def disable_logging(self):
        self.log.setLevel(logging.WARNING)
