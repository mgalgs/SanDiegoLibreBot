Your friendly [r/SanDiegoLibre](https://reddit.com/r/SanDiegoLibre) bot.

## Local environment setup

```
git clone https://github.com/mgalgs/SanDiegoLibreBot.git
cd SanDiegoLibreBot
```

And create a file named `env.sh` with the following content:

```
CLIENT_ID=<redacted>
CLIENT_SECRET=<redacted>
REDDIT_USERNAME=<redacted>
REDDIT_PASSWORD=<redacted>
```

One-time virtual environment initialization:

```
python3 -m venv venv
```

Then every time you want to work on the bot:

```
source enter.sh
```

## Kubernetes setup

This bot is deployed on a kubernetes cluster.

### Configuration (secrets)

First you need to make your `env.sh` into a kubernetes Secret.

```
./k8s/gen_secrets.sh sdlbot-secrets < env.sh | kubectl apply -f -
```

### Deployment

```
kubectl apply -f ./k8s/deployment.yaml
```
