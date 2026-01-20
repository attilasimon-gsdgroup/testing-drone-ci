# Drone CI Quickstart

Checking out Drone CI using Docker, Drone Runner, ngrok and GitHub.

Start out with the official quickstart video: https://www.youtube.com/watch?v=Qf8EHRzAgHQ, made by [Harness](https://github.com/harness), and then follow some extra steps, if you wish, from this Readme.

This repo is a small python app created only to test out this Drone CI setup.

## ngrok

A tool that creates a secure, public URL (tunnel) pointing to a local server/app running on your machine, like Drone in this case.

- Sign up on the [ngrok website](https://ngrok.com/)
- Download and install the app
- Get auth token and set it up locally using a terminal:

  ```
  ngrok config add-authtoken <token>
  ```
- Start ngrok in a terminal:
  ```
  ngrok http 8080
  ```
Once ngrok is started, the terminal will show information about this instance and some logs. The `Forwarding` section contains the public and local urls.

## GitHub

Register an OAuth app: https://github.com/settings/applications
- Use the ngrok URL as app URL
- Use the same URL followed by `/login` for the Auth URL
- Optional: add logo
- Get **Client ID**
- Generate and get **Client Secret**
- Save both of these for later use

## Docker

We'll use Drone server & Drone Runner Docker containers locally.

- Create folder for project (name: `drone-quickstart`)
	- cd into it
	- create `data` folder for Drone to save the db
	
- Generate random string using openssl (will be used as Drone RPC Secret)
  ```
  openssl rand -hex 16
  ```
	
- List and if missing, create docker network for the drone server (name: `drone-net`)
  ```
  docker network ls
  ```
  ```
  docker network create drone-net
  ```
	
- Start Drone container using the corresponding data:
  ```
  docker run 
  --rm 
  --volume=$PWD/data:/data 
  --env=DRONE_GITHUB_CLIENT_ID=<GitHub-Client-ID> 
  --env=DRONE_GITHUB_CLIENT_SECRET=<GitHub-Client-Secret>
  --env=DRONE_RPC_SECRET=<Drone-RPC-Secret>
  --env=DRONE_SERVER_HOST=<ngrok-URL>
  --env=DRONE_SERVER_PROTO=https
  --publish=8080:80
  --name=drone
  --detach=true
  --network=drone-net
  drone/drone:2

- Start drone-runner-docker container using the corresponding data:
  ```
  docker run
  --rm
  --volume=/var/run/docker.sock:/var/run/docker.sock
  --env=DRONE_RPC_PROTO=http
  --env=DRONE_RPC_HOST=drone
  --env=DRONE_RPC_SECRET=<Drone-RPC-Secret>
  --env=DRONE_RUNNER_NAME=my-first-runner
  --publish=3000:3000
  --name=drone-runner
  --detach=true
  --network=drone-net
  drone/drone-runner-docker:1.8
  ```

## Drone

Access the ngrok URL, and set up Drone: Continue -> Connect with Github -> add account data -> Drone landing page

The `testing-drone-ci` repo has to be enabled.

Note: if there are no repositories on this github account, Drone will also be empty

## Notes

### Difference between Drone server and Drone runner

- **Server**: Central hub—handles UI/API, user auth, repo sync, webhook reception from GitHub, build queuing, and status storage. It's the brain.
- **Runner**: Execution agent—polls the server for queued builds, runs pipeline steps (e.g., in Docker containers for your docker-type pipeline), and reports results back. You can have multiple runners for scaling; here, it's drone-runner-docker for container-based exec.

### How the parts are connected

- The app is registered on GitHub with the Drone server's callback URL (e.g., the ngrok URL + /authorize)
- When a user logs into Drone, Drone redirects them to GitHub's OAuth endpoint, referencing the app's client ID
- GitHub redirects back to Drone's callback after approval, granting an access token
- For repo activation in Drone, it uses that token to list repos and automatically set up a webhook in the GitHub repo settings, pointing to Drone's endpoint (the ngrok URL + /hook)

### Full workflow from GitHub push to CI finish

1. A commit is pushed to GitHub (triggers on 'push' event as per .drone.yml)
2. GitHub sends a webhook payload to the Drone server's `/hook` endpoint (via ngrok URL, set up during repo activation in Drone UI)
3. Drone server validates the webhook (using GitHub app secrets), parses the event, checks .drone.yml from the commit, and queues a build if it matches triggers
4. Drone Runner (drone-runner-docker) polls the server periodically via RPC (using the shared secret)
5. Runner picks up the queued build, clones the repo (using OAuth token), and executes pipeline steps sequentially in temp Docker containers (e.g., spins up python:3.13 for 'install' and 'test' steps)
6. Each step runs commands; if any fails, build fails. Runner streams logs and status back to server in real-time
7. Build finishes, server updates status, notifies GitHub (commit status API), and you see results in Drone UI

## Troubleshooting

### Client version is too old

> Error response from daemon: client version 1.40 is too old. Minimum supported API version is 1.44, please upgrade your client to a newer version

**More info**:

https://developer.harness.io/docs/platform/knowledgebase/articles/docker-29-version-compatibility/

**Solution**: set the DOCKER_MIN_API_VERSION to 1.24

**Windows**:

Docker Desktop on Windows doesn't install dockerd.exe under "C:\Program Files\Docker" like a standalone Docker Engine. To set the minimum API version with Docker Desktop, edit the Docker Engine daemon JSON via Docker Desktop's settings.

Steps (presumes Linux-container mode / WSL2 backend — applies to most installs):

1. Open Docker Desktop (system tray whale → Docker Dashboard → Settings).
2. Go to "Docker Engine" (or "Docker Engine" tab under Settings).
3. In the JSON editor, add the min API entry. Example:
	{
	  "min-api-version": "1.24"
	}
(If the file already has other keys, merge this entry at top level.)

4. Click Apply and Restart.

## Testing additional features

In addition to what is in the quickstart video, we can try out a few more Drone features.

### Secrets

- Go to Drone UI → your repo → Settings → Secrets
- Add a new secret:
  ```
  Name: my_test_key
  Value: supersecretvalueTEST
  ```
- Then add it to `.drone.yml` to see if it works, for exaple in the `commands` section, add this to `install` step:
  ```
	environment:
      MY_TEST_KEY:
        from_secret: my_test_key
    commands:
      - echo "My secret is:"
      - echo $MY_TEST_KEY
      - echo "For security reasons, you will see asteriks '*******' instead the value under the echo command."
  ```
- Push the changes and check the results

### Plugins

Plugins can be used to add additional features to Drone.

#### Telegram notifications

Using community plugin: appleboy/drone-telegram  
https://github.com/appleboy/drone-telegram

1. Create a Telegram bot
	- Message `@BotFather` on Telegram  
	- /newbot → follow prompts → get  `BOT_TOKEN` (looks like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
	
2. Get our chat ID
	- open: `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
	- Message new bot anything (or add it to a group/channel)
	- Immediately refresh the getUpdates page
	- Look for `"chat":{"id":123456789,...` → that's the TO (user/group ID).
	
3. Add secrets to Drone Repo settings:
	- `TELEGRAM_TOKEN`
	- `TELEGRAM_TO`
	
4. Add notification step to `.drone.yml`
   ```
	  - name: notify-telegram
	    image: appleboy/drone-telegram
	    settings:
	      token: 
			from_secret: TELEGRAM_TOKEN
	      to: 
			from_secret: TELEGRAM_TO
	    when:
	      status: [ success, failure ]
   ```
  - Optional:
	- custom message (inside `settings`):
    ```
	message: "Build {{build.number}} on {{repo.name}} is {{build.status}}! Link: {{build.link}}"
    ```
	- ignore if this step fails and mark build as successful (after `when`):
    ```
	failure: ignore
    ```
5. Test
	- push a commit
	- a notification should appear on Telegram
