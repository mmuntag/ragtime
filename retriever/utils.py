import time

base_prompt = \
"""Egy segítőkész mesterséges intelligencia asszisztens vagy, válaszolj a feltett kérdésekre magyar nyelven a legjobb tudásod szerint.
Fogsz találkozni OCR-rel keletkezett zajos szöveg részletekkel is, a válaszaidban mindig igyekezz helyes magyar nyelvet használni,
és ha idézel a kontextudból, javítsd a hibáit, amennyiben lehetséges."""


class Timer:
    def __init__(self, msg, silent=False):
        self.msg = msg
        self.silent = silent

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        if not self.silent:
            print(f"[TIMER] Time elapsed [{self.msg}]:  {self.end_time - self.start_time}")
