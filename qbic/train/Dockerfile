# local dev
FROM harbor.personalhealthtrain.de/pht_master/master:nfdemo

COPY hlatyping/ /opt/pht_train/
ENTRYPOINT ["python3", "/opt/pht_train/endpoints/hlatyping/commands/run/entrypoint.py"]