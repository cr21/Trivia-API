import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  # CORS Header
  # default CORS constructor
  # CORS(app)
  CORS(app, resources=r'/api/*')
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  #CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add("Access-Control-Allow-Headers","Content-Type,Authorization,True")
    response.headers.add("Access-Control-Allow-Methods","GET,PUT,POST,PATCH,DELETE,OPTIONS")
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route("/categories")
  def get_All_Categories():
    categories = Category.query.all()
    categories = {category.id:category.type for category in categories}
    print(categories)
    return jsonify({
      "success":True,
      "categories":categories
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  
  def get_paginated_questions(request,selection):
    '''
    Helper method for getting books for perticular page if page number is 
    not passed then get first page result
    '''
    page = request.args.get('page',1,type=int)
    start = (page-1)* QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE 
    all_questions = selection[start:end]
    all_questions=[question.format() for question in all_questions]
    return all_questions

  @app.route("/questions")
  def get_all_questions():
    selection = Question.query.order_by(Question.id).all()
    all_questions = get_paginated_questions(request,selection)
    all_categories = Category.query.all()
    if len(all_questions) == 0:
      abort(404)
    else:
      return jsonify({
        'questions':all_questions,
        'total_questions':len(selection),
        'categories': {category.id:category.type for category in all_categories},
        # 'currentCategory': None 
        'current_category':None
      })
  '''

  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route("/questions/<int:id>",methods=["DELETE"])
  def delete_question(id):
    # fetch question details from db 
    question = Question.query.get(id)
    print("questions",question)
    # if question id is not present in db abort operation
    # else return sucess True 
    if question is None:
      abort(422)
    else:
      question.delete()
      return jsonify({
        "status_code":200,
        "success": True
      })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route("/questions",methods=["POST"])
  def add_questions():
    print("heu")
    try:
      data = request.get_json()
      question = data.get("question")
      answer = data.get("answer")
      difficulty = data.get("difficulty")
      category = data.get("category")
      search_term = data.get("searchTerm")
      print("search_term",search_term)
      # if search is not present then Normal Create Question else search and return
      if search_term is None:
        print("INSERTING RECORD!!!!!!!!!!!!!!!!!!!!1")
        # categories = {\
        #                 category.type : category.id 
        #                 for category in Category.query.all()
        #               }
        # print(categories)
        question_record = Question(question,answer,category,difficulty)
        question_record.insert()
        selection = Question.query.order_by(Question.id).all()
      
        return jsonify({
          "status_code":200,
          "success":True,
          "total_questions":len(selection)
        })
      else:
        print("SEARCHING RECORD!!!!!!!!!!!!!!!!!!!!1")
        selection = Question.query.filter(Question.question.ilike('%'+search_term+'%')).all()
        print(selection)
        questions = get_paginated_questions(request,selection)
        if len(questions) == 0:
          print("DUDDDDDDDDDDDDD")
          abort(404,description="resource not found")
        else:
          print("___")
          return jsonify({
            'questions':questions,
            'total_questions':len(selection),
            'current_category':None
          })
    except:
      print("HI")
      print("exception",sys.exc_info())
      abort(404)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  # @app.route("/questions",methods=["POST"])
  # def 

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route("/categories/<int:id>/questions",methods=["GET"])
  def get_questions_by_categories(id):
    selection = Question.query.filter_by(category = id).all()
    print(selection)
    questions = get_paginated_questions(request,selection)
    if len(questions) == 0:
      abort(404)
    else:
      return jsonify({
        'success':True,
        'status_code':200,
        'questions':questions,
        'total_questions':len(selection),
        'current_category': None 
      })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route("/quizzes",methods=["POST"])
  def get_quiz_questions():
    try:
      body = request.get_json()
      previous_question = body.get('previous_questions')
      quiz_category = int(body.get('quiz_category')['id'])
      category = Category.query.get(quiz_category)
      # if category is not None 
      if not category == None:
        # check if there are some previous questions so that we will not show those question
        # again
        if  "previous_questions"  in body and len(previous_question) > 0 :
          # filtered out category and filterd out previous question
          questions = Question.query.filter(Question.id.notin_(
                        previous_question), Question.category == category.id).all()
          # questions = Question.query.filter_by(Question.id.notin_(previous_question),
          #             category = category.id).all()
        # if there are no previous question then check for category and if category is all
        # then show all question
        else:
          print("in first else",category)
          questions = Question.query.filter_by(category = category.id).all()
      else:
        # if category is none then only check for previous question filter
        if "previous_questions" in body and len(previous_question) > 0:
          questions = Question.query.filter(Question.id.notin_(previous_question)).all()
        # if previous question is None and category is also None then show all
        else:
          questions = Question.query.all()
      max = len(questions) - 1
      if max > 0:
          questions = questions[random.randint(0, max)].format()

      else:
          questions = False
      print(questions)
      return jsonify({
          'status': 200,
          "success": True,
          "question": questions
      })          
    except:
      print(sys.exc_info())
      abort(500)
    


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    print("hey")
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def Unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "Unprocessable"
      }), 422

  @app.errorhandler(500)
  def server_processing_error(error):
    return jsonify({
      "success":False,
      "error":500,
      "message":"Internal Server Error"
    }),500

  @app.errorhandler(400)
  def client_processing_error(error):
    return jsonify({
      "success":False,
      "error":400,
      "message":"request format Error"
    }),400


  return app

    