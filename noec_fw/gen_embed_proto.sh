#!/bin/bash

protoc --plugin=../EmbeddedProto/protoc-gen-eams --proto_path=proto --eams_out=vals.proto
