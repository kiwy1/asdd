FROM python:3.11-slim
WORKDIR /app
RUN pip install influxdb-client
COPY smart_grid_sim.py .
CMD ["python", "smart_grid_sim.py"]
