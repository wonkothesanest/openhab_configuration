The backup script is enabled by setting up the root user's aws credentials for s3 upload and adding boto3 pip installed to root.

It runs every night at 2am and has a rotation of 4 entries.


The Store function listens to the rabbitmq for finished messages from the chat bots, it then stores it to a file that it knows will be backedup by the backup system.
