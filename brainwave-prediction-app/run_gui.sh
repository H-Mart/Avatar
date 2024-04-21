#!/bin/bash

export BCI_GUI_SERIAL_PORT="/dev/cu.usbserial-DP04WFVZ"
export BCI_GUI_USE_FAKE_BCI="False"
export BCI_GUI_PREDICTION_SERVER_URL="https://prediction.henrymarty.dev"

python3.11 -m prediction_gui.GUI
