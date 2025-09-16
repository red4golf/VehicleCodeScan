# Vehicle Code Scanner Reporting Service

This project provides a small Flask-based web application for uploading Foxwell NT650 Elite scanner exports, interpreting diagnostic codes, embedding user-supplied photos, and delivering a branded PDF report by email. Files and generated reports are stored for 30 days before automated cleanup.

## Features

- Authenticated web form for uploading scanner exports, multiple JPG images, and vehicle details.
- Parser for Foxwell NT650 Elite text/CSV exports with OBD-II code interpretation.
- Multilingual report generation (English and Spanish) using ReportLab.
- Email delivery of generated PDF report attachments.
- Storage metadata tracked in SQLite with a purge script that deletes items older than 30 days.

## Getting Started

1. **Install dependencies**
   ```bash
   pip install -e .[development]
   ```

2. **Set environment variables** (see `.env.example`):
   - `APP_SECRET_KEY`
   - `APP_USERNAME` / `APP_PASSWORD`
   - `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`
   - `MAIL_SENDER`

3. **Run the web app**
   ```bash
   flask --app vehiclecodescan.app run --debug
   ```

4. **Run scheduled cleanup**
   ```bash
   python -m vehiclecodescan.cron.purge
   ```

codex/create-vehicle-health-report-system-drdpm9
## Static demo

If you only need to preview the upload experience, open `demo/upload-demo.html` directly in a web browser. The page mirrors the
Flask template, including validation styling and a sample success summary, without requiring any backend services.

=======
main
## Tests

```bash
pytest
```

## Docker

Build and run using Docker:
```bash
docker build -t vehiclecodescan .
docker run --env-file .env -p 5000:5000 vehiclecodescan
```

## License

MIT
