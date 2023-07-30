FROM grafana/grafana

COPY config/grafana_datasources.yaml /etc/grafana/provisioning/datasources/datasource.yaml
COPY config/grafana_dashboards.yaml /etc/grafana/provisioning/dashboards/dashboards.yaml
COPY dashboards /opt/grafana/dashboards
