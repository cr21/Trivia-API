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
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'root','localhost:5432', self.database_name)
        self.question = {
                            "question":"Who is  your favorite sport player",
                            "answer":"Leo Messi",
                            "category":"6",
                            "difficulty":1
        }
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
    # get all Question Success Test
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['categories'])
        # self.assertEqual(data['currentCategory'],data['curre'])


    # get All Question Faiulre test
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # get All categories
    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        print(data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
    
     # # delete success routine
    def test_delete_questions(self):
        res = self.client().delete("/questions/9")
        # print(res)
        question = Question.query.filter(Question.id == 9).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(question, None)
     
    # delete Failure message 422 error
    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('/questions/2000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    # successfully add new question
    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.question)
        data = json.loads(res.data)
        # print("data",data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        
    
    def test_500_if_question_creation_fails(self):
        self.question["category"]=20
        res = self.client().post('/questions', json=self.question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # get questions based on categories
    def test_get_question_by_categories(self):
        res =self.client().get("/categories/6/questions")
        data = json.loads(res.data)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['status_code'], 200)
        self.assertEqual(data['success'], True)

    # error if any or accessing the page that dont have data
    def test_404_get_question_by_category(self):
        res=self.client().get("categories/100/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    # for search question
    def test_search_questions(self):
        res=self.client().post("questions",json={'searchTerm': "Taj"})
        data = json.loads(res.data)
        self.assertTrue(data["questions"])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['total_questions'],1)

    def test_quiz_All_category_no_previous_question(self):
        res =self.client().post("quizzes",json={
                                                "previous_questions": [],
	                                            "quiz_category":  {"type": "click", "id": 0}
                                                }
                                )
        data  = json.loads(res.data)
        self.assertEqual(res.status,'200 OK')
        self.assertEqual(res.status_code,200)
        self.assertTrue(data["question"])

    def test_quiz_by_category_no_previous_question(self):
        res =self.client().post("quizzes",json={
                                                "previous_questions": [],
	                                            "quiz_category":  {"type": "click", "id": 6}
                                                }
                                )
        data  = json.loads(res.data)
        self.assertEqual(res.status,'200 OK')
        self.assertEqual(res.status_code,200)
        self.assertTrue(data["question"])

    def test_quiz_by_category_previous_question(self):
        res =self.client().post("quizzes",json={
                                                "previous_questions": [14],
	                                            "quiz_category":  {"type": "click", "id": 6}
                                                }
                                )
        data  = json.loads(res.data)
        self.assertEqual(res.status,'200 OK')
        self.assertEqual(res.status_code,200)
        self.assertTrue(data["question"])

        
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()