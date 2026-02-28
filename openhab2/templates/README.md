# OpenHAB Template Library - Universal Device Model

## Structure

```
templates/
├── switch/          # Switch profile template
├── sensor/          # Sensor profile template
├── light/           # Light profile template
└── README.md
```

## Template Instantiation

Templates are defined in `openhab_conf/scripts/template_engine.js` and support:
- **Parameter customization**: device ID, protocol-specific topics
- **Profile mapping**: capability-based channel definitions

## Available Templates

| Template | Capabilities | Channels |
|----------|--------------|----------|
| switch | on_off | power |
| sensor | measurement | temperature, humidity |
| light | on_off, dimmer | power, brightness |

## Usage

Templates are instantiated automatically when devices are discovered.
Manual instantiation via Rules or Main UI using the template engine script.
