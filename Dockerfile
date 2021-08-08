FROM python:latest
WORKDIR /usr/src/pager_duty_stats

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y nodejs \
    npm

ADD ./pager_duty_stats ./pager_duty_stats
ADD ./ui/src ./ui/src
COPY ./ui/webpack.config.js ./ui/webpack.config.js

ENV VIRTUAL_ENV=./virtual_env
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY ./requirements.txt ./requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV FLASK_APP=pager_duty_stats/application.py
ENV FLASK_ENV=prod

COPY ./package.json ./package.json
COPY ./.babelrc ./.babelrc

RUN npm install
RUN npx webpack --mode production --config ui/webpack.config.js

EXPOSE 443

CMD ["flask", "run"]
