---
identifier: openscad-library-reference
type: knowledge
description: Quick reference for major OpenSCAD libraries (BOSL2, NopSCADlib, MCAD, dotSCAD, YAPP, etc.) with usage patterns
version: 1.0.0
tags: [openscad, libraries, reference, bosl2, nopscadlib, mcad, dotscad, yapp]
---

# OpenSCAD Libraries Quick Reference

All libraries are installed in `/home/unit/.local/share/OpenSCAD/libraries/`

## Core Libraries

### BOSL2 (Most Versatile)
**Path:** `BOSL2/std.scad`
**Purpose:** Attachments, rounding, distribution, gears, threading, primitives

**Include:**
```openscad
include <BOSL2/std.scad>
```

**Key Features:**
| Feature | Module | Example |
|---------|--------|---------|
| Semantic positioning | up(), left(), right() | `up(10) cube([20,20,10])` |
| Attachments | attach(), anchor | `attach(TOP) cyl(...)` |
| Smart shapes | cuboid(), cyl() | `cuboid([40,30,20], rounding=3)` |
| Distribution | xcopies(), grid_copies() | `xcopies(12, n=5) sphere()` |
| Gears | spur_gear() | `spur_gear(pitch=3, teeth=20)` |
| Threads | threaded_rod() | `threaded_rod(d=8, l=30)` |

**Common Submodules:**
```openscad
include <BOSL2/gears.scad>        // Gear generation
include <BOSL2/threading.scad>    // Threaded parts
include <BOSL2/screws.scad>       // Screw utilities
include <BOSL2/hinges.scad>       // Hinge generation
include <BOSL2/nema_steppers.scad> // Motor mounts
```

---

### NopSCADlib (Hardware Vitamins)
**Path:** `NopSCADlib/lib.scad`
**Purpose:** Mechanical hardware, connectors, electronics, fasteners

**Include:**
```openscad
include <NopSCADlib/lib.scad>
```

**Key Features:**
| Component | Module | Example |
|-----------|--------|---------|
| Screws | screw() | `screw(M3_cap_screw, 10)` |
| Nuts | nut() | `nut(M3_nut)` |
| Bolts/Fasteners | washer() | `washer(M3_washer)` |
| Bearings | ball_bearing() | `ball_bearing(625)` |
| Motors | NEMA() | `NEMA(17)` |
| Heatsinks | heatsink() | `heatsink(TO220_heatsink)` |
| Connectors | D_connector() | `D_connector(15pin)` |
| Batteries | battery() | `battery(AA)` |
| LEDs | led() | `led(3mm)` |
| Resistors | resistor() | `resistor(0805)` |

**Common Usage:**
```openscad
include <NopSCADlib/lib.scad>

// Mount a NEMA17 stepper
stepper = NEMA(17);

// Use with accuracy for assembly simulation
screw_hole = screw_clearance_radius(M3_cap_screw);
```

---

### MCAD (Official Library)
**Path:** `MCAD/` directory
**Purpose:** Motors, materials, shapes, mathematical operations

**Key Modules:**
```openscad
use <MCAD/stepper.scad>           // Stepper motors
use <MCAD/materials.scad>          // Material colors
use <MCAD/shapes.scad>             // Additional shapes
use <MCAD/gears.scad>              // Basic gears
use <MCAD/involute_gears.scad>    // Advanced gears
use <MCAD/motors.scad>             // Motor models
```

**Example:**
```openscad
use <MCAD/stepper.scad>

// 28BYJ-48 stepper motor
nema17_motor();

// Servo
servo_side_view();
```

---

### dotSCAD (Advanced Math & Patterns)
**Path:** `dotSCAD/dotSCAD.scad`
**Purpose:** Bezier curves, paths, Voronoi patterns, Perlin noise, mathematical utilities

**Include:**
```openscad
include <dotSCAD/dotSCAD.scad>
```

**Key Features:**
| Feature | Module | Use Case |
|---------|--------|----------|
| Bezier curves | bezier_line() | Smooth decorative curves |
| Voronoi | voronoi() | Complex tessellations |
| Perlin noise | perlin_noise() | Organic patterns |
| Path operations | path_extrude() | Paths as shapes |
| Loft | loft() | Smooth transitions |

---

## Electronics & Enclosures

### YAPP (Electronics Enclosures)
**Path:** `YAPP/YAPPgenerator_v3.scad`
**Purpose:** Parametric electronics enclosure generation

**Include:**
```openscad
include <YAPP/YAPPgenerator_v3.scad>
```

**Key Features:**
- Parametric box generation
- Built-in mounting posts
- Cable glands
- Button/switch cutouts
- Customizable tolerances

**Example:**
```openscad
include <YAPP/YAPPgenerator_v3.scad>

// Define box parameters
YappGen_SetupBox(
    box_width = 100,
    box_depth = 80,
    box_height = 50,
    wall_thickness = 2
);

// Render enclosure
YappGen_MakeBox();
```

---

### Arduino Mounting
**Path:** `arduino-mounting/arduino.scad`
**Purpose:** Arduino board mounts and enclosures

**Include:**
```openscad
use <arduino-mounting/arduino.scad>
```

**Key Features:**
- Arduino mounting brackets
- Case designs
- Standoff generators

---

### PCB Standoffs
**Path:** `pcb-standoffs/pcb_standoff.scad`
**Purpose:** Rapid PCB mounting standoff generation

**Include:**
```openscad
use <pcb-standoffs/pcb_standoff.scad>
```

---

## Robotics & Motion

### BOSL2 Stepper Motors
**Path:** `BOSL2/nema_steppers.scad`
**Purpose:** NEMA stepper motor models and mounting masks

**Include:**
```openscad
include <BOSL2/nema_steppers.scad>
```

**Key Features:**
| Motor | Model | Size |
|-------|-------|------|
| NEMA11 | NEMA(11) | 28.5mm |
| NEMA14 | NEMA(14) | 35.2mm |
| NEMA17 | NEMA(17) | 42.3mm |
| NEMA23 | NEMA(23) | 57.1mm |
| NEMA34 | NEMA(34) | 86.3mm |

---

### OpenSCAD_ServoArms
**Path:** `OpenSCAD_ServoArms/servo_arm.scad`
**Purpose:** Parametric servo arms for SG90/MG90 servos

**Include:**
```openscad
use <OpenSCAD_ServoArms/servo_arm.scad>
```

---

### Timing Belt & Pulleys
**Path:** `Pulleys/pulley.scad`
**Purpose:** GT2, GT3, HTD timing belt pulley generation

**Include:**
```openscad
use <Pulleys/pulley.scad>
```

**Key Features:**
- Belt profile generation
- Pulley dimensioning
- Synchronous motion design

---

### Threads Library
**Path:** `threads/threads.scad`
**Purpose:** Metric and imperial thread generation

**Include:**
```openscad
include <threads/threads.scad>
```

**Features:**
- Metric threads (M3, M4, M5, M6, etc.)
- Imperial threads
- Internal and external threads

**Example:**
```openscad
include <threads/threads.scad>

// M8 threaded rod
metric_thread(diameter=8, pitch=1.25, length=30);

// M8 threaded hole (internal)
metric_thread(diameter=8, pitch=1.25, length=10, internal=true);
```

---

## Fabrication & Storage

### Gridfinity
**Path:** `gridfinity/gridfinity-rebuilt-utility.scad`
**Purpose:** Parametric Gridfinity bins and baseplates

**Include:**
```openscad
include <gridfinity/gridfinity-rebuilt-utility.scad>
```

**Key Features:**
- Bin generation (all sizes)
- Baseplate generation
- Gridfinity utility functions
- Magnetic pocket support

---

### JointSCAD (Fabrication Joints)
**Path:** `JointSCAD/joint.scad`
**Purpose:** Parametric joint generation for fabrication

**Include:**
```openscad
use <JointSCAD/joint.scad>
```

**Joint Types:**
| Joint | Module | Use Case |
|-------|--------|----------|
| Dovetail | dovetail() | Wood joinery |
| Mortise/Tenon | mortise(), tenon() | Wood joinery |
| Finger | finger_joint() | Box joints |
| Bridle | bridle_joint() | Wood structures |
| Box | box_joint() | Cardboard/plywood |

---

### Extrusions (T-Slot)
**Path:** `extrusions/` directory
**Purpose:** 2020/8020 aluminum T-slot profile compatibility

**Modules:**
- 2020 profile generators
- Bracket geometries
- Slot-tab connectors

---

### Laser Cutting Support
**Path:** `lasercut/lasercut.scad`
**Purpose:** Convert 3D models to 2D for laser/CNC cutting

**Include:**
```openscad
use <lasercut/lasercut.scad>
```

---

### BOLTS (Standard Fasteners)
**Path:** `BOLTS/` directory
**Purpose:** Parametric standard nuts, bolts, bearings

**Key Features:**
- ISO standard fasteners
- Bearing specifications
- Material codes

---

## Library Selection Guide

### For Structural Design
**Choose BOSL2** for semantic positioning and rounding

### For Hardware Integration
**Choose NopSCADlib** for realistic mechanical components

### For Advanced Math
**Choose dotSCAD** for curves and complex patterns

### For Gridfinity Storage
**Choose gridfinity library** or NopSCADlib + BOSL2

### For 3D Printing Optimization
**Choose BOSL2** for quality rounding and anchoring

### For CNC/Laser Fabrication
**Choose JointSCAD** + lasercut library

---

## Common Include Pattern

```openscad
// Comprehensive setup for most projects
include <BOSL2/std.scad>
include <BOSL2/gears.scad>
include <BOSL2/threading.scad>
use <MCAD/stepper.scad>
use <NopSCADlib/lib.scad>

// For specialized projects
// include <YAPP/YAPPgenerator_v3.scad>
// include <gridfinity/gridfinity-rebuilt-utility.scad>
// use <JointSCAD/joint.scad>
```

---

## Performance Tips

1. **Include vs Use**
   - `include` makes all functions available
   - `use` for specific modules (faster parsing)

2. **Minimize includes**
   - Only include what you need
   - Use submodule includes for specific features

3. **Lazy Loading**
   - Comment out unused libraries during development
   - Enable for final render

4. **Library Quality**
   - BOSL2: Actively maintained, comprehensive
   - NopSCADlib: Well-documented, extensive
   - MCAD: Official, basic features
   - dotSCAD: Specialized, less common use
