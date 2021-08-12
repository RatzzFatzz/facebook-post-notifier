pipeline {
    agent any

    environment {
        DOCKER_HUB = credentials('docker-hub-ratzzfatzz')
    }

    stages {
        stage('Build') {
            steps {
                script {
                    sh "docker build -t zeitgeist-notifier ."
                }
            }
        }

        stage('Push image') {
            steps {
                script {
                    sh "docker tag zeitgeist-notifier ratzzfatzz/zeitgeist-notifier:latest"
                    sh "docker login -u $DOCKER_HUB_USR -p $DOCKER_HUB_PSW"
                    sh "docker push ratzzfatzz/zeitgeist-notifier:latest"
                }
            }
        }
    }
}