extends Control

var gyro: Vector3 = Vector3.ZERO
var udp := PacketPeerUDP.new()
var connected = false

func _ready():
	udp.connect_to_host(IP.resolve_hostname("leandro.local"), 5005)

func _process(delta):
	var input = Input.get_gyroscope()
	
	gyro += input

	$Gyro.text = "(" + str(snapped(gyro.x, 0.01)) + ", " + str(snapped(gyro.y, 0.01)) + ", " + str(snapped(gyro.z, 0.01)) + ")"
	$GyroDelta.text = "(" + str(snapped(input.x, 0.01)) + ", " + str(snapped(input.y, 0.01)) + ", " + str(snapped(input.z, 0.01)) + ")"
	
	var data_to_send = {
		"type": "gyro",
		"x": gyro.x,
		"y": gyro.y,
		"z": gyro.z,
	}
	
	udp.put_packet(JSON.stringify(data_to_send).to_utf8_buffer())

func reset_gyro():
	gyro = Vector3.ZERO
