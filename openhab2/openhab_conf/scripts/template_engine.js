/**
 * Universal Device Model - Template Engine
 * Reusable device templates, instantiation, parameter customization
 */

var LOG = Java.type("org.slf4j.LoggerFactory").getLogger("template_engine");

// Template library - reusable device templates
var TEMPLATES = {
    switch: {
        profile: "switch",
        version: "1.0",
        items: [
            { name: "power", type: "Switch", icon: "switch" }
        ],
        mqttTopics: { state: "devices/switch_{id}/state", command: "devices/switch_{id}/state/set" },
        httpPaths: { power: "/devices/{id}/power" },
        capabilities: ["on_off"]
    },
    sensor: {
        profile: "sensor",
        version: "1.0",
        items: [
            { name: "temperature", type: "Number", icon: "temperature" },
            { name: "humidity", type: "Number", icon: "humidity" }
        ],
        mqttTopics: { temp: "devices/sensor_{id}/temp", humidity: "devices/sensor_{id}/humidity" },
        httpPaths: { temperature: "/devices/{id}/temperature", humidity: "/devices/{id}/humidity" },
        capabilities: ["measurement", "temperature", "humidity"]
    },
    light: {
        profile: "light",
        version: "1.0",
        items: [
            { name: "power", type: "Switch", icon: "light" },
            { name: "brightness", type: "Dimmer", icon: "light" }
        ],
        mqttTopics: { state: "devices/light_{id}/state", brightness: "devices/light_{id}/brightness" },
        httpPaths: { on: "/devices/{id}/on", brightness: "/devices/{id}/brightness" },
        capabilities: ["on_off", "dimmer"]
    }
};

function instantiateDeviceTemplate(deviceId, profile, protocol) {
    var template = TEMPLATES[profile];
    if (!template) {
        LOG.warn("No template for profile: {}", profile);
        return null;
    }
    
    var config = {
        deviceId: deviceId,
        profile: profile,
        protocol: protocol,
        mqttTopics: substituteParams(template.mqttTopics, deviceId),
        httpPaths: substituteParams(template.httpPaths, deviceId)
    };
    
    LOG.info("Instantiated template {} for device {} via {}", profile, deviceId, protocol);
    return config;
}

function substituteParams(obj, id) {
    var result = {};
    for (var key in obj) {
        result[key] = obj[key].replace(/\{id\}/g, id).replace(/\{\w+\}/g, id);
    }
    return result;
}

function getTemplate(profile) {
    return TEMPLATES[profile] ? JSON.parse(JSON.stringify(TEMPLATES[profile])) : null;
}

function listTemplates() {
    return Object.keys(TEMPLATES).map(function(p) {
        return { profile: p, version: TEMPLATES[p].version, capabilities: TEMPLATES[p].capabilities };
    });
}

