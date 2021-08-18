FROM python:3.8-slim-buster

WORKDIR /usr/src/pager_duty_stats

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y nodejs \
    npm

ADD ./pager_duty_stats ./pager_duty_stats
ADD ./ui/src ./ui/src
ADD ./ui/dist/index.html ./ui/dist/index.html
ADD ./ui/dist/stats.html ./ui/dist/stats.html
ADD ./ui/dist/css ./ui/dist/css
COPY ./ui/webpack.config.js ./ui/webpack.config.js

ENV VIRTUAL_ENV=./virtual_env
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

ENV FLASK_APP=pager_duty_stats/application.py
# ENV FLASK_APP=pager_duty_stats/toy_app.py
ENV FLASK_ENV=prod

COPY ./package.json ./package.json
COPY ./.babelrc ./.babelrc

RUN npm install
RUN npx webpack --mode production --config ui/webpack.config.js

EXPOSE 5000

# CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
CMD ["sleep", "infinity"]