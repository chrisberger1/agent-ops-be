pipeline {
    agent any
    
    environment {
        DOCKER_COMPOSE_VERSION = '2.15.1'
        PYTHON_VERSION = '3.9'
        APP_NAME = 'bench-management-app'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                sh """
                python${PYTHON_VERSION} -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                pip install pytest pytest-cov flake8
                """
            }
        }
        
        stage('Lint') {
            steps {
                sh """
                . venv/bin/activate
                flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
                """
            }
        }
        
        stage('Test') {
            steps {
                sh """
                . venv/bin/activate
                pytest --cov=app tests/
                """
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh "docker-compose build"
            }
        }
        
        stage('Deploy to Development') {
            when {
                branch 'develop'
            }
            steps {
                sh "docker-compose up -d"
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                // Add production deployment steps here
                echo "Deploying to production..."
            }
        }
    }
    
    post {
        always {
            sh "docker-compose down || true"
            cleanWs()
        }
        success {
            echo 'Build successful!'
        }
        failure {
            echo 'Build failed!'
        }
    }
}