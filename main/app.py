from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 간단한 강의 데이터 (DB 대신 메모리)
courses = [
    {"id": 1, "name": "파이썬 입문", "teacher": "김코딩"},
    {"id": 2, "name": "웹 개발", "teacher": "이프론트"},
    {"id": 3, "name": "자료구조", "teacher": "박컴공"},
]

registered_courses = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/courses')
def course_list():
    return render_template('courses.html', courses=courses)

@app.route('/register/<int:course_id>')
def register(course_id):
    course = next((c for c in courses if c['id'] == course_id), None)
    if course and course not in registered_courses:
        registered_courses.append(course)
    return redirect(url_for('my_courses'))

@app.route('/my-courses')
def my_courses():
    return render_template('my_courses.html', courses=registered_courses)

@app.route('/unregister/<int:course_id>')
def unregister(course_id):
    global registered_courses
    registered_courses = [c for c in registered_courses if c['id'] != course_id]
    return redirect(url_for('my_courses'))

if __name__ == '__main__':
    app.run(debug=True)
