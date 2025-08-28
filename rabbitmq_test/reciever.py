import json

import pika

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()

channel.queue_declare(queue="hello")


def callback(ch, method, prorerties, body: bytes):
    print(json.loads(body.decode("utf-8"))["dafkljaf;lasdjf"])
    print(f" [x] Received {body}")


channel.basic_consume(queue="hello", on_message_callback=callback, auto_ack=True)

print(" [*] Waiting for messages. To exit press CTRL+C")

channel.start_consuming()
