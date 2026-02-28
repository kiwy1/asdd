FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir aiocoap
COPY coap_virtual_sim.py .
CMD ["python", "coap_virtual_sim.py"]
