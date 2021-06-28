#!/bin/sh
sleep 70
curl -X POST kibana:5601/api/saved_objects/_import -H "kbn-xsrf: true" --form file=@docker.ndjson
curl -X POST kibana:5601/api/saved_objects/_import -H "kbn-xsrf: true" --form file=@kafka.ndjson
curl -X POST kibana:5601/api/saved_objects/_import -H "kbn-xsrf: true" --form file=@emotedet.ndjson
