# Drone CI Quickstart

Test out Drone CI using Docker, Drone Runner and GitHub.

Start out with the official quickstart video: https://www.youtube.com/watch?v=Qf8EHRzAgHQ, and then follow some extra steps if you wish from this Readme.

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
	
- Start Drone container:
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

- drone-runner-docker container:
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

  Note: if there are no repositories on this github account, Drone will also be empty

  
