#!/bin/bash

protoc --python_out=. --proto_path=noec_fw/proto vals.proto
