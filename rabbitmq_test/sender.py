import pika, json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')

mes= {'dafkljaf;lasdjf': 1111}
mes = json.dumps(mes)
channel.basic_publish(exchange='', routing_key='hello', body=mes)
print(" [x] Sent 'Hello World!'")

connection.close()