CONDA_ENV=rnaFoldRand_v0.1

conda_env_from_history.yml:
	conda activate $(CONDA_ENV);\
	conda env export --from-history > $@

conda_env_full.yml:
	conda activate $(CONDA_ENV);\
	conda env export > $@
