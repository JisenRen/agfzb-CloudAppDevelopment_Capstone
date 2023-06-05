import requests
import json
# import related models here
from .models import *
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

# Create a `get_request` to make HTTP GET requests
def get_request(url, **kwargs):
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except e:
        # If any error occurs
        # print("Network exception occurred")
        return {}

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload):
    response = requests.post(url, headers={'Content-Type': 'application/json'}, json=json_payload)
    print(f"POST to {url} with status {response.status_code}.")
    return response.text

# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # For each dealer object
        for dealer in json_result:
            # Get its content in `doc` object
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)

    return results

def get_dealer_by_id_from_cf(url, dealerId=None):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealerId)
    if json_result:
        # For each dealer object
        for dealer in json_result:
            # Get its content in `doc` object
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealerId=None):
    returns = []
    json_data = get_request(url, dealerId=dealerId)
    if json_data:
        for item in json_data:
            item_id = item['id'] if 'id' in item else None
            dealership = item['dealership'] if 'dealership' in item else None
            name = item['name'] if 'name' in item else None
            purchase = item['purchase'] if 'purchase' in item else None
            review = item['review'] if 'review' in item else None
            purchase_date = item['purchase_date'] if 'purchase_date' in item else None
            car_make = item['car_make'] if 'car_make' in item else None
            car_model = item['car_model'] if 'car_model' in item else None
            car_year = item['car_year'] if 'car_year' in item else None
            sentiment = analyze_review_sentiments(review) if review is not None else {}
            review = DealerReview(id=item_id, dealership=dealership, name=name, purchase=purchase, review=review,
                                  purchase_date=purchase_date, car_make=car_make, car_model=car_model, car_year=car_year,
                                  sentiment=sentiment)
            returns.append(review)
    return returns

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
    authenticator = IAMAuthenticator("RVGZBBpLF9mxwyDRWl9cOYvm8lprM8jna07JVfhYDs9k")
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator
    )
    url = "https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/2208eb75-c398-4ec0-8d5f-d0871c2eaec7"
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze(text=text, features=Features(sentiment=SentimentOptions(document=True))).get_result()
    # response = requests.get(url, params=params, headers={'Content-Type': 'application/json'}, auth=HTTPBasicAuth('apikey', api_key))
    return response["sentiment"]["document"]["label"]
