#!/usr/bin/env python3

import re

import proxyio


ARGS = None


def init(arg):
    global ARGS

    ARGS = arg


def process_incoming(data):
    if ARGS.incoming_filter:
       data = interactive_incoming(data)

    return data 


def process_outgoing(data):
    if ARGS.outgoing_filter:
        data = interactive_outgoing(data)

    return data 


def interactive_incoming(data): 
    data = interactive_generic(data, ARGS.incoming_filter, f"Found match for Incoming Filter. Please input substitution: ")

    return data


def interactive_outgoing(data):
    data = interactive_generic(data, ARGS.outgoing_filter, f"Found match for Outgoing Filter. Please input substitution: ")

    return data


def interactive_generic(data, gen_filter, match_string):
    cast_filter = cast(gen_filter, data)

    if re.search(cast_filter, data):
        substitution = proxyio.get(match_string)
        substitution = cast(substitution, data)
        data = re.sub(cast_filter, substitution, data, 1, re.S) 

    return data


def cast(value, data):
    if type(value) is not type(data):
        return value.encode("utf-8")
    return value
