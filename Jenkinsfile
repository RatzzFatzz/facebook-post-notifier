pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                script {
                    sh "docker build -t zeitgeist-notifier ."
                    sh "docker images"
                }
            }
        }
    }
}