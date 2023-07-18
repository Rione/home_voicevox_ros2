#!/bin/bash

TMP_FILE="/tmp/test.log"

timeout 5 ros2 launch voicevox_ros2 voicevox.launch.py > "$TMP_FILE"

grep -qi "error" "$TMP_FILE" &&
    cat "$TMP_FILE" &&
    exit 1

echo "No errors found during the test" && exit 0
