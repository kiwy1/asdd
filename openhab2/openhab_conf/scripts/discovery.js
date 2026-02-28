/**
 * Universal Device Model - Discovery Engine
 * Auto-discovery, capability negotiation, device profiling
 */

var PROFILES = {
    "switch": { capabilities: ["on_off"], channels: ["power", "state"] },
    "sensor": { capabilities: ["measurement"], channels: ["temperature", "humidity"] },
    "light": { capabilities: ["on_off", "dimmer"], channels: ["power", "brightness"] }
};

var discoveredDevices = {};
var LOG = Java.type("org.slf4j.LoggerFactory").getLogger("discovery");

function handleDiscovery(payload, protocol) {
    try {
        var data = JSON.parse(payload);
        var deviceId = data.id || "unknown_" + Date.now();
        var profile = data.profile || detectProfile(data);
        
        discoveredDevices[deviceId] = {
            id: deviceId,
            profile: profile,
            protocol: protocol,
            capabilities: PROFILES[profile] ? PROFILES[profile].capabilities : [],
            timestamp: new Date().getTime()
        };
        
        LOG.info("Discovered device: {} profile: {} via {}", deviceId, profile, protocol);
        
        // Trigger template instantiation if available
        if (typeof instantiateDeviceTemplate === "function") {
            instantiateDeviceTemplate(deviceId, profile, protocol);
        }
    } catch (e) {
        LOG.warn("Discovery parse error: {}", e.message);
    }
}

function detectProfile(data) {
    if (data.temperature !== undefined || data.temp !== undefined) return "sensor";
    if (data.brightness !== undefined || data.on !== undefined) return "light";
    if (data.power !== undefined || data.state !== undefined) return "switch";
    return "generic";
}

function scanAllProtocols() {
    // MQTT devices are discovered via UDM_Discovery_CoAP (CoAP bridge publishes to MQTT)
    // HTTP devices: could trigger HTTP GET to simulator discovery endpoint
    LOG.info("Discovery scan triggered");
    return discoveredDevices;
}

function getDiscoveredDevices() {
    return discoveredDevices;
}

function getDeviceProfile(deviceId) {
    var dev = discoveredDevices[deviceId];
    return dev ? dev.profile : null;
}

