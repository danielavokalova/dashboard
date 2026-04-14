# GDS / NDC Connectors

<!-- tags: GDS, NDC, connector, Amadeus, Sabre, Travelport, Galileo, API, source -->

Connectors define which content sources (GDS, NDC, LCC) GOL IBE uses to retrieve fares and availability.

## Available connectors

| Connector | Type | Content |
|-----------|------|---------|
| Amadeus | GDS | Full-service carriers worldwide |
| Sabre | GDS | Full-service carriers worldwide |
| Travelport (Galileo) | GDS | Full-service carriers worldwide |
| Lufthansa Group NDC | NDC | LH, Austrian, SWISS direct fares |
| British Airways NDC | NDC | BA direct fares and ancillaries |

## Add a connector

1. Go to **Settings → Advanced Settings → Connectors**.
2. Click **Add connector**.
3. Select the connector type.
4. Enter your credentials (PCC/Office ID, password, queue numbers).
5. Click **Test connection**.
6. If successful, click **Activate**.

> ℹ️ Connector credentials are provided by your GDS account manager. Contact GOL support if you need help obtaining them.
