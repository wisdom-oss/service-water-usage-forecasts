FROM python:3.10-slim
# Set some labels
LABEL de.uol.wisdom-oss.vendor="WISdoM 2.0 Project Group"
LABEL de.uol.wisdom-oss.maintainer="wisdom@uol.de"
LABEL de.uol.wisdom-oss.service-name="water-usage-forecast"
WORKDIR /opt/water-usage-forecast
# Copy and install the requirements
COPY . /opt/water-usage-forecast
RUN python -m pip install --no-cache -r /opt/water-usage-forecast/requirements.txt
# Switch to the just created user and into the home directory
ENTRYPOINT ["python", "service.py"]
