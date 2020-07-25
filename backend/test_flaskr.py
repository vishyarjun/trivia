import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_category_success(self): #1
        result = self.client().get('/categories')
        data = json.loads(result.data)
       
        self.assertEqual(result.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'] is not None)

    def test_get_category_failure(self): #2
        result = self.client().get('/categories/1000')
        data = json.loads(result.data)
        
        self.assertEqual(result.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertTrue(data.get('categories') is None)

    def test_get_questions_success(self):#3
        result = self.client().get('/questions?page=1')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data.get('success'),True)
        self.assertTrue(int(data.get('total_questions'))>0)
        self.assertTrue(data.get('categories') is not None)

    def test_get_questions_failure(self):#4
        result = self.client().get('/questions?page=1000')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertEqual(data.get('success'),False)
        self.assertTrue(data.get('total_questions') is None)  
        self.assertTrue(data.get('questions') is None)

    def test_post_questions(self): #5
        json_data = {
            'question': 'What is the expansion of NEOWISE?',
            'answer': 'Near Earth Object Wide-Field Infrared Survey Explorer',
            'difficulty': 3,
            'category': 1
        }
        result = self.client().post('/questions', json=json_data)
        result_data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result_data.get('created')>0)
        self.assertEqual(result_data.get('success'), True)

    def test_post_questions_error(self): #6
        json_data = {
            'question': 'What is the expansion of NEOWISE?',
            'answer': None,
            'difficulty': 3,
            'category': 1
        }
        result = self.client().post('/questions', json=json_data)
        result_data = json.loads(result.data)
        self.assertEqual(result.status_code, 400)
        self.assertTrue(result_data.get('created') is None)
        self.assertEqual(result_data.get('success'), False)

    def test_post_questions_error_2(self): #7
        json_data = {
            'question': 'What is the expansion of NEOWISE?',
            'answer': 'Near Earth Object Wide-Field Infrared Survey Explorer',
            'difficulty': 3,
            'category': 1
        }
        result = self.client().post('/questions/6', json=json_data)
        result_data = json.loads(result.data)
        self.assertEqual(result.status_code, 405)

    def test_search_questions_success(self): #8
        json_data = {
            'searchTerm':'hi'
        }
        result = self.client().post('/questions', json=json_data)
        result_data = json.loads(result.data)
        
        self.assertTrue(result.status_code, 200)
        self.assertEqual(result_data.get('success'), True)
        self.assertTrue(result_data.get('questions') is not None)
        self.assertTrue(result_data.get('total_questions')>0)

    def test_search_questions_failure(self): #9
        json_data = {
            'searchTerm':''
        }
        result = self.client().post('/questions', json=json_data)
        result_data = json.loads(result.data)
        
        self.assertTrue(result.status_code, 400)
        self.assertEqual(result_data.get('success'), False)
        self.assertTrue(result_data.get('questions') is None)
        self.assertTrue(result_data.get('total_questions') is None)

    def test_delete_success(self): #10
        json_data = {
            'question': 'Sampel Ques?',
            'answer': 'Sample Answer',
            'difficulty': 2,
            'category': 1
        }
        result = self.client().post('/questions', json=json_data)
        result_data = json.loads(result.data)
        ques_id = result_data['created']

        result = self.client().delete('/questions/{}'.format(ques_id))
        result_data = json.loads(result.data)

        self.assertTrue(result.status_code, 200)
        self.assertEqual(result_data.get('success'), True)
        self.assertEqual(result_data.get('deleted'), ques_id)

    def test_delete_failure(self): #11
        result = self.client().delete('/questions/{}'.format(99999))
        result_data = json.loads(result.data)

        self.assertTrue(result.status_code, 422)
        self.assertEqual(result_data.get('success'), False)
        self.assertEqual(result_data.get('deleted'), None)

    def test_get_questions_by_categories_success(self): #12
        result = self.client().get('/categories/2/questions')
        result_data = json.loads(result.data)

        self.assertTrue(result.status_code,200)
        self.assertEqual(result_data.get('success'), True)
        self.assertTrue(result_data.get('total_questions')>0)
        self.assertTrue(result_data.get('questions') is not None)


    def test_get_questions_by_categories_failure(self): #13
        result = self.client().get('/categories/9999/questions')
        result_data = json.loads(result.data)

        self.assertTrue(result.status_code,400)
        self.assertEqual(result_data.get('success'), False)
        self.assertTrue(result_data.get('total_questions') is None)
        self.assertTrue(result_data.get('questions') is None)

    def test_post_quizzes_success(self): #14
        req_data = {
            'previous_questions':[1, 2, 3],
            'quiz_category':{'id':'0'},
        }
        result = self.client().post('/quizzes',json=req_data)
        result_data = json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(result_data['question'] is not None)
        self.assertTrue(result_data['question']['id'] not in req_data['previous_questions'])

    def test_post_quizzes_success_2(self): #15
        req_data = {
            'previous_questions':[],
            'quiz_category':{'id':1},
        }
        result = self.client().post('/quizzes',json=req_data)
        result_data = json.loads(result.data)
        self.assertEqual(result.status_code,200)
        self.assertTrue(result_data['question'] is not None)
        self.assertTrue(result_data['question']['id'] not in req_data['previous_questions'])

    def test_post_quizzes_failure(self): #16
        req_data = {
            'previous_questions':[],
            'quiz_category':None,
        }
        result = self.client().post('/quizzes',json=req_data)
        result_data = json.loads(result.data)
        self.assertEqual(result.status_code,400)
        self.assertTrue(result_data.get('question') is None)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
