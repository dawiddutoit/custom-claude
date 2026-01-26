# Advanced Conditional Card Patterns

## Table of Contents

1. Complex Logic Patterns
2. Real-World Use Cases
3. Workarounds and Limitations
4. Troubleshooting Guide
5. Best Practices

## 1. Complex Logic Patterns

### Nested AND/OR Logic

```yaml
visibility:
  - condition: and
    conditions:
      # Show during daytime...
      - condition: time
        after: "06:00:00"
        before: "22:00:00"
      # ...AND (someone is home OR security is armed)
      - condition: or
        conditions:
          - condition: state
            entity: person.john
            state: home
          - condition: state
            entity: alarm_control_panel.home
            state: armed_away
```

### Multiple Condition Combinations

```yaml
# Show card when ANY of these are true:
# - Battery below 20%
# - Device unavailable
# - Last updated > 24 hours ago
visibility:
  - condition: or
    conditions:
      - condition: numeric_state
        entity: sensor.motion_sensor_battery
        below: 20
      - condition: state
        entity: sensor.motion_sensor_battery
        state: unavailable
      - condition: template
        value_template: "{{ (as_timestamp(now()) - as_timestamp(states.sensor.motion_sensor_battery.last_updated)) > 86400 }}"
```

**Note:** Template conditions require creating template binary sensors (see Limitations section).

### Time-Based Visibility with Exceptions

```yaml
# Show during business hours, EXCEPT on weekends
visibility:
  - condition: and
    conditions:
      - condition: time
        after: "09:00:00"
        before: "17:00:00"
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
```

## 2. Real-World Use Cases

### Dynamic Dashboard Layouts

#### Show Camera When Motion Detected

```yaml
type: conditional
conditions:
  - condition: state
    entity: binary_sensor.motion_living_room
    state: "on"
card:
  type: camera
  entity: camera.living_room
```

#### Climate Controls When Someone Home

```yaml
type: vertical-stack
cards:
  - type: thermostat
    entity: climate.living_room
    visibility:
      - condition: or
        conditions:
          - condition: state
            entity: person.john
            state: home
          - condition: state
            entity: person.jane
            state: home
```

#### Low Battery Alert Section

```yaml
type: entities
title: Low Battery Devices
entities:
  - sensor.motion_sensor_battery
  - sensor.door_sensor_battery
visibility:
  - condition: or
    conditions:
      - condition: numeric_state
        entity: sensor.motion_sensor_battery
        below: 20
      - condition: numeric_state
        entity: sensor.door_sensor_battery
        below: 20
```

### Responsive Design Patterns

#### Mobile vs Desktop Layout

```yaml
# Mobile: Show compact chips
type: custom:mushroom-chips-card
chips:
  - type: entity
    entity: sensor.temperature
  - type: weather
    entity: weather.home
visibility:
  - condition: screen
    media_query: "(max-width: 600px)"

---

# Desktop: Show detailed cards
type: grid
columns: 3
cards:
  - type: sensor
    entity: sensor.temperature
  - type: weather-forecast
    entity: weather.home
visibility:
  - condition: screen
    media_query: "(min-width: 1280px)"
```

#### Tablet-Specific View

```yaml
visibility:
  - condition: screen
    media_query: "(min-width: 601px) and (max-width: 1279px)"
```

### User-Specific Views

#### Admin-Only Controls

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: "## Advanced Settings"

  - type: entities
    entities:
      - switch.developer_mode
      - switch.debug_logging
      - input_boolean.maintenance_mode
visibility:
  - condition: user
    users:
      - 1234567890abcdef  # Admin user ID
```

**Finding User IDs:**
1. Go to Settings → People
2. Click on user
3. User ID is in the URL: `/config/person/USER_ID_HERE`

### Context-Aware Alerts

#### Temperature Warning

```yaml
type: markdown
content: "⚠️ Temperature outside normal range!"
visibility:
  - condition: or
    conditions:
      - condition: numeric_state
        entity: sensor.temperature
        below: 18
      - condition: numeric_state
        entity: sensor.temperature
        above: 28
```

#### Occupied Room Indicators

```yaml
type: entities
title: Bedroom
entities:
  - light.bedroom
  - climate.bedroom
  - sensor.temperature_bedroom
visibility:
  - condition: state
    entity: binary_sensor.bedroom_occupied
    state: "on"
```

#### After-Hours Emergency Button

```yaml
type: button
name: Emergency Contact
icon: mdi:phone-alert
tap_action:
  action: perform-action
  perform_action: notify.mobile_app
  data:
    message: "Emergency call requested"
visibility:
  - condition: time
    after: "17:00:00"
    before: "09:00:00"
```

## 3. Workarounds and Limitations

### Attribute-Based Conditions

**Problem:** Cannot directly check entity attributes.

❌ This doesn't work:
```yaml
visibility:
  - condition: state
    entity: climate.living_room
    attribute: hvac_mode
    state: "cool"
```

✅ Workaround: Create template sensor
```yaml
# In configuration.yaml
template:
  - sensor:
      - name: "AC Mode"
        state: "{{ state_attr('climate.living_room', 'hvac_mode') }}"

# In dashboard
visibility:
  - condition: state
    entity: sensor.ac_mode
    state: "cool"
```

### Template Conditions

**Problem:** No template support in conditional cards.

❌ This doesn't work:
```yaml
visibility:
  - condition: template
    value_template: "{{ states('sensor.temperature') | float > 25 }}"
```

✅ Workaround: Create template binary sensor
```yaml
# In configuration.yaml
template:
  - binary_sensor:
      - name: "Temperature High"
        state: "{{ states('sensor.temperature') | float > 25 }}"

# In dashboard
visibility:
  - condition: state
    entity: binary_sensor.temperature_high
    state: "on"
```

### Complex Time Logic

For complex time-based conditions (sunrise/sunset, holidays, custom schedules), create helper entities:

```yaml
# In configuration.yaml
template:
  - binary_sensor:
      - name: "Daylight Hours"
        state: >
          {{ now() > state_attr('sun.sun', 'next_rising')
             and now() < state_attr('sun.sun', 'next_setting') }}
```

## 4. Troubleshooting Guide

### Card Not Hiding

**Symptoms:**
- Card always visible regardless of conditions
- Conditions seem correct but don't work

**Solutions:**
1. Exit edit mode (cards always visible when editing)
2. Check entity state in Developer Tools → States
3. Verify YAML indentation (very important)
4. Check for typos in entity_id
5. Ensure condition values match exactly (e.g., "on" vs true)

### User Condition Not Working

**Symptoms:**
- User-specific cards visible to all users
- User ID doesn't work

**Solutions:**
1. Verify using user ID, not username or email
2. Find correct ID in Settings → People → (click user) → check URL
3. User ID is alphanumeric string (e.g., 1234567890abcdef)
4. Clear browser cache if recently changed users

### Time Condition Not Working

**Symptoms:**
- Time-based visibility incorrect
- Cards show/hide at wrong times

**Solutions:**
1. Use 24-hour format with quotes: `"23:00:00"` not `"11:00 PM"`
2. Check Home Assistant timezone in Settings → System → General
3. Verify `after` time is before `before` time
4. For overnight ranges, split into two conditions with OR

### Numeric Condition Not Working

**Symptoms:**
- Numeric thresholds don't trigger
- Sensor-based visibility broken

**Solutions:**
1. Check sensor has numeric state (not "unknown" or "unavailable")
2. Use proper comparison operators (`above`/`below`, not `>` or `<`)
3. Verify sensor unit matches expectation (°C vs °F, kΩ vs Ω)
4. Add buffer zone to avoid flapping (e.g., above: 19, below: 21 instead of exact 20)

### Screen Condition Not Working

**Symptoms:**
- Responsive layout doesn't change
- Cards visible on wrong screen sizes

**Solutions:**
1. Test on actual device (browser resize ≠ responsive behavior)
2. Use correct media query syntax (parentheses, quotes)
3. Check for conflicting conditions (AND logic may prevent visibility)
4. Clear browser cache
5. Verify Home Assistant Companion app settings (may override)

## 5. Best Practices

### 1. Combine Conditional with State-Based Visibility

Use conditional card for complex logic, per-card visibility for simple conditions:

```yaml
# Complex logic: Conditional Card
type: conditional
conditions:
  - condition: and
    conditions:
      - condition: state
        entity: person.john
        state: home
      - condition: time
        after: "18:00:00"
card:
  # Simple visibility: Per-card property
  type: entities
  entities:
    - entity: light.bedroom
      visibility:
        - condition: state
          entity: light.bedroom
          state: "on"
```

### 2. Test Conditions in Edit Mode

Remember: Cards with `visibility` always render in edit mode. **Exit edit mode to test visibility behavior.**

### 3. Use Helper Entities for Complex Logic

Create template sensors/binary sensors for:
- Attribute-based conditions
- Template logic
- Complex calculations
- Reusable conditions across multiple cards

### 4. Combine with Mushroom Template Cards

```yaml
type: custom:mushroom-template-card
primary: "Windows Open"
secondary: "{{ states('sensor.windows_open') }} windows"
icon: mdi:window-open
visibility:
  - condition: numeric_state
    entity: sensor.windows_open
    above: 0
```

### 5. Use Screen Conditions for Responsive Design

```yaml
# Mobile: Compact view
type: custom:mushroom-chips-card
visibility:
  - condition: screen
    media_query: "(max-width: 600px)"

# Desktop: Detailed view
type: grid
columns: 3
visibility:
  - condition: screen
    media_query: "(min-width: 1280px)"
```

### 6. Document User IDs

Keep a reference of user IDs for maintenance:

```yaml
# User IDs Reference:
# john_admin: 1234567890abcdef
# jane_user: fedcba0987654321
# guest: abcdef1234567890

visibility:
  - condition: user
    users:
      - 1234567890abcdef  # john_admin
```

### 7. Add Buffer Zones for Numeric Conditions

Prevent flapping by adding hysteresis:

```yaml
# Show "too cold" alert when temp < 18
# Hide when temp > 20 (2-degree buffer)
visibility:
  - condition: numeric_state
    entity: sensor.temperature
    below: 18
```

### 8. Use Descriptive Entity Names

Create well-named template entities for clarity:

```yaml
# GOOD
template:
  - binary_sensor:
      - name: "AC Cooling Mode Active"
      - name: "Any Window Open"
      - name: "Daylight Hours"

# BAD
template:
  - binary_sensor:
      - name: "Helper 1"
      - name: "Check"
```

### 9. Group Related Conditions

Use vertical-stack to manage related conditional cards:

```yaml
type: vertical-stack
cards:
  # All cards in this stack share similar conditions
  - type: entities
    entities: [...]
    visibility: [...]
  - type: sensor
    entity: sensor.temp
    visibility: [...]
```

### 10. Consider Performance

- Avoid complex nested conditions on every card
- Use helper entities to pre-compute conditions
- Limit number of conditional cards per view (< 20 recommended)
- Cache frequently-checked states in template sensors

## Common Media Queries

```yaml
# Mobile (portrait)
media_query: "(max-width: 600px)"

# Mobile (landscape)
media_query: "(max-width: 900px) and (orientation: landscape)"

# Tablet (portrait)
media_query: "(min-width: 601px) and (max-width: 900px)"

# Tablet (landscape)
media_query: "(min-width: 901px) and (max-width: 1279px)"

# Desktop
media_query: "(min-width: 1280px)"

# Large desktop
media_query: "(min-width: 1920px)"

# Orientation-specific
media_query: "(orientation: landscape)"
media_query: "(orientation: portrait)"

# High-DPI displays
media_query: "(min-resolution: 192dpi)"
```

## Time Condition Examples

```yaml
# Daytime
after: "06:00:00"
before: "22:00:00"

# Night
after: "22:00:00"
before: "06:00:00"

# Business hours (weekdays only)
after: "09:00:00"
before: "17:00:00"
weekday:
  - mon
  - tue
  - wed
  - thu
  - fri

# Weekends only
weekday:
  - sat
  - sun

# Morning routine
after: "06:00:00"
before: "09:00:00"

# Evening routine
after: "18:00:00"
before: "23:00:00"
```
