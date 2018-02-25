import requests
import json
from .esiop import EsiOp
from .esiauth import EsiAuth
import logging

logger = logging.getLogger("EsiPysi")

class EsiPysi():
    """
    The EsiPysi class creates "EsiOp" operations based on a provided swagger spec
    """

    def __init__(self, swagger_url, **kwargs):
        """
        Initialize the class
            
        Parameters
        ----------
        swagger_url : str (url)
            URL to the swagger spec json
        user_agent : str
            User agent for calls to ESI
        """
        self.user_agent = kwargs.get("user_agent")

        self.operations = {}
        self.data = {}

        r = requests.get(swagger_url)
        data = r.json()
        self.data = data

        #Get base url
        self.base_url = "https://" + data.get("host","") + data.get("basePath", "")

        #Reformat json
        paths = data.get("paths", {})
        #each path
        for path, verbs in paths.items():
            #each http verb in a path
            for verb, operation in verbs.items():
                operation_id = operation.get("operationId")
                if operation_id is None:
                    continue
                new_op = operation.copy()
                new_op["path"] = path
                new_op["verb"] = verb

                #Handle parameter refs
                params = operation.get("parameters")
                new_op["parameters"] = {}
                for param in params:
                    path = param.get("$ref")
                    if path is None:
                        param_details = param.copy()
                    else:
                        param_details = self.__get_ref(path)
                    param_name = param_details.get("name")
                    new_op["parameters"][param_name] = param_details

                self.operations [operation_id] = new_op

        #Temp for ref
        #with open("reform.json", mode="w") as file:
        #    op_json = json.dumps(self.operations, indent=2)
        #    file.write(op_json)

    def __get_ref(self, path):
        path_split = path.split("/")
        if path_split[0] != "#":
            #Unsupported
            return None
        ref = self.data
        for i in range(1, len(path_split)):
            ref = ref.get(path_split[i], {})

        return ref

    def get_operation(self, operation_id):
        """
        Get an ESI operation from it's id

        Parameters
        ----------
        operation_id : str
            The operation id of the API call (e.g. "get_alliances_alliance_id")

        Returns
        -------
        operation : esiop class
            A class object used to preform the operation
        """
        operation = self.operations.get(operation_id)
        if operation is None:
            return None
        return EsiOp(operation, self.base_url, self.user_agent)