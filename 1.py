curl -X POST "https://safir.bale.ai/api/v2/auth/token" \
     -d "grant_type=client_credentials" \
     -d "client_secret=your_actual_client_secret" \
     -d "scope=read" \
     -d "client_id=your_actual_client_id"