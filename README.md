# Krishi Mitr - AI-Powered Smart Farming Assistant 🌾

**Production-Ready Version 1.0** | **Rebranded from Farm-IQ**

A comprehensive AI and ML platform for Indian farmers providing crop recommendations, disease detection, fertilizer management, yield predictions, and sustainable farming guidance.

## What's New in v1.0 (Production-Ready Updates)

✅ **Complete Backend Implementation**
- Created 4 missing utility modules (yield_logic, sustainability, irrigation, database)
- Added MongoDB integration for user management and activity tracking
- Implemented Auth0 authentication with secure session management
- Full orchestrator pattern for multi-agent coordination

✅ **Enhanced Error Handling**
- Custom 404 and 500 error pages
- Comprehensive logging system
- Security headers and CSRF protection
- Graceful failure handling

✅ **New Features**
- User profiles and activity history
- Health check endpoint (`/api/health`)
- API documentation endpoint (`/api/agents`)
- Sustainability advisor with crop rotation guidance
- Smart irrigation scheduling with water conservation tips
- Market trends and agricultural news feeds

✅ **Production Infrastructure**
- Environment-based configuration (`.env.example`)
- Complete setup guide (SETUP.md)
- Dependency management with requirements.txt
- Ready for Heroku, AWS, Docker deployment

**[Quick Start Guide →](./RUN_PROJECT.md)**

✅ **Modern Frontend Architecture** (NEW in v1.1)
- Next.js 14 with TypeScript for type-safe development
- Seamless Flask proxy integration for API calls
- 3 comprehensive CSS files (1,342 lines) with design system
- 20+ animations and interactive components
- Fully responsive mobile-first design
- Dark/light mode support

**Quick Commands:**
```bash
npm install
npm run dev  # Starts Next.js + proxies to Flask
cd app && python app.py  # Run Flask backend
```

Visit: **http://localhost:3000** (Next.js frontend with Flask backend)

---

#### A production-ready AI-powered agricultural platform with ML/DL models for crop recommendations, disease detection, yield predictions, fertilizer management, and sustainable farming guidance.

## DISCLAIMER ⚠️
This is a POC(Proof of concept) kind-of project. The data used here comes up with no guarantee from the creator. So, don't use it for making farming decisions. If you do so, the creator is not responsible for anything. However, this project presents the idea that how we can use ML/DL into precision farming if developed at large scale and with authentic and verified data.

## MOTIVATION 💪
- Farming is one of the major sectors that influences a country’s economic growth. 

- In country like India, majority of the population is dependent on agriculture for their livelihood. Many new technologies, such as Machine Learning and Deep Learning, are being implemented into agriculture so that it is easier for farmers to grow and maximize their yield. 

- In this project, I present a website in which the following applications are implemented; Crop recommendation, Fertilizer recommendation and Plant disease prediction, respectively. 

    - In the crop recommendation application, the user can provide the soil data from their side and the application will predict which crop should the user grow. 
    
    - For the fertilizer recommendation application, the user can input the soil data and the type of crop they are growing, and the application will predict what the soil lacks or has excess of and will recommend improvements. 
    
    - For the last application, that is the plant disease prediction application, the user can input an image of a diseased plant leaf, and the application will predict what disease it is and will also give a little background about the disease and suggestions to cure it.

## DATA SOURCE 📊
- [Crop recommendation dataset ](https://www.kaggle.com/atharvaingle/crop-recommendation-dataset) (custom built dataset)
- [Fertilizer suggestion dataset](https://github.com/vannu07/Farm-IQ-AI-Powered-Smart-Farming-Assistant/blob/main/app/Data/fertilizer.csv) (custom built dataset)
- [Disease detection dataset](https://www.kaggle.com/vipoooool/new-plant-diseases-dataset)

## Notebooks 📓
##### I have also published the corresponding code on Kaggle Notebooks.
- [Crop Recommendation](https://www.kaggle.com/atharvaingle/what-crop-to-grow)
- [Disease Detection](https://www.kaggle.com/atharvaingle/plant-disease-classification-resnet-99-2)

# Built with 🛠️
<code><img height="30" src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/python/python.png"></code>
<code><img height="30" src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/html/html.png"></code>
<code><img height="30" src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/css/css.png"></code>
<code><img height="30" src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/javascript/javascript.png"></code>
<code><img height="30" src="https://github.com/tomchen/stack-icons/raw/master/logos/bootstrap.svg"></code>
<code><img height="30" src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/git/git.png"></code>
<code><img height="30" src="https://symbols.getvecta.com/stencil_80/56_flask.3a79b5a056.jpg"></code>
<code><img height="30" src="https://cdn.iconscout.com/icon/free/png-256/heroku-225989.png"></code>

<code><img height="30" src="https://raw.githubusercontent.com/numpy/numpy/7e7f4adab814b223f7f917369a72757cd28b10cb/branding/icons/numpylogo.svg"></code>
<code><img height="30" src="https://raw.githubusercontent.com/pandas-dev/pandas/761bceb77d44aa63b71dda43ca46e8fd4b9d7422/web/pandas/static/img/pandas.svg"></code>
<code><img height="30" src="https://matplotlib.org/_static/logo2.svg"></code>
<code><img height="30" src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Scikit_learn_logo_small.svg/1280px-Scikit_learn_logo_small.svg.png"></code>
<code><img height="30" src="https://raw.githubusercontent.com/pytorch/pytorch/39fa0b5d0a3b966a50dcd90b26e6c36942705d6d/docs/source/_static/img/pytorch-logo-dark.svg"></code>

## How to use 💻
- Crop Recommendation system ==> enter the corresponding nutrient values of your soil, state and city. Note that, the N-P-K (Nitrogen-Phosphorous-Pottasium) values to be entered should be the ratio between them. Refer [this website](https://www.gardeningknowhow.com/garden-how-to/soil-fertilizers/fertilizer-numbers-npk.htm) for more information.
Note: When you enter the city name, make sure to enter mostly common city names. Remote cities/towns may not be available in the [Weather API](https://openweathermap.org/) from where humidity, temperature data is fetched.

- Fertilizer suggestion system ==> Enter the nutrient contents of your soil and the crop you want to grow. The algorithm will tell which nutrient the soil has excess of or lacks. Accordingly, it will give suggestions for buying fertilizers.

- Disease Detection System ==> Upload an image of leaf of your plant. The algorithm will tell the crop type and whether it is diseased or healthy. If it is diseased, it will tell you the cause of the disease and suggest you how to prevent/cure the disease accordingly.
Note that, for now it only supports following crops

<details>
  <summary>Supported crops
</summary>

- Apple
- Blueberry
- Cherry
- Corn
- Grape
- Pepper
- Orange
- Peach
- Potato
- Soybean
- Strawberry
- Tomato
- Squash
- Raspberry
</details>

## How to run locally 🛠️
- Before the following steps make sure you have [git](https://git-scm.com/download), [Anaconda](https://www.anaconda.com/) or [miniconda](https://docs.conda.io/en/latest/miniconda.html) installed on your system
- Clone the complete project with `git clone https://github.com/vannu07/Farm-IQ-AI-Powered-Smart-Farming-Assistant.git` or you can just download the code and unzip it
- **Note:** The master branch doesn't have the updated code used for deployment, to download the updated code used for deployment you can use the following command
  ```
  ❯ git clone -b deploy https://github.com/vannu07/Farm-IQ-AI-Powered-Smart-Farming-Assistant.git 
  ```
- `deploy` branch has only the code required for deploying the app (rest of the code that was used for training the models, data preparation can be accessed on `master` branch)
- It is highly recommended to clone the deploy branch for running the project locally (the further steps apply only if you have the deploy branch cloned)
- Once the project is cloned, open anaconda prompt in the directory where the project was cloned and paste the following block
  ```
  conda create -n Farm-IQ   python=3.6.12
  conda activate Farm-IQ 
  pip install -r requirements.txt
  ```
- And finally run the project with
  ```
  python app.py
  ```
- Open the localhost url provided after running `app.py` and now you can use the project locally in your web browser.

## Contribute 👨‍💻
Please read [CONTRIBUTING.md](https://github.com/vannu07/Farm-IQ-AI-Powered-Smart-Farming-Assistant/blob/main/Contributing.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Usage ⚙️
You can use this project for further developing it and adding your work in it. If you use this project, kindly mention the original source of the project and mention the link of this repo in your report.

## Further Improvements 📈
This was my first big project so there are lot of things to improve upon

- 🎨 Frontend Cleanup: CSS is partially inline and scattered. Consolidating styles and improving layout with Bootstrap or modern CSS frameworks will enhance UI/UX.
- 🌱 Data Enrichment: More region-specific crop and soil data can be collected via web scraping or APIs (e.g., Soil Health Card portal) to improve prediction accuracy.	
- 🌿 Disease Detection: Current image dataset is limited. Expanding it with diverse, high-quality plant images and augmenting the model with deeper CNNs (e.g., ResNet) will increase robustness.
- ⚙️ Code Modularization: The project currently uses Jupyter Notebooks. Migrating to a modular Flask structure with routes.py, utils.py, etc., will enhance maintainability and scalability.
- 🤖 AI Chatbot Upgrade: FarmAI currently gives static replies. It can be powered by OpenAI's GPT API to provide real-time, intelligent agricultural advice.
- 📊 User Dashboard: A simple analytics dashboard using Chart.js or Plotly can be added to show crop trends, past predictions, and insights.

This project serves as a strong foundation for building a production-ready, AI-powered agricultural platform. 🌾

## Credits 💳
This project is heavily inspired from **[this GitHub repository](https://github.com/7NNS7/Recommendation-System-for-Farming)** (especially the crop recommendation and fertilizer recommendation part). This project is an extended version of the above mentioned project. Please star the mentioned repo.

## License 📝
This project is licensed under [GNU (GENERAL PUBLIC LICENSE)](https://github.com/vannu07/Farm-IQ-AI-Powered-Smart-Farming-Assistant/blob/main/LICENSE).

## Contact 📞

#### If you have any doubt or want to contribute feel free to email me or hit me up on [LinkedIn](https://www.linkedin.com/in/varnit-kumar-0883bb251/)
