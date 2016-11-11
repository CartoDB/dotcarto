import ConfigParser
from os.path import join, dirname, basename
from zipfile import ZipFile

from carto.sql import SQLClient
from carto.auth import APIKeyAuthClient

config = ConfigParser.RawConfigParser()
config.read("dotcarto.conf")

CARTO_BASE_URL = config.get('carto', 'base_url')
CARTO_API_KEY = config.get('carto', 'api_key')


sql = SQLClient(APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY))


class DotCartoFile(object):
    replacements = []

    def __init__(self, carto_file_path):
        self.carto_file_path = carto_file_path

    def replace_dataset(self, original_dataset_name, new_dataset_name):
        self.replacements.append({
            "original_dataset_name": original_dataset_name,
            "new_dataset_name": new_dataset_name
        })

    def get_new(self):
        with ZipFile(self.carto_file_path) as original_carto_file:
            visualization_id = original_carto_file.namelist()[0][:-1]
            json_file_relative_path = join(visualization_id, visualization_id + ".carto.json")
            json = original_carto_file.read(json_file_relative_path)

        with ZipFile(join(dirname(self.carto_file_path), "NEW_{carto_file_name}".format(carto_file_name=basename(self.carto_file_path))), mode='w') as new_carto_file:
            for replacement in self.replacements:
                original_dataset_name = replacement["original_dataset_name"]
                new_dataset_name = replacement["new_dataset_name"]

                json = json.replace(original_dataset_name, new_dataset_name)

                new_dataset = sql.send("select * from {dataset}".format(dataset=replacement["new_dataset_name"]), format="gpkg")
                new_carto_file.writestr(join(visualization_id, replacement["new_dataset_name"] + ".gpkg"), new_dataset)

            new_carto_file.writestr(json_file_relative_path, json)
