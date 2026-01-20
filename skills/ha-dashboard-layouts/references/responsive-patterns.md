# Responsive Mobile-First Patterns

Design patterns for creating mobile-friendly Home Assistant dashboards.

## Mobile-First Principles

### 1. Test on Mobile During Development

**Critical:** Exit edit mode and view on actual phone.

- Browser resize ≠ mobile behavior
- Cards reflow differently than desktop resizing suggests
- Touch targets behave differently

### 2. Touch-Friendly Targets

- Minimum 44×44px tap targets
- Adequate spacing between interactive elements
- Use larger buttons on mobile views

```yaml
# Good: Spacious buttons
type: grid
columns: 2
square: true
cards:
  - type: button
    entity: light.bedroom
  - type: button
    entity: light.bathroom
```

### 3. Vertical Stacks Default

```yaml
# This pattern works well on mobile and desktop
type: vertical-stack
cards:
  - type: grid
    columns: 2  # Desktop: 2 columns, Mobile: 1 column
    cards:
      - type: button
        entity: light.bedroom
      - type: button
        entity: light.bathroom
```

### 4. Minimize Horizontal Scrolling

- Avoid wide grids that require panning
- Use `columns: 2` or `columns: 3` max for grid cards
- Test with narrow screen widths

**Bad:**
```yaml
type: grid
columns: 6  # Too wide for mobile
```

**Good:**
```yaml
type: grid
columns: 3  # Responsive
```

### 5. Top = Priority

- Place frequently-used controls at top of view
- Most important information loads first
- Users scroll down, not up

**Example: Priority Order**

```yaml
cards:
  - # 1. Quick status (top)
    type: custom:mushroom-chips-card
    chips:
      - type: weather
      - type: template
        content: "{{ states('sensor.lights_on') }} lights"

  - # 2. Frequently-used controls
    type: grid
    columns: 2
    cards:
      - type: button
        entity: light.all_lights
      - type: button
        entity: script.good_night

  - # 3. Detailed information (bottom)
    type: entities
    entities:
      - sensor.temperature
      - sensor.humidity
```

### 6. Collapsible Controls

```yaml
# Use collapsible controls on climate/media cards
type: thermostat
entity: climate.bedroom
collapsible_controls: true  # Hides controls until tapped
```

## Responsive Layout Patterns

### Pattern 1: Grid with Auto-Reflow

Native grid cards automatically reflow on mobile.

```yaml
type: grid
columns: 3  # Desktop: 3, Mobile: 1
cards:
  - type: sensor
    entity: sensor.temp1
  - type: sensor
    entity: sensor.temp2
  - type: sensor
    entity: sensor.temp3
```

**Mobile behavior:** Automatically stacks to 1 column.

### Pattern 2: Horizontal Stack of Vertical Stacks

Creates responsive two-column layout.

```yaml
type: horizontal-stack
cards:
  - type: vertical-stack  # Left column
    cards:
      - type: sensor
        entity: sensor.temperature
      - type: sensor
        entity: sensor.humidity

  - type: vertical-stack  # Right column
    cards:
      - type: button
        entity: light.living_room
      - type: button
        entity: light.bedroom
```

**Mobile behavior:** Stacks vertically (left column on top, right column below).

### Pattern 3: Conditional Card Visibility

Show/hide cards based on screen size using card-mod.

```yaml
type: custom:mod-card
card_mod:
  style: |
    @media (max-width: 768px) {
      ha-card { display: none; }
    }
card:
  type: entities
  entities:
    - sensor.detailed_stats
```

**Use when:** Desktop-only content not needed on mobile.

### Pattern 4: Compact Headers on Mobile

```yaml
type: custom:mushroom-template-card
primary: "{{ states('weather.home') | title }}"
secondary: "{{ state_attr('weather.home', 'temperature') }}°C"
icon: mdi:weather-sunny
card_mod:
  style: |
    ha-card {
      @media (max-width: 768px) {
        height: 80px !important;
      }
    }
```

## Common Responsive Issues

### Issue 1: Horizontal Stacks Too Wide

**Problem:** Horizontal stack with 4+ cards becomes cramped on mobile.

**Solution:** Use grid with `columns: 2` instead.

```yaml
# Bad
type: horizontal-stack
cards:
  - type: button
    entity: light.1
  - type: button
    entity: light.2
  - type: button
    entity: light.3
  - type: button
    entity: light.4

# Good
type: grid
columns: 2
cards:
  - type: button
    entity: light.1
  - type: button
    entity: light.2
  - type: button
    entity: light.3
  - type: button
    entity: light.4
```

### Issue 2: Text Too Small

**Problem:** Small text unreadable on mobile.

**Solution:** Use card-mod to increase font size on mobile.

```yaml
type: markdown
content: "Temperature: {{ states('sensor.temp') }}°C"
card_mod:
  style: |
    ha-card {
      @media (max-width: 768px) {
        font-size: 18px;
      }
    }
```

### Issue 3: Dense Information Overload

**Problem:** Too much information on single screen.

**Solution:** Use tabs or navigation to split content.

```yaml
# Create separate views
views:
  - title: Overview
    path: overview
    cards:
      - type: button
        name: Climate Details
        tap_action:
          action: navigate
          navigation_path: /lovelace/climate

  - title: Climate
    path: climate
    subview: true
    cards:
      # Detailed climate cards
```

## Mobile Dashboard Example

Minimalist mobile-first dashboard.

```yaml
title: Home
views:
  - title: Home
    path: home
    type: sections
    sections:
      # Status chips at top (highest priority)
      - type: grid
        cards:
          - type: custom:mushroom-chips-card
            chips:
              - type: weather
                entity: weather.home
              - type: template
                icon: mdi:lightbulb
                content: "{{ states('sensor.lights_on') }}"

      # Quick actions (frequently used)
      - title: Quick Actions
        type: grid
        columns: 2
        cards:
          - type: button
            entity: light.all_lights
            name: All Lights
          - type: button
            name: Good Night
            tap_action:
              action: perform-action
              perform_action: script.good_night

      # Climate (important but less frequent)
      - title: Climate
        type: grid
        cards:
          - type: thermostat
            entity: climate.living_room
            collapsible_controls: true
          - type: sensor
            entity: sensor.temperature
```

## Testing Checklist

- [ ] Test on actual mobile device (not just browser resize)
- [ ] Verify tap targets are 44×44px minimum
- [ ] Check for horizontal scrolling
- [ ] Confirm text is readable without zooming
- [ ] Test navigation flows
- [ ] Verify controls are reachable with one hand
- [ ] Check loading time on mobile network
- [ ] Test landscape and portrait orientations

## Official Documentation

- [Mobile Dashboard Tips - Home Assistant Community](https://community.home-assistant.io/)
