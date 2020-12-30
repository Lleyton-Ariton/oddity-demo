# Oddity Demo

Web app showcasing a demo of time series anomaly detection with the Oddity Engine

<p align="center">
  <img src="./imgs/oddity-demo.gif" alt="Logo"/, width="500", height="160">
</p>

The web app was built with [**Streamlit**](https://www.streamlit.io/) and deployed to a google cloud kubernetes cluster. The cluster may or may not be currently still available, so follow the instructions below to run the demo locally with a docker container.

## Instructions

### Running Locally
- Ensure [**Docker**](https://www.docker.com/) is installed on your computer

- Clone or download this github repository and cd into it 

- Build the docker container with:

	```Bash 
	docker build -t oddity-demo/app:latest .
	```
	
- Then run the container lockally with:

	```Bash
	docker run -p 8501:8501 oddity-demo/app:latest
	```

The demo should now run locally on port 8501

## Important Links

The following are some important links for more information:

> PyPi: [https://pypi.org/project/oddity/](https://pypi.org/project/oddity/)

> Oddity: [https://github.com/Lleyton-Ariton/oddity](https://github.com/Lleyton-Ariton/oddity)

> Oddity Engine (Rust): [https://github.com/Lleyton-Ariton/oddity-engine](https://github.com/Lleyton-Ariton/oddity-engine)

## Extra
For some extra information on time series data/anomaly detection, you can check out my medum article series [*Houston, we have a problem*](https://lleyton-ariton.medium.com/houston-we-have-a-problem-time-series-anomaly-detection-4ab48c10dd01).