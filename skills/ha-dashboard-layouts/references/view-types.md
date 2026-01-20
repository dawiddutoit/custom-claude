# View Types

Home Assistant dashboard view types beyond the standard card-based layout.

## Overview

- **Masonry** - Auto-packed columns for information-dense displays
- **Panel** - Full-screen single card
- **Sidebar** - Two-column desktop layout

## Masonry View

Auto-packed columns with unpredictable but space-efficient layout.

```yaml
views:
  - title: Overview
    type: masonry
    cards:
      - type: weather-forecast
        entity: weather.home
      - type: sensor
        entity: sensor.temperature
      - type: sensor
        entity: sensor.humidity
      # Cards auto-pack to fill vertical space
```

**Characteristics:**
- Auto-packed columns
- Unpredictable layout (cards fill available space)
- Good for dashboards with varying card heights
- Not recommended for precise layouts

**Use when:**
- Information-dense displays
- Card order doesn't matter
- Maximizing space utilization

**Avoid when:**
- Need predictable card positions
- Mobile-first design (unpredictable on mobile)

## Panel View

Full-width single card filling entire view.

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

**Important:** Only ONE card allowed per panel view.

**Use cases:**
- Full-screen maps
- Kiosk displays
- Camera feeds
- Full-width visualizations
- Embedded iframes

**Example: Full-Screen Camera**

```yaml
views:
  - title: Front Door
    type: panel
    cards:
      - type: picture-entity
        entity: camera.front_door
        camera_view: live
```

## Sidebar View

Two-column layout with main content and narrow sidebar.

```yaml
views:
  - title: Dashboard
    type: sidebar
    cards:
      - type: weather-forecast  # Main content (wide column)
        entity: weather.home
      - type: custom:apexcharts-card  # Main content
        graph_span: 24h
        series:
          - entity: sensor.temperature
    sidebar:
      - type: entities  # Sidebar content (narrow column)
        entities:
          - sensor.temperature
          - sensor.humidity
          - sensor.pressure
      - type: button
        entity: light.all_lights
```

**Layout:**
- Main content: Wide left column
- Sidebar: Narrow right column
- Sidebar width: ~25% of screen

**Mobile behavior:**
- Sidebar stacks below main content on narrow screens

**Use when:**
- Desktop-focused dashboards
- Need persistent controls/status visible while viewing main content
- Two-zone information hierarchy (primary + secondary)

**Avoid when:**
- Mobile-first design (sidebar becomes bottom section)
- Need more than two columns

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

### By Room (Family-Friendly)

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

### By Function (Technical Users)

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

### Hybrid Approach

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
- "Home" overview with critical status indicators
- Navigation buttons to detailed views
- Conditional visibility for room cards (show only when occupied)

## Official Documentation

- [Views - Home Assistant](https://www.home-assistant.io/dashboards/views/)
