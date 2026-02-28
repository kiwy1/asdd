FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask requests

COPY http_simulator.py .

EXPOSE 9999

CMD ["python", "http_simulator.py"]
