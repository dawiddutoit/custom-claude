# Layout-Card (HACS Custom)

Advanced CSS Grid layout card with media queries and grid-template-areas.

## Installation

HACS → Frontend → Search "layout-card"

**Repository:** https://github.com/thomasloven/lovelace-layout-card

## When to Use

- Need precise CSS Grid control
- Require media queries for complex responsive behavior
- Want to use grid-template-areas for named regions
- Need auto-fill/auto-fit responsive columns

## Basic Grid Layout

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

## Responsive with Media Queries

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

## Grid Areas (Named Regions)

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

## Advanced Example: Desktop Grid with Spanning Cards

```yaml
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

## Common Patterns

### Auto-Fill Responsive Grid

```yaml
layout:
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr))
```

Cards automatically wrap to new row when space is limited.

### Fixed Desktop, Flexible Mobile

```yaml
layout:
  grid-template-columns: repeat(3, 1fr)  # Desktop: 3 columns
  mediaquery:
    "(max-width: 768px)":
      grid-template-columns: 1fr  # Mobile: 1 column
```

### Spanning Cards

```yaml
cards:
  - type: weather-forecast
    view_layout:
      grid-column: span 2  # Takes 2 columns
      grid-row: span 2     # Takes 2 rows
```

## Official Documentation

- [Layout-Card GitHub](https://github.com/thomasloven/lovelace-layout-card)
- [CSS Grid Guide](https://css-tricks.com/snippets/css/complete-guide-grid/)
