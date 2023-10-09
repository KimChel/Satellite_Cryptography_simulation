
# Satellite Downlink

A simulation of downlink space communication focusing on cryptography. Basically the satellite encrypts the image data, sends the encrypted data along with the key and the ground station decodes and generates the decoded image.


## Authors

- [@kimchel](https://www.github.com/kimchel)


## Run Locally

Clone the project

```bash
  git clone https://github.com/KimChel/Satellite_Downlink_Simulation.git
```

Go to the project directory

```bash
  cd my-project
```

Install libraries

```bash
  pip install paho-mqtt
  pip install ttkbootstrap
```






## Usage/Examples

```python
mqttBroker = "io.eclipse.org"
#mqttBroker = IP_ADDRESS
client.connect(mqttBroker, port=1883)
```

You can use a local mqtt broker (e.g. Mosquitto etc) or a cloud mqtt broker (e.g. HiveMQ, RabbitMQ etc.)

