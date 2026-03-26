# Client Intake Form Reference

This page describes every field in `configs/client_intake_template.yaml` and the accepted values.

The template file itself (`client_intake_template.yaml`) should be sent to the client before any setup work begins. They fill it in and return it to the Pipeline TD.

---

## `studio`

| Field | Type | Example | Notes |
|---|---|---|---|
| `name` | string | `"Acme VFX Studio"` | Full legal name. Used verbatim in the license key — must match exactly on all machines |
| `project_code` | string | `"ACME_PROJ_2026"` | UPPERCASE_UNDERSCORE. Becomes the root folder name on the NAS |
| `timezone` | string | `"Asia/Kolkata"` | IANA timezone. Used for log timestamps and metadata |

---

## `filesystem`

| Field | Type | Example | Notes |
|---|---|---|---|
| `studio_root` | string | `"/mnt/nas/projects"` | Absolute NAS path. Windows: `\\NAS01\projects` or `Z:\projects` |
| `os_platform` | enum | `"linux"` | `windows` / `linux` / `mac` |

---

## `project_structure`

| Field | Type | Example | Notes |
|---|---|---|---|
| `sequences.count` | int | `10` | Pre-create this many sequence folders |
| `sequences.naming` | format string | `"sq{:03d}"` | Python format string → `sq001`, `sq002`. Use `ep{:02d}` for episodic |
| `shots.per_sequence` | int | `20` | Shots to pre-create per sequence |
| `shots.naming` | format string | `"sh{:03d}0"` | `sh0010`, `sh0020` (increment of 10). Use `"sh{:04d}"` for increment of 1 |

---

## `departments`

A list of task departments to create work/publish/render/cache folders for under every shot.

```yaml
departments:
  - anim
  - comp
  - fx
  - lighting
  - lookdev
  - model
  - render
  - rig
  # Optional
  - previs
  - roto
  - matte_paint
  - editorial
  - motion_graphics
```

> **Rule:** Only list departments that will be actively staffed on this project. Empty unused folders create confusion on the NAS.

---

## `dcc_software`

The DCC applications your studio has valid software licenses for.

```yaml
dcc_software:
  - maya         # .ma, .mb work and publish files
  - nuke         # .nk, .nkc scripts
  - houdini      # .hip, .hipnc, .hiplc
  - blender      # .blend
  # Optional
  - c4d
  - 3dsmax
  - substance
  - resolve
```

---

## `asset_types`

The categories of assets that will be built for this project.

```yaml
asset_types:
  - char        # Characters (hero, background)
  - prop        # Handheld or scene props
  - env         # Environment / set dressing
  - vehicle     # Cars, ships, aircraft
  - fx          # Simulation source geometry
  # Optional
  - crowd
  - matte_paint
  - hdri
```

---

## `technical`

| Field | Type | Accepted Values | Notes |
|---|---|---|---|
| `frame_rate` | number | `24`, `25`, `30`, `48`, `60`, `23.976`, `29.97` | Project frame rate in FPS |
| `frame_padding` | int | `3`, `4` | Digits in frame numbers (`0001` vs `001`) |
| `color_space` | string | `ACEScg`, `sRGB`, `Linear`, `scene_linear` | Primary working colour space |
| `image_format` | string | `EXR`, `DPX`, `TIFF`, `PNG` | Primary render output format |
| `delivery_format` | string | `H264_MP4`, `ProRes`, `DNxHD` | Dailies deliverable codec |
| `resolution` | string | `1920x1080`, `2048x1556`, `3840x2160` | Project canvas resolution |
| `bit_depth` | int | `8`, `16`, `32` | EXR bit depth |

---

## `pipeline`

| Field | Type | Default | Notes |
|---|---|---|---|
| `enable_dependency_tracking` | bool | `false` | Scan `.ma`/`.nk` files for upstream file refs on every publish |
| `versioning_padding` | int | `3` | `3` → `v001`, `4` → `v0001` |
| `naming_separator` | string | `"_"` | Character between tokens in filenames |
| `enable_dailies_watermark` | bool | `false` | Burn studio name + date into daily playblasts |
| `enable_auto_backup` | bool | `false` | Auto version-bump when artist manually saves |

---

## `contacts`

Pipeline admin contacts. Used for license generation records and support escalation.

```yaml
contacts:
  pipeline_td:
    name:  "Jordan Smith"
    email: "jordan@studioacme.com"
  vfx_supervisor:
    name:  "Alex Reyes"
    email: "alex.reyes@studioacme.com"
  it_admin:
    name:  "Sam Patel"
    email: "it@studioacme.com"
```
