extends TextureRect

var socket = PacketPeerUDP.new()
var thread: Thread

var image: Image
var image_mutex: Mutex = Mutex.new()

func _ready():
	if socket.bind(4242,"*") != OK:
		print("Failed to bind to port 4242")
		return
	else:
		print('started on port 4242')
	
	thread = Thread.new()

	thread.start(listen_for_images_function)

func _physics_process(delta):
	if image_mutex.try_lock():
		var im_tx = ImageTexture.create_from_image(image)
		self.set_texture(im_tx)
		image_mutex.unlock()

func listen_for_images_function():
	while true:
		while socket.wait() == OK:
			var data = socket.get_packet().get_string_from_ascii()
			if data:
				create_texture_from_pool_byte_array(Marshalls.base64_to_raw(data))

func create_texture_from_pool_byte_array(byte_array):
	if image_mutex.try_lock():
		image = Image.new()
		image.load_jpg_from_buffer(byte_array)
		image_mutex.unlock()
