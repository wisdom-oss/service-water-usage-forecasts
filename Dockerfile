FROM python:3.9
# Set some labels
LABEL de.uol.wisdom-oss.vendor="WISdoM 2.0 Project Group"
LABEL de.uol.wisdom-oss.maintainer="wisdom@uol.de"
LABEL de.uol.wisdom-oss.service-name="water-usage-forecast"
RUN addgroup --system water-usage-forecast && \
    adduser --home /opt/water-usage-forecast --system --gecos "" water-usage-forecast --ingroup water-usage-forecast

WORKDIR /opt/water-usage-forecast
# Copy and install the requirements
COPY . /opt/water-usage-forecast
RUN python -m pip install --no-cache -r /opt/water-usage-forecast/requirements.txt
# Switch to the just created user and into the home directory
USER water-usage-forecast
ENTRYPOINT ["python", "service.py"]