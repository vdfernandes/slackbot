clean-pyc:
	@find . -name '*.pyc' -exec rm --force {} +
	@find . -name '*.pyo' -exec rm --force {} +
	@find . -name '*~' -exec rm --force  {} +

dependencies:
	pip install -r requirements.txt

prepare-db:
	@python -c 'from slackbot.models import create_all; create_all()'

install: dependencies config prepare-db
	@if [ ! -d logs ] ; then mkdir logs ; echo "logs directory created!" ; fi

find-user-id:
	@python -c "from slackbot.slack.methods import find_id; print(find_id('user','$(USER)'))"

find-channel-id:
	@python -c "from slackbot.slack.methods import find_id; print(find_id('channel','$(CHANNEL)'))"

find-pchannel-id:
	@python -c "from slackbot.slack.methods import find_id; print(find_id('priv_channel','$(CHANNEL)'))"
