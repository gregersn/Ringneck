from typing import Any, List, Union, Dict
from pydantic import BaseModel

from ringneck import run


class Character(BaseModel):
    kin: str
    name: str


def test_generate():
    generate_program = """kin = {
    1: 'Human',
    2: 'Elf'
}

names = {
    'Human': ['A', 'B'],
    'Elf': ['C', 'D']
}
names.get("Human")
$.kin = random_table(kin)
$.name = random_table(names.get($.kin))
"""
    char = Character.construct()

    def random_table(table: Union[Dict[str, Any], List[Any]]):
        if isinstance(table, dict):
            return list(table.values())[0]

        return table[0]

    run(generate_program,
        global_variables=char,
        builtins={"random_table": random_table})

    names = {
        'Human': ['A', 'B'],
        'Elf': ['C', 'D']
    }
    assert char.kin in ['Human', 'Elf']
    assert char.name in names[char.kin]


def test_set_and_get_global():
    program = """$.foo = $.bar"""

    data = {'bar': 'asdf'}
    run(program, global_variables=data)

    assert data['foo'] == data['bar']
