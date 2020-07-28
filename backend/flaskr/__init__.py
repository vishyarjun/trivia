import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json
from sqlalchemy.sql.expression import func
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    setup_db(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization, true')
        response.headers.add(
          'Access-Control-Allow-Methods', 'GET, PATCH, POST, DELETE, OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def categories():
        if request.method == 'GET':
            categories = Category.query.all()
            if len(categories) == 0:
                abort(404)
            json_data = {
                'success': True,
                'categories': {cat.id: cat.type for cat in categories}
            }
            return jsonify(json_data)
        else:
            abort(405)

    @app.route('/questions', methods=['GET', 'POST'])
    def questions():
        app.logger.info(request.args.get('page'))
        if request.method == 'GET':
            selection = Question.query.all()
            categories = Category.query.all()
            questions = paginate_questions(request, selection)
            if len(questions) == 0:
                abort(404)
            json_data = {
              'success': True,
              'questions': questions,
              'total_questions': len(selection),
              'categories': {cat.id: cat.type for cat in categories},
              'current_category': None
            }
            return jsonify(json_data)
        else:
            content = request.json
            app.logger.info(content)
            if content is None:
                abort(400)
            if content.get('searchTerm') is not '' and content.get('searchTerm') is not None:
                results = Question.query.filter(
                  Question.question.ilike('%{}%'.format(content['searchTerm']))).all()
                return jsonify({
                  'success': True,
                  'questions': [result.format() for result in results],
                  'total_questions': len(results),
                  'current_category': None
                })
            else:
                if content.get('question') is None or content.get('answer') is None or content.get('category') is None or content.get('difficulty') is None:
                    abort(400)
                question = Question(
                    question=content['question'],
                    answer=content['answer'],
                    category=content['category'],
                    difficulty=content['difficulty'],
                )
                question.insert()
                return jsonify(
                    {
                      'success': True,
                      'created': question.id
                    }
                  )

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def del_question(id):
        if request.method == 'DELETE':
            try:
                del_ques = Question.query.get(id)
                del_ques.delete()
                return jsonify({
                    'success': True,
                    'deleted': id
                })
            except:
                abort(422)

    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_questions_by_categories(id):
        results = Question.query.filter_by(category=id).all()
        app.logger.info(results)
        if len(results) == 0:
            abort(400)
        return jsonify({
            'success': True,
            'questions': [result.format() for result in results],
            'total_questions': len(results),
            'current_category': None
            })

    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        body = request.get_json()
        app.logger.info(body)
        prev = [data for data in body.get('previous_questions')]
        app.logger.info(prev)
        if body.get('quiz_category') is None:
            abort(400)
        elif body.get('quiz_category').get('id') == 0:
            next_ques = Question.query.filter(
              Question.id.notin_(prev)).order_by(func.random()).first()
        else:
            next_ques = Question.query.filter(
              Question.category == body['quiz_category']['id'], 
              Question.id.notin_(prev)).order_by(func.random()).first()
        if len(prev) == 0 and next_ques is None:
            abort(400)
        return jsonify({
            'success': True,
            'question': None if next_ques is None else next_ques.format()
            })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
            }), 404

    @app.errorhandler(405)
    def not_allowe(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not allowed"
            }), 405

    @app.errorhandler(400)
    def bad_req(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
            }), 400

    @app.errorhandler(422)
    def not_proc(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
            }), 422

    return app
# ***************** PENDING ************************

# Documentation

# Test cases

# ***************** PENDING ************************
