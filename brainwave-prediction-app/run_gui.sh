#!/bin/bash

export BCI_GUI_SERIAL_PORT="/dev/ttyUSB0"
export BCI_GUI_USE_FAKE_BCI="True"
export BCI_GUI_PREDICTION_SERVER_URL="https://prediction.henrymarty.dev"

python -m prediction_gui.GUI