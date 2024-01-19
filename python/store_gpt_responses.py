#!/usr/bin/env python

import configparser
import json
import pika
import os
import boto3

config = configparser.ConfigParser()
config.read('/etc/secrets.ini')
username = config['rabbitmq'].get('username')
password = config['rabbitmq'].get('password')

def save_message_to_file(message):
    file_path = '/home/dusty/oh_backup/chat_responses.json'

    # Check if the directory exists, create if it doesn't
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Append message to the file
    with open(file_path, 'a') as file:
        file.write(message + '\n')

def callback(ch, method, properties, body):
    print("Received a message")
    save_message_to_file(body.decode())

# RabbitMQ server credentials and host
credentials = pika.PlainCredentials(username, password)
parameters = pika.ConnectionParameters('orangepi5b', 5672, '/', credentials)

# Set up connection to RabbitMQ
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Ensure the queue exists
channel.queue_declare(queue='chatgpt_response')

# Start consuming messages from the queue
channel.basic_consume(queue='chatgpt_response', on_message_callback=callback, auto_ack=True)

print('Waiting for messages...')
channel.start_consuming()


