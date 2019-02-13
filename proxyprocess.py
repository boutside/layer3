#!/usr/bin/env python3

import re

def process_incoming(data):
    str_data = data.decode("utf-8")
    
    changed = re.sub(b'\x42', b'\x41', data)
    return changed

def process_outgoing(data):
    str_data = data.decode("utf-8")

    changed = re.sub(r"simple", "proxy", str_data)
    return changed.encode("utf-8")
