extends Control

var gyro: Vector3 = Vector3.ZERO
var udp := PacketPeerUDP.new()
var connected = false

var state: Dictionary = {
	"type": "state",
	"up": false,
	"down": false,
	"left": false,
	"right": false,
}


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
	udp.connect_to_host($LeandroIP.text, 5005)
	udp.put_packet(JSON.stringify(data_to_send).to_utf8_buffer())
	udp.put_packet(JSON.stringify(state).to_utf8_buffer())

func reset_gyro():
	gyro = Vector3.ZERO


func _on_button_down(button: String):
	state[button] = true

func _on_button_up(button: String):
	state[button] = false
