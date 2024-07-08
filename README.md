# Data Takehome Test

## Setup

1. Clone the repository:
   ```sh
   git clone <your-repo-url>
   cd fetch_rewards_project
2. Install Docker and Docker Compose:
    Docker installation guide
    Docker Compose installation guide

3. Install AWS CLI Local:
    pip install awscli-local

4. Install PostgreSQL client:
    PostgreSQL installation guide

5. Install Python dependencies:
    pip install -r requirements.txt

## Running the Project

1. Start Docker services:
    docker-compose up
2. Run the ETL script:
    python3 SQSQueue.py
3. Verify data in PostgreSQL:
    psql -d postgres -U postgres -h localhost -W
