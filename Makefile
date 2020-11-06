install:
		( \
    		pip install --upgrade pip; \
    		pip install -r requirements.txt; \
  	)

virtual:
		virtualenv -p python3 venv

runwithdata:
		python3 -m project

run:
		( \
    		make install; \
    		python3 -m pipelines.blob_storage_connexion; \
    		rm -rf Analytics_Train_Set/Analytics_Train_Set_Json/poly/*; \
    		tar -C Analytics_Train_Set/Analytics_Train_Set_Json/poly/ --strip-components=1 -xvf poly.tar; \
    		python3 -m project; \
  	)
