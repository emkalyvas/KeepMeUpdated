# KeepMeUpdated API Documentation

KeepMeUpdated exposes a comprehensive RESTful API built with FastAPI. You can use this API to integrate KeepMeUpdated with external services, home automation systems (like Home Assistant), or custom scripts.

## Authentication

To authenticate with the API, you must first generate an **API Token** from the KeepMeUpdated dashboard:
1. Navigate to **Settings** -> **API Tokens**.
2. Click **+ Generate Token**.
3. Copy the generated token (it will look like `kmu_xxxx...`).

Include this token in the `Authorization` header of your HTTP requests as a Bearer token:

```http
Authorization: Bearer kmu_your_generated_token_here
```

## Interactive Documentation

You can explore all available endpoints, schemas, and test requests directly in your browser:

- **Swagger UI**: `http://<your-keepmeupdated-ip>/api/docs`
- **ReDoc**: `http://<your-keepmeupdated-ip>/api/redoc`

## Common API Endpoints

All API endpoints are prefixed with `/api/`.

### 1. Channels
Manage the destinations where notifications are sent.
- `GET /api/channels/` - List all configured channels.
- `POST /api/channels/` - Create a new channel.
  **Payload Example:**
  ```json
  {
    "plugin_id": "gotify",
    "name": "My Gotify Server",
    "config": {
      "url": "http://gotify.example.com",
      "token": "secret_token"
    },
    "is_active": true
  }
  ```
- `POST /api/channels/test` - Send a test notification to a specific channel configuration.
  **Payload Example:** *(Same as Channel creation)*

### 2. Notifications
Manage scheduled and recurring alerts.
- `GET /api/notifications/` - List all notifications.
- `POST /api/notifications/` - Create a new notification.

  **Scheduling Configuration Details:**
  - `schedule_type`: Determines how the schedule is evaluated. Must be one of:
    - `"specific_time"`: Runs exactly once at the specified date and time.
    - `"cron"`: Runs repeatedly based on a standard cron expression.
    - `"interval"`: Runs repeatedly after a set duration.
  - `schedule_expr`: The value depends on the `schedule_type`:
    - If `"specific_time"`: An ISO 8601 datetime string (e.g., `"2024-12-31T23:59:00"`).
    - If `"cron"`: A standard cron expression (e.g., `"0 8 * * *"` for every day at 8 AM).
    - If `"interval"`: An integer followed optionally by a unit (e.g., `"30"`, `"45 minutes"`, `"2 hours"`, `"1 day"`). Defaults to minutes if no unit is provided.
  - `exclusions`: An optional list of rules to skip executions. Two rule types are supported:
    - **Time Exclusion**: `{"type": "time", "start": "22:00", "end": "06:00", "tz_offset": 120}`. Skips executions between the start and end times. (`tz_offset` is your local timezone offset in minutes).
    - **Weekday Exclusion**: `{"type": "weekday", "days": [5, 6], "tz_offset": 120}`. Skips executions on the specified days (where 0 = Monday, 6 = Sunday).

  **Payload Example:**
  ```json
  {
    "channel_id": 1,
    "title": "Daily Backup Status",
    "payload": "Backup completed successfully at {time}",
    "schedule_type": "cron",
    "schedule_expr": "0 2 * * *",
    "parameters": {},
    "exclusions": [
      {
        "type": "weekday",
        "days": [5, 6],
        "tz_offset": 0
      }
    ],
    "is_active": true
  }
  ```
- `POST /api/notifications/trigger/{notification_id}` - Manually trigger an existing notification to run immediately, regardless of its schedule.

### 3. Custom Variables
Manage static variables that can be injected into your notification payloads.
- `GET /api/custom-variables/` - List all custom variables.
- `POST /api/custom-variables/` - Create a new custom variable.
  **Payload Example:**
  ```json
  {
    "name": "home_temperature",
    "value": "22.5°C"
  }
  ```
- `PUT /api/custom-variables/{id}` - Update the value of a custom variable dynamically from an external system.
  **Payload Example:**
  ```json
  {
    "name": "home_temperature",
    "value": "23.0°C"
  }
  ```

### 4. Data Sources
Manage dynamic data sources that fetch contextual information.
- `GET /api/data-sources/` - List configured data sources.
- `POST /api/data-sources/test` - Test a data source configuration and see the context variables it provides.
  **Payload Example:**
  ```json
  {
    "plugin_id": "weather_owm",
    "name": "Local Weather",
    "config": {
      "api_key": "YOUR_API_KEY",
      "city": "London"
    },
    "is_active": true
  }
  ```

## Example: Triggering a Notification via Curl

You can trigger a pre-configured notification from an external script using `curl`:

```bash
curl -X POST "http://localhost:8000/api/notifications/trigger/12" \
     -H "Authorization: Bearer kmu_your_token_here" \
     -H "Content-Type: application/json"
```

## Example: Updating a Custom Variable via Curl

If you have a custom variable `{home_temperature}` (ID: 5), you can update it dynamically from an external sensor:

```bash
curl -X PUT "http://localhost:8000/api/custom-variables/5" \
     -H "Authorization: Bearer kmu_your_token_here" \
     -H "Content-Type: application/json" \
     -d '{"name": "home_temperature", "value": "22.5°C"}'
```
