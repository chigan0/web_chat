from typing import Tuple, Union
from random import choice
from pickle import loads, dumps

from settings import settings


def random_str(length:int=16) -> str:
	symb = 'abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	return ''.join((choice(symb) for i in range(length)))
	

# Get Random Username and Surname
def get_fake_username() -> Tuple[str, str]:
	with open(f"{settings.BASE_DIR}/util/male_names_rus.txt", encoding='utf-8') as names, open(
		f"{settings.BASE_DIR}/util/male_surnames_rus.txt", encoding='utf-8') as surnames:
		
		names = list(names.read().replace('\n', ' ').split())
		surnames = list(surnames.read().replace('\n', ' ').split())
		
		return choice(surnames), choice(names)


# Conver data into bytes
def pickle_data_dumps(data: Union[dict, object], data_loads: bool = False) -> Union[bytes, dict]:
	if data is None:
		return None

	if data_loads:
		return loads(data)

	else:
		if type(data) == dict:
			picke_dumps = {}

			for i in data:
				picke_dumps[i] = data[i]

		else:
			picke_dumps = data

		return dumps(picke_dumps)