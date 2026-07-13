Smart Agriculture - Adaptive Irrigation & Digital Twin 

Progetto realizzato per il corso di Intelligent Internet of Things (A.A. 2023/2024).

Studente: [Tuo Nome e Cognome]

Matricola: [Tua Matricola]

Scenario Applicativo

L'obiettivo di questo progetto è la realizzazione di un sistema IoT avanzato per l'ottimizzazione automatica del processo di irrigazione agricola. Il sistema è progettato per prevenire gli sprechi idrici e proteggere le colture, adattandosi in tempo reale alle condizioni meteorologiche (siccità, pioggia, vento forte).

Componenti Principali (Architettura)

1. Edge Layer (Environmental Node)

Il nodo agricolo intelligente, situato nel campo, è dotato di sensori e attuatori per interagire autonomamente con l'ambiente.
Sensori:

Soil Humidity: Misura la percentuale di umidità del terreno.

Wind Sensor: Rileva la velocità del vento in km/h.

Rain Sensor: Rileva la presenza di precipitazioni in corso.

Temperature: Misura la temperatura dell'aria.

Battery Level: Monitora lo stato energetico del nodo IoT.

Attuatori:

Irrigation Pump: Accende o spegne l'erogazione dell'acqua.

Rotation Motor: Attiva o disattiva la rotazione del getto d'acqua (utile in caso di forte vento per non disperdere le risorse idriche).

2. Cloud Layer (Data Manager)

Il servizio centrale ospitato sul server che agisce come "cervello" del sistema.

Digital Twin Manager: Mantiene in memoria una replica esatta e costantemente aggiornata dello stato di ogni nodo agricolo attivo (EnvNodeDigitalTwin).

Adaptive Logic: Ragiona sui dati del Digital Twin. Accende l'acqua se c'è siccità, spegne la rotazione se c'è vento, e ferma l'irrigazione se inizia a piovere.

Alerting System: Genera allerte specifiche in tempo reale:

Drought Alert: Terreno troppo secco.

Storm Alert: Vento oltre la soglia di sicurezza.

Maintenance Alert: Batteria del nodo scarica.

New Configs: Invia nuove configurazioni e soglie operative ai nodi sul campo (es. cambio di coltura stagionale) senza necessità di riavviarli.

📊 Modello Dati Telemetria (SenML + JSON)

Utilizzato per l'invio periodico dei dati dai sensori al Cloud, rispettando gli standard industriali.

Field (n)

Unit (u)

Type

Descrizione

battery

/

Double

Livello batteria (0.0 - 1.0)

temperature

Cel

Double

Temperatura dell'aria in °C

humidity

%RH

Double

Umidità del terreno (0 - 100%)

wind_speed

km/h

Double

Velocità del vento in km/h

is_raining

N/A

Boolean

Stato precipitazioni (true = Piove)

📡 Comunicazione e Protocollo MQTT

Il sistema utilizza esclusivamente il protocollo MQTT. La scelta è motivata dalla natura asincrona della telemetria, dal disaccoppiamento tra campo e cloud, e dalla leggerezza del protocollo, ideale per dispositivi alimentati a batteria.

Tutti i Topic sono isolati all'interno di un Base Topic protetto: /iot/user/<matricola>/

MQTT Topics & Data

1. Telemetry & State (Edge -> Cloud)

Topic: .../node/{node_id}/telemetry

Payload: Array JSON in formato SenML.

QoS: 1

2. Node Info / Discovery (Edge -> Cloud)

Topic: .../node/{node_id}/info

Payload: JSON custom con i descrittori e le soglie del nodo.

QoS: 1

Retain: True (Il Cloud riceve la "carta d'identità" del nodo anche se si connette in ritardo).

3. Alerts (Cloud -> Dashboard / Utenti)

Topic: .../alert/{alert_type}/{node_id}

Payload: JSON custom con le coordinate dell'emergenza o payload nullo se l'allarme è risolto.

QoS: 1

Retain: True (Interfacce o App leggono lo stato di allarme non appena si avviano).

4. Control & Configuration (Cloud -> Edge)

Action: .../node/{node_id}/action (Comandi: irrigation_on, rotation_off, ecc.)

Config: .../node/{node_id}/config (Aggiornamento remoto soglie di vento/umidità).

QoS: 1

MQTT Topics & Service Mapping

Topic Pattern

Publisher

Subscriber

Purpose

.../node/+/telemetry

Env Node

Data Manager

Monitoraggio continuo stato sensori (SenML).

.../node/+/info

Env Node

Data Manager

Discovery e creazione del Digital Twin.

.../node/<node_id>/action

Data Manager

Env Node

Attuazione autonoma per mitigare anomalie.

.../node/<node_id>/config

Data Manager

Env Node

Aggiornamento remoto delle soglie.

.../alert/+/+

Data Manager

(Dashboard)

Notifica allarmi (Siccità, Vento, Batteria).

