#memcache
try:
	import memcache
	MC = memcache.Client(['127.0.0.1:11211'], debug=0)
except:
	print "No se pudo conectar a memcached"
	exit(0)
