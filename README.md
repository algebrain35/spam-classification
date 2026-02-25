# Spam Classification Server

FastAPI server that uses logistic regression model to predict spam emails, enabled by Redis worker responsible for queueing emails and post-classification (assigning tier score to Email).

To run server,

```bash
chmod +x run.sh
./run.sh
```

or build image using Dockerfile.
