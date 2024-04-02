import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import lxml
import os
ID_COURSE = 63054


def get_sections(url):

    response = requests.get(url=url)
    src = response.json()
    course = src['courses'][0]
    return {'id_course': course['id'],
            'sections': course['sections']}

def get_lessons_from_sections(url):

    response = requests.get(url=url)
    src = response.json()
    lessons_list =[]
    for section in src['sections']:
        lessons_list.append({
            'position': section['position'],
            'id':section['id'],
            'lessons': section['units'],
        })
    return lessons_list

def get_lessons(id_section):

    response = requests.get(url=f'https://stepik.org/api/sections/{id_section}')
    src = response.json()

    section = src['sections'][0]
    return {
            'position': section['position'],
            'id':section['id'],
            'lessons': section['units'],
            }

def get_steps(lesson):

    response = requests.get(url=f'https://stepik.org/api/units?ids%5B%5D={lesson}')
    src = response.json()
    id_lesson = src["units"][0]['lesson']
    response = requests.get(url=f'https://stepik.org/api/lessons/?ids%5B%5D={id_lesson}')
    src = response.json()

    return {
        'lesson': src['lessons'][0]['id'],
        'steps': src['lessons'][0]['steps']
    }

def get_text(id_step,lesson_path):

    tables = None
    tables_json = []
    TABLE_TAG = "<p>\n[TABLE]\n</p>"
    response = requests.get(url=f'https://stepik.org/api/steps?ids%5B%5D={id_step}')
    src = response.json()
    soup = BeautifulSoup(src['steps'][0]['block']['text'].encode('utf-8'), 'html.parser')

    #удаляет нахуй таблицы
    tables = soup.find_all('table')
    for table in tables:
        tables_json.append(pd.read_html(str(table))[0].to_json(force_ascii= False))
        table.replace_with(BeautifulSoup(TABLE_TAG, 'html.parser'))

    # try:
    #     tables = soup.find_all('table')
    #     tables_json = tables.to_json()
    # except Exception as e: 
    #     tables_json = None
    #     print('error ', e)

    # with open(f'{step_directory}\{step_directory}.txt','w',encoding="utf-8") as f:
    #     f.write(soup.text)
    # try:
    #     tables.to_csv(f'{id_step}.csv', index=False, path_or_buf = lesson_path)
    # except:
    #     pass

    return {'text': soup.text,
            'tables':tables_json if tables_json != None or len(tables_json) >0 else None}
    
def main():


    # cource_directory = f'ID_COURCE_{ID_COURSE}'

    # if not os.path.exists(cource_directory):
    #     os.makedirs(cource_directory)

    directory = f'ID_COURSE_{ID_COURSE}'

    if not os.path.exists(directory):
        os.makedirs(directory)

    full_data = []
    url = f'https://stepik.org/api/courses/{ID_COURSE}'
    sections = get_sections(url)
    for id_section in sections['sections'][1:2]:
        # full_data['id_course'] = sections['id_course']

        print(id_section)
        lessons = get_lessons(id_section)
        print(lessons)
        for lesson in lessons['lessons']:
            
            lesson_path = os.path.join(
            directory, '%s' % (f'ID_LESSON_{lesson}')
            )
            if not os.path.exists(lesson_path):
                os.makedirs(lesson_path)

            lessons_data = []
            step_data = []
            print(lesson)
            steps = get_steps(lesson)
            for id_step in steps['steps']:

                text = get_text(id_step, lesson_path)
                step_data.append({
                    'id_step':id_step,
                    'text': text
                })
            lessons_data.append({
                'id_lesson': lesson,
                'steps': step_data
            })

            

            file_path = os.path.join(
            lesson_path, '%s.%s' % (f'{lesson}', 'json')
            )
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(lessons_data, file, indent=4, ensure_ascii=False, skipkeys=False)

        # full_data.append({
        #     'id_section': id_section,
        #     'lessons': lessons_data
        # })

            

if __name__=='__main__':
    main()