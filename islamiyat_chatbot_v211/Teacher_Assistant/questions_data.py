import json, os

_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'questions_data.json')
with open(_path, 'r', encoding='utf-8') as _f:
    _data = json.load(_f)

QUESTIONS    = _data['questions']
CLASS_GROUPS = _data['class_groups']
