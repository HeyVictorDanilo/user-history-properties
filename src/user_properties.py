import json

from typing import List, Tuple, Dict, Any

from src.db_util import DBInstance


class LambdaCoreHandler:
    def __init__(self, event, context):

        if not event.get('headers', {}).get('authorization'):
            raise Exception('Header authorization with the hey_key is required')

        self.query: str = str(event.get('queryStringParameters', {}).get('query'))

        self.conn = DBInstance(public_key=event.get('headers', {}).get("authorization"))

    def result(self) -> List[Dict[str, Any]]:
        if self.query:
            return self.get_data()
        else:
            raise Exception('Parameter query cannot be empty')

    def get_schema_properties(self) -> List[Tuple[Any]]:
        schema_properties_query: str = """
            SELECT 
                name, type, updated_at, created_at, priority, help_name, description
            FROM
                property_user_schema;
        """
        return self.conn.handler(query=schema_properties_query)

    def get_generic_properties(self, user_id: int) -> List[Tuple[Any]]:
        generic_properties_query: str = f"""
            SELECT 
                name, value, updated_at, created_at
            FROM
                user_property 
            WHERE
                user_id = {user_id};
        """
        return self.conn.handler(query=generic_properties_query)

    def get_user_properties(self, user_id: int) -> List[Tuple[Any]]:
        generic_properties: List[Tuple[Any]] = self.get_generic_properties(user_id=user_id)
        schema_properties: List[Tuple[Any]] = self.get_schema_properties()
        return [
            sp for sp in schema_properties if sp[1] not in [gp[1] for gp in generic_properties]
        ]

    @staticmethod
    def build_properties_body(properties: List[Tuple[Any]]) -> List[Dict[str, Any]]:
        dict_properties: List = []
        for p in properties:
            dict_properties.append({
                "name": p[0],
                "type": p[1],
                "updated_at": p[2].strftime("%m/%d/%y, %H:%M:%S"),
                "created_at": p[3].strftime("%m/%d/%y, %H:%M:%S"),
                "priority": p[4],
                "help_name": p[5],
                "description": p[6]
            })
        return dict_properties

    def get_data(self) -> List[Dict[str, Any]]:
        return self.build_properties_body(
            properties=self.get_user_properties(user_id=self.get_user_id())
        )

    def get_user_id(self) -> int:
        user_ids_query: str = f"""
            SELECT 
                uc.id
            FROM 
                user_company as uc 
            WHERE 
                uc.email = '{self.query}' or uc.mobile_number = '{self.query}' or uc.identification = '{self.query}'
            ORDER by uc.updated_at desc limit 1;
        """
        user_id = self.conn.handler(query=user_ids_query)
        if user_id:
            return user_id[0][0]
        else:
            raise Exception("The user doesn't exists")


def handler(event=None, context=None) -> Dict[str, Any]:
    try:
        response = LambdaCoreHandler(event, context)
        return {
            "isBase64Encoded": False,
            "statusCode": "200",
            "headers": {
                "content-type": "application/json"
            },
            "body": json.dumps(response.result())
        }
    except Exception as e:
        exception_message = str(e)
        api_exception_obj = {
            "isBase64Encoded": False,
            "statusCode": "400",
            "headers": {
                "content-type": "application/json"
            },
            "body": json.dumps({
                "error": {
                    "message": exception_message,
                }
            })
        }
        return api_exception_obj
