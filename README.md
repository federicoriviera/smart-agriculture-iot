# IoT Smart Agriculture Management System

## Table of Contents

- [Scenario - Smart Agriculture Adaptive Irrigation](#scenario---smart-agriculture-adaptive-irrigation)
- [Main Components](#main-components)
- [Environmental Node Telemetry Model (SenML+JSON)](#environmental-node-telemetry-model-senmljson)
- [Communication](#communication)
- [MQTT Topics & Data](#mqtt-topics--data)
- [MQTT Topics & Service Mapping](#mqtt-topics--service-mapping)

## Scenario - Smart Agriculture Adaptive Irrigation

Il progetto IoT Smart Agriculture simula un'infrastruttura intelligente per la gestione e l'ottimizzazione dell'irrigazione agricola. L'obiettivo è prevenire gli sprechi idrici, proteggere le colture e adattare le strategie in tempo reale in base alle condizioni meteorologiche (es. vento forte, pioggia, siccità improvvisa).

## Main Components

**Edge Layer (Environmental Node)** Il nodo agricolo intelligente è situato nel campo ed è dotato di sensori e attuatori per interagire in autonomia con l'ambiente.
*Sensors:*
* **Soil Humidity Sensor**: Misura la percentuale di umidità del terreno.
* **Wind Sensor**: Rileva la velocità del vento in km/h.
* **Rain Sensor**: Rileva la presenza di precipitazioni in corso.
* **Temperature**: Misura la temperatura dell'aria.
* **Battery Level**: Monitora lo stato energetico del dispositivo IoT.

*Actuators:*
* **Irrigation Pump**: Accende o spegne l'erogazione dell'acqua in base alla siccità o alla pioggia.
* **Rotation Motor**: Attiva o disattiva la rotazione del getto d'acqua (utile per non disperdere acqua in caso di forte vento).

**Cloud Layer (Data Manager)** Il servizio centrale che agisce come coordinatore del sistema.
* **Digital Twin Manager**: Mantiene lo stato aggiornato di tutti i nodi ambientali attivi (`EnvNodeDigitalTwin`).
* **Alert**: per generare allerte specifiche:
  * *Drought Alert*: Terreno eccessivamente secco.
  * *Storm Alert*: Vento oltre la soglia di sicurezza.
  * *Maintenance Alert*: Batteria scarica.
* **Adaptive Logic**: In caso di pioggia o vento forte, invia comandi immediati per fermare le pompe o la rotazione, mitigando lo spreco idrico. Al rientro dei parametri normali, o se è necessaria acqua, invia comandi di irrigazione.
* **New configs**: può mandare nuove configurazioni (nuove soglie operative stagionali) ai nodi agricoli.

## Environmental Node Telemetry Model (SenML+JSON)
Utilizzato per l'invio periodico dei dati dai sensori al cloud.

| Field (n) | Unit (u) | Type | Description |
| :--- | :--- | :--- | :--- |
| `battery` | `/` (%) | Double | Livello batteria (0.0 - 1.0) |
| `temperature` | `Cel` | Double | Temperatura dell'aria in °C |
| `humidity` | `%RH` | Double | Percentuale di umidità del terreno |
| `wind_speed` | `km/h` | Double | Velocità del vento in km/h |
| `is_raining` | N/A | Boolean | Stato delle precipitazioni (True=Piove) |

## Communication

Il sistema utilizza il protocollo MQTT per tutte le comunicazioni: la scelta è motivata dalle poche risorse dei nodi agricoli (alimentati a batteria), dall'asincronia della telemetria ambientale e dalla necessità di gestire dinamicamente il disaccoppiamento tra campo e server centrale.

## MQTT Topics & Data

**1. Telemetry & State (Edge -> Cloud)**
* **Topic:** `node/{node_id}/telemetry`
* **Payload:** Array JSON in formato SenML.
* **QoS:** 1.

**2. Node Info (Edge -> Cloud)**
* **Topic:** `node/{node_id}/info`
* **Payload:** JSON custom.
* **QoS:** 1
* **Retain:** True (Il Manager riceve l'info anche se si connette dopo).

**3. Alerts (Cloud -> Employees/Dashboard)**
* **Topic:** `smart_agri/alert/{alert_type}/{node_id}`
* **Payload:** JSON custom.
* **QoS:** 1
* **Retain:** True (L'agricoltore riceve l'alert anche se si connette dopo).

**4. Control & Configuration (Cloud -> Edge)**
* **Action:** `node/{node_id}/action` (Comandi attuatori: "irrigation_on", "irrigation_off", "rotation_on", "rotation_off").
* **Config:** `node/{node_id}/config` (Aggiornamento remoto soglie).
* **QoS:** 1

## MQTT Topics & Service Mapping

| Topic Pattern | Publisher | Subscriber | Purpose |
| :--- | :--- | :--- | :--- |
| `node/+/telemetry` | Smart Node | Data Manager | Monitoraggio continuo stato e sensori. |
| `node/+/info` | Smart Node | Data Manager | Discovery e registrazione nuovi nodi. |
| `alert/+/+` | Data Manager | Dashboard/App | Notifica anomalie meteo e manutenzione. |
| `node/<node_id>/config` | Data Manager | Smart Node | Invio nuove soglie e configurazioni sul campo. |
| `node/<node_id>/action` | Data Manager | Smart Node | Attuazione remota per mitigazione (es. blocco irrigazione). |
