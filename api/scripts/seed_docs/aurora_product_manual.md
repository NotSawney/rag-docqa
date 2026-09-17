# Aurora Analytics — Product Manual

> Fictional product used as sample corpus for the RAG demo. Any resemblance to a real product is coincidental.

## Overview

Aurora Analytics is a self-hosted dashboard platform for small teams. It ingests data
from CSV files, Postgres databases, and REST APIs, and renders configurable dashboards
with tables, charts, and scheduled email reports.

## Installation

Aurora ships as a Docker image. The minimum supported version is Aurora 3.2. To install,
pull the image `aurora/analytics:3.2` and run it with a Postgres 14+ database attached.
Aurora requires 2 GB of RAM and 1 vCPU for up to 10 concurrent users. For 11 to 50 users,
the recommended configuration is 4 GB of RAM and 2 vCPUs.

## Data Sources

A workspace can connect up to five data sources on the Starter plan and unlimited data
sources on the Business plan. Supported source types are CSV upload, Postgres, MySQL, and
generic REST endpoints returning JSON. Google Sheets is supported only on the Business plan.
Each data source refreshes on a schedule you define, from every 5 minutes up to once per day.

## Dashboards

Dashboards are built from widgets. A single dashboard supports up to 30 widgets. Widget
types include table, line chart, bar chart, single-value KPI, and pivot table. Dashboards
can be shared with a public read-only link, which can be password protected.

## Scheduled Reports

Aurora can email a PDF snapshot of any dashboard on a daily, weekly, or monthly schedule.
Reports are sent from the address configured in Settings → Email. The Starter plan allows
up to three scheduled reports; the Business plan allows unlimited scheduled reports.

## User Roles

Aurora has three roles: Viewer, Editor, and Admin. Viewers can open dashboards and export
data. Editors can additionally create and modify dashboards and data sources. Admins can
manage users, billing, and workspace settings. Only an Admin can delete a data source.
