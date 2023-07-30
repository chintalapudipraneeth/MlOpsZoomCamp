FROM jenkins/jenkins:latest

# Distributed Builds plugins
RUN jenkins-plugin-cli --plugins ssh-slaves

# install Notifications and Publishing plugins
RUN jenkins-plugin-cli --plugins email-ext
RUN jenkins-plugin-cli --plugins mailer
RUN jenkins-plugin-cli --plugins slack

# Artifacts
RUN jenkins-plugin-cli --plugins htmlpublisher

# UI
RUN jenkins-plugin-cli --plugins greenballs
RUN jenkins-plugin-cli --plugins simple-theme-plugin

# Scaling
RUN jenkins-plugin-cli --plugins kubernetes

# install Maven
USER root
RUN apt-get update && apt-get install -y maven
USER jenkins
