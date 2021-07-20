FROM continuumio/miniconda3

COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "mega_viewer/main.py"]