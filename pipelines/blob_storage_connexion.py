from pathlib import Path
from typing import List

from azure.storage.blob import ContainerClient

from credentials.blob_credentials import facts_container, facts_sas_token


class BlobStorageConnexionPipeline:
    
    def launch(self,
               account_url: str = "https://hecdf.blob.core.windows.net"
              ) -> None:
        print('BlobStorageConnexion launched')
        facts_blob_service = self.extract(account_url)
        blobs = self.transform(facts_blob_service)
        self.load(facts_blob_service, blobs)
        print('BlobStorageConnexion ended\n')
    
    @staticmethod
    def extract(account_url: str):
        return ContainerClient(account_url=account_url,
                               container_name=facts_container,
                               credential=facts_sas_token)
    
    @staticmethod
    def transform(facts_blob_service) -> List[str]:
        return list(facts_blob_service.list_blobs())
    
    @staticmethod
    def load(facts_blob_service, blobs: List[str]) -> None:
        for blob in blobs:
            file_name = blob.name
            download_stream = (
                facts_blob_service
                .get_blob_client(file_name)
                .download_blob()
            )
            Path(f'./{file_name}').parent.mkdir(parents=True, exist_ok=True)
            with open(f"./{file_name}", "wb") as data:
                data.write(download_stream.readall())

                
if __name__ == '__main__':
    BlobStorageConnexionPipeline().launch()

