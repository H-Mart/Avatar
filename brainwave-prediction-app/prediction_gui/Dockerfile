FROM python:3.11
LABEL authors="henry"

COPY gui_requirements.txt /prediction_gui/gui_requirements.txt
WORKDIR /prediction_gui

RUN pip install --upgrade pip
RUN pip install -r gui_requirements.txt

COPY . /prediction_gui/app

CMD ["python", "-m", "app.GUI"]