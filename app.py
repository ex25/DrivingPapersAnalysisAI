from flask import Flask, render_template, jsonify, request, stream_with_context, Response
from database.db import get_connection
from database.classification import Classification
from tool.zhipu import get_result_by_zhipu
from tool.alibaba import get_result_by_tongyi
from tool.pdf import get_pdf_text
import os

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/statistics/zhipu')
def statistics_zhipu():
    return render_template('statistics_zhipu.html')
    pass


@app.route('/statistics/tongyi')
def statistics_tongyi():
    return render_template('statistics_tongyi.html')
    pass


@app.route('/statistics/zhipu/result')
def statistics_zhipu_result():
    conn = get_connection()
    result = Classification.get_classification_results(conn)
    return jsonify(result)


@app.route('/statistics/tongyi/result')
def statistics_tongyi_result():
    conn = get_connection()
    result = Classification.get_classification_results(conn, 'tongyi')
    return jsonify(result)

@app.route('/zero-shot/zhipu')
def zeroshot_zhipu():
    return render_template('zero_shot_zhipu.html')
    pass


@app.route('/zero-shot/tongyi')
def zeroshot_tongyi():
    return render_template('zero_shot_tongyi.html')
    pass


@app.route('/zhipu/chat', methods=["POST"])
def zeroshot_zhipu_chat():
    data = request.json
    file_path = 'data/pdfs/' + data.get('file_path').split('\\')[-1]
    system_prompt = data.get('system_prompt')
    text = get_pdf_text(file_path)
    if not file_path or not os.path.exists(file_path):
        return jsonify({"message": "Invalid file path"}), 400

    def generate():
        for result in get_result_by_zhipu(system_prompt, text):
            yield result

    return Response(stream_with_context(generate()), content_type='text/event-stream')



@app.route('/tongyi/chat', methods=["POST"])
def zeroshot_tongyi_chat():
    data = request.json
    file_path = 'data/pdfs/' + data.get('file_path').split('\\')[-1]
    system_prompt = data.get('system_prompt')
    text = get_pdf_text(file_path)
    if not file_path or not os.path.exists(file_path):
        return jsonify({"message": "Invalid file path"}), 400

    def generate():
        for result in get_result_by_tongyi(system_prompt, text):
            yield result

    return Response(stream_with_context(generate()), content_type='text/event-stream')


@app.route('/few-shot/zhipu')
def fewshot_zhipu():
    return render_template('few_shot_zhipu.html')
    pass


@app.route('/few-shot/tongyi')
def fewshot_tongyi():
    return render_template('few_shot_tongyi.html')
    pass


if __name__ == '__main__':
    app.run(debug=True)
