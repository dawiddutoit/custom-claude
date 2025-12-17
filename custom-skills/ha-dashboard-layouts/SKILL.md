---
name: ha-dashboard-layouts
description: "Design and implement Home Assistant Lovelace dashboard layouts including Sections View, grid cards, stacks (horizontal/vertical), and layout-card for responsive mobile-first dashboards. Use when creating HA dashboards, organizing cards, implementing responsive designs, combining layouts, or working with Sections View (2024+), masonry, panel, or sidebar layouts."
---

# Home Assistant Dashboard Layouts

Build responsive, mobile-first Home Assistant Lovelace dashboards using native layout types and custom layout cards.

## Overview

This skill covers Home Assistant's layout systems:
- **Sections View** (2024+ default): Drag-and-drop Z-Grid layout with automatic mobile responsiveness
- **Grid Cards**: Precise column control with auto-stacking on mobile
- **Stacks**: Horizontal and vertical card grouping with nesting patterns
- **Layout-Card** (HACS custom): Advanced CSS Grid with media queries
- **Other View Types**: Masonry, Panel, Sidebar

All patterns emphasize mobile-first design and progressive enhancement.

## Quick Start

### Sections View (Recommended for New Dashboards)

```yaml
# Modern approach with drag-and-drop editing
title: Home
views:
  - title: Overview
    path: overview
    type: sections  # Default in HA 2024.3+
    sections:
      - title: Climate
        type: grid
        cards:
          - type: thermostat
            entity: climate.living_room
          - type: sensor
            entity: sensor.temperature
```

**Key Features:**
- Drag-and-drop card positioning
- Z-Grid layout (left-to-right, wrapping to new rows)
- Automatic mobile column reflow
- Width adjustment via UI slider (no YAML)

### Grid Card (Native)

```yaml
# Precise column control
type: grid
columns: 3  # Auto-stacks to 1 column on mobile
square: false
cards:
  - type: button
    entity: light.bedroom
  - type: button
    entity: light.living_room
  - type: button
    entity: light.kitchen
```

### Horizontal Stack

```yaml
# Group cards side-by-side
type: horizontal-stack
cards:
  - type: button
    entity: light.bedroom
  - type: button
    entity: light.bathroom
```

## Layout Decision Tree

**Choose your layout approach:**

```
START
│
├─ Need drag-and-drop editing?
│  └─ YES → Use Sections View (default 2024+)
│
├─ Need precise CSS Grid control?
│  └─ YES → Use layout-card (HACS) with media queries
│
├─ Need simple column layout?
│  └─ YES → Use native Grid Card
│
├─ Need side-by-side cards?
│  └─ YES → Use horizontal-stack
│
└─ Need top-to-bottom cards?
   └─ YES → Use vertical-stack
```

## View Types

### 1. Sections View (Default 2024+)

**Best for:** General purpose, mobile-first dashboards

```yaml
views:
  - title: Home
    type: sections
    sections:
      - title: Quick Actions
        type: grid
        cards:
          - type: button
            entity: light.all_lights
          - type: button
            entity: script.good_night

      - title: Climate
        type: grid
        columns: 2
        cards:
          - type: thermostat
            entity: climate.living_room
          - type: sensor
            entity: sensor.temperature
```

**Z-Grid Behavior:**
- Sections flow left-to-right
- Wrap to new row when current row is full
- Row height = tallest section in that row
- Column widths remain constant

**Mobile Responsiveness:**
- Automatic column reflow based on screen width
- Test on mobile during editing (card behavior differs from desktop)
- Keep frequently-used controls in top-left (first to load)

### 2. Masonry View

**Best for:** Information-dense displays, space-efficient layouts

```yaml
views:
  - title: Overview
    type: masonry
    cards:
      - type: weather-forecast
        entity: weather.home
      - type: sensor
        entity: sensor.temperature
      # Cards auto-pack to fill vertical space
```

**Characteristics:**
- Auto-packed columns
- Unpredictable layout (cards fill available space)
- Good for dashboards with varying card heights

### 3. Panel View

**Best for:** Full-width single card (maps, cameras, full-screen visualizations)

```yaml
views:
  - title: Map
    type: panel
    cards:
      - type: map
        entities:
          - person.john
          - person.jane
```

### 4. Sidebar View

**Best for:** Two-column desktop layouts

```yaml
views:
  - title: Dashboard
    type: sidebar
    cards:
      - type: weather-forecast  # Main content (wide column)
        entity: weather.home
    sidebar:
      - type: entities  # Sidebar content (narrow column)
        entities:
          - sensor.temperature
```

**Note:** Desktop-focused, may not work well on mobile.

## Grid Card Patterns

### Basic Grid

```yaml
type: grid
cards:
  - type: button
    entity: light.living_room
  - type: button
    entity: light.bedroom
  - type: button
    entity: light.kitchen
  - type: button
    entity: light.bathroom
square: false  # Allow rectangular cards (default: true)
columns: 2     # Cards per row (default: auto-calculated)
```

### Responsive 3-Column Grid

```yaml
type: grid
columns: 3  # Desktop: 3 columns, Mobile: auto-stacks to 1
square: false
cards:
  - type: sensor
    entity: sensor.temp_bedroom
  - type: sensor
    entity: sensor.temp_living_room
  - type: sensor
    entity: sensor.temp_office
```

**Mobile Behavior:**
- Grid cards automatically reflow on narrow screens
- No media queries needed for basic responsiveness

## Stack Patterns

### Horizontal Stack (Side-by-Side)

```yaml
type: horizontal-stack
cards:
  - type: button
    entity: light.bedroom
    name: Bedroom
  - type: button
    entity: light.bathroom
    name: Bathroom
```

**Use when:** You want cards to appear side-by-side on desktop and mobile.

### Vertical Stack (Top-to-Bottom)

```yaml
type: vertical-stack
cards:
  - type: entities
    entities:
      - light.bedroom
  - type: thermostat
    entity: climate.bedroom
  - type: sensor
    entity: sensor.temperature
```

**Use when:** You want cards to stack vertically regardless of screen size.

### Nested Stacks (Two-Column Layout)

```yaml
# Horizontal stack of vertical stacks = responsive two-column layout
type: horizontal-stack
cards:
  - type: vertical-stack  # Left column
    cards:
      - type: sensor
        entity: sensor.temperature
      - type: sensor
        entity: sensor.humidity
      - type: sensor
        entity: sensor.pressure

  - type: vertical-stack  # Right column
    cards:
      - type: button
        entity: light.living_room
      - type: button
        entity: light.bedroom
      - type: button
        entity: light.kitchen
```

**Mobile Behavior:** Horizontal stacks of vertical stacks will stack vertically on mobile, creating a responsive single-column layout.

**Best Practice:** This is the recommended pattern for creating responsive two-column layouts that gracefully degrade to single column on mobile.

## Layout-Card (HACS Custom)

**Installation:** HACS → Frontend → Search "layout-card"

**When to use:**
- Need precise CSS Grid control
- Require media queries for complex responsive behavior
- Want to use grid-template-areas for named regions
- Need auto-fill/auto-fit responsive columns

### Basic Grid Layout

```yaml
type: custom:layout-card
layout_type: grid
layout:
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr))
  grid-template-rows: auto
  grid-gap: 8px
cards:
  - type: button
    entity: light.living_room
  - type: button
    entity: light.bedroom
  - type: button
    entity: light.kitchen
```

### Responsive with Media Queries

```yaml
type: custom:layout-card
layout_type: grid
layout:
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr))
  grid-gap: 8px
  mediaquery:
    "(max-width: 600px)":
      grid-template-columns: 1fr  # Mobile: single column
    "(min-width: 1280px)":
      grid-template-columns: repeat(4, 1fr)  # Desktop: 4 columns
cards:
  - type: button
    entity: light.living_room
  # ...
```

### Grid Areas (Named Regions)

```yaml
type: custom:layout-card
layout_type: grid
layout:
  grid-template-columns: 1fr 1fr 1fr
  grid-template-rows: auto
  grid-template-areas: |
    "header header header"
    "sidebar main main"
    "footer footer footer"
cards:
  - type: markdown
    content: "# Dashboard Header"
    view_layout:
      grid-area: header

  - type: entities
    entities:
      - sensor.temperature
    view_layout:
      grid-area: sidebar

  - type: map
    entities:
      - person.john
    view_layout:
      grid-area: main

  - type: markdown
    content: "Footer content"
    view_layout:
      grid-area: footer
```

## Mobile-First Best Practices

### 1. Test on Mobile During Development

- Exit edit mode and view on actual phone
- Browser resize doesn't accurately represent mobile behavior
- Cards reflow differently than desktop resizing suggests

### 2. Touch-Friendly Targets

- Minimum 44×44px tap targets
- Ensure adequate spacing between interactive elements
- Use larger buttons on mobile views

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

### 5. Top = Priority

- Place frequently-used controls at top of view
- Most important information loads first
- Users scroll down, not up

### 6. Collapsible Controls

```yaml
# Use collapsible controls on climate/media cards
type: thermostat
entity: climate.bedroom
collapsible_controls: true  # Hides controls until tapped
```

## Real-World Examples

### Minimalist Mobile Dashboard

```yaml
title: Home
views:
  - title: Home
    path: home
    type: sections
    sections:
      - type: grid
        cards:
          # Status chips at top
          - type: custom:mushroom-chips-card
            chips:
              - type: weather
                entity: weather.home
              - type: template
                icon: mdi:lightbulb
                content: "{{ states('sensor.lights_on') }}"

      - title: Climate
        type: grid
        cards:
          - type: thermostat
            entity: climate.living_room
          - type: sensor
            entity: sensor.temperature

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
```

### Desktop Grid Layout

```yaml
views:
  - title: Overview
    path: overview
    type: custom:layout-card
    layout_type: grid
    layout:
      grid-template-columns: 2fr 1fr
      grid-template-rows: auto auto 1fr
      grid-gap: 8px
      mediaquery:
        "(max-width: 1024px)":
          grid-template-columns: 1fr
    cards:
      # Large graph spanning 2 rows
      - type: custom:apexcharts-card
        graph_span: 24h
        view_layout:
          grid-row: span 2
        series:
          - entity: sensor.power_consumption

      # Status column
      - type: vertical-stack
        cards:
          - type: weather-forecast
            entity: weather.home
          - type: entities
            entities:
              - sensor.temperature
              - sensor.humidity

      # Controls
      - type: grid
        columns: 3
        cards:
          - type: button
            entity: light.living_room
          - type: button
            entity: light.bedroom
          - type: button
            entity: light.kitchen
```

## Navigation Between Views

### Define View Paths

```yaml
views:
  - title: Home
    path: home  # URL: /lovelace/home
    cards: [...]

  - title: Bedroom
    path: bedroom  # URL: /lovelace/bedroom
    cards: [...]
```

### Navigate with Buttons

```yaml
type: button
name: Go to Bedroom
icon: mdi:bed
tap_action:
  action: navigate
  navigation_path: /lovelace/bedroom
```

### Subviews with Back Button

```yaml
views:
  - title: Bedroom Details
    path: bedroom-details
    subview: true  # Shows back button
    back_path: /lovelace/home  # Optional custom back path
```

## Organizational Strategies

### By Room (Recommended for Families)

```
Views:
├── Home (overview)
├── Living Room
├── Bedroom
├── Kitchen
└── Outdoors
```

**Pros:** Intuitive for family members, matches physical space
**Cons:** Cross-room automations harder to visualize

### By Function (Recommended for Technical Users)

```
Views:
├── Lighting
├── Climate
├── Security
├── Media
└── Energy
```

**Pros:** Single-domain control, good for technical users
**Cons:** Less intuitive for non-technical users

### Hybrid Approach (Best of Both)

```
Main Dashboard:
├── Home (overview/status)
├── Rooms
│   ├── Living Room
│   ├── Bedroom
│   └── Kitchen
└── Systems
    ├── Climate
    ├── Security
    └── Energy
```

**Implementation:**
- Create "Home" overview with critical status indicators
- Use navigation buttons to link to detailed views
- Use conditional visibility to show room cards only when occupied

## References

For more detailed information, see:

- [references/view-types.md](references/view-types.md) - Complete view type configurations
- [references/responsive-patterns.md](references/responsive-patterns.md) - Mobile-first design patterns
- [references/layout-card-advanced.md](references/layout-card-advanced.md) - Advanced layout-card techniques

## Official Documentation

- [Views - Home Assistant](https://www.home-assistant.io/dashboards/views/)
- [Grid card - Home Assistant](https://www.home-assistant.io/dashboards/grid/)
- [Layout-Card GitHub](https://github.com/thomasloven/lovelace-layout-card)
