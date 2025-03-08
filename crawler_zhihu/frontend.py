from flask import Flask, render_template
from tools.file_lock import FileLock
import time

app = Flask(__name__)
file_lock = FileLock()

def load_data_with_retry(file_path, max_retries=3, retry_delay=0.1):
    """带重试机制的数据加载"""
    for attempt in range(max_retries):
        try:
            data = file_lock.read_json(file_path)
            if data is not None:
                # 如果是 user_details.json，返回第一个元素
                if 'user_details.json' in file_path and isinstance(data, list):
                    return data[0]
                return data
        except Exception as e:
            if attempt == max_retries - 1:
                return {'error': str(e)}
            time.sleep(retry_delay)
            print(f"重试加载文件 {file_path}，第 {attempt + 1} 次")
    return {'error': '无法加载数据'}

def load_user_data():
    return load_data_with_retry('./db/user_details.json')

def load_answer_data():
    return load_data_with_retry('./db/answer.json')

def load_question_data():
    return load_data_with_retry('./db/question.json')

@app.route('/')
def show_user():
    user_data = load_user_data()
    
    if 'error' in user_data:
        return render_template('error.html', error=user_data['error']), 500
    
    # 确保必要的字段存在
    if 'follower' not in user_data:
        user_data['follower'] = {}
    if 'fans' not in user_data:
        user_data['fans'] = {}
    
    # 定义系统保留字段（可根据需要扩展）
    system_fields = {
        'href', '用户名', '关注了', '关注者', 
        'follower', 'fans', 'update_time'
    }
    
    return render_template(
        'user.html',
        user=user_data,
        system_fields=system_fields
    )
    
@app.route('/answers')
def show_answers():
    answer_data = load_answer_data()
    if 'error' in answer_data:
        return render_template('error.html', error=answer_data['error']), 500
    return render_template('answers.html', answers=answer_data)

@app.route('/questions')
def show_questions():
    question_data = load_question_data()
    if 'error' in question_data:
        return render_template('error.html', error=question_data['error']), 500
    return render_template('questions.html', questions=question_data)

if __name__ == '__main__':
    app.run(debug=True)