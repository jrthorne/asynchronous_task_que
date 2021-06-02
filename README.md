# Asynchronous Processing



A project is available for asyncronous processing called django-celery which uses a queue runner (usually redis) placing tasks on a queue which then gets run by celery. Though this can work well, there are three issues:

- Either redis or celery occasionally would crash without warning which would mean that jobs the user expected to have happen (send an email, create a PDF file) would mysteriously not happen, and this would not get fixed until the developer gets user complaints. The identification of a celery or redis crash is very opaque.
- If code is deployed and uwsgi reloads the changed application to memory to serve via the webserver, you have an extra overhead of reloading the app into celery as well. Sometimes this may crash celery causing the issue above, or sometimes if celery is not reloaded, and the application served by the webserver to people's browsers is different to that served by celery causing a great deal of confusion.
- At the time of writing there  was no obvious way to inspect the queue without executing shell commands which involved logging on to the server running celery

This project has an admin window to show the job queue, allows you to create jobs on the queue via django admin, allows you to inspect the standard output and standard error of a queued task that has been run, or to kill a task that is pending. There is also a cron scheduler that will run tasks hourly or daily. These are run by two user cron tasks which you should put in to the cron table of www-data or what ever user is running your webserver on a production system. For simplicity here though, I put them into roots crontab, and have one application server that also runs the batch processes. I have never had cron unexpectedly quit in over 25 years in the industry.

# Event Logging

I have trouble with AWS cloudwatch which could well be due to my limited understanding on the search facilities on the AWS cloudwatch dashboard. I find the logs hard to search. Also (I may be wrong), but I understand it works by  an agent running on the AWS server and reads the log files on that server then passes them to AWS via some kind of API to be served by AWS on an underwhelming web page displaying the logs as text.

Postgres is a much better place to store logs in my understanding, and django admin is an excellent tool for searching/filtering logs. Any logs caused by the application crashing can be handled by Sentry (https://sentry.io), but with application logs for bookings, transactions, log ins, etc, I have found it invaluable to have a single line event logger which stuffs logs into a django table. This is what I provide here.

# Running this Project

I have created a docker container that makes it pretty easy to set up and see the project working. It creates a server with the cron tasks installed and starts the cron server. Once the docker container is built and running, you have to log in, run migrations, create a superuser and run the django webserver. I could automate this, but have left it as an exercise to aid illustration on how the project is set up, and so you get a chance to see the console logs as it is running. Here is what to do:

$ docker-compose build
$ docker-compose up

Log in to the container, so first:
$ docker ps
to get the container id of the running container, then
$ docker exec -it <CONTAINER ID> bash

You can look at root's crontab which should have the que runner, and the cron sheduler:
`*/5 * * * * /usr/local/bin/python /app/manage.py run_pending_commands >> /dev/null 2>&1
*/1 * * * * /usr/local/bin/python /app/manage.py queue_cron_tasks >> /dev/null 2>&1`

Then when in a bash shell on the running container
root$ /.manage.py test

To make sure things are working, then:

root$ raamig

Which runs migrations via an alias in the .bash_aliases file, then

root$ ./manage.py createsuperuser
to create the super user of your choice, eg 'admin' with 'password'. And finally
root$ runserver

Go to your browser:
http://localhost:8000/admin/

log in as the user you crated (admin/password?), and go to 
http://localhost:8000/admin/async_que/queuedtask/
Add a task with command 'test_mgt_com' and save it. It will appear as pending. Wait five minutes (the queue runner runs every five minutes),
and it will have run. Open the detail, and see the standard out and standard error. The management 
command records an event log. Check it here:
http://localhost:8000/admin/async_que/event/


NOTES:
crontab file must have a newline before EOF
Shell scripts in .docker/ must have execute access