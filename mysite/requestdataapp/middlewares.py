from datetime import timedelta, datetime
from http import HTTPStatus

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin


def set_useragent_on_request_middleware(get_response):

    print("initial call")

    def middleware(request: HttpRequest) -> HttpResponse:
        # print("before get response")
        request.user_agent = request.META.get("HTTP_USER_AGENT")
        response = get_response(request)
        # print("after get response")
        return response

    return middleware


class CountRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest):
        self.requests_count += 1
        # print("requests count: ", self.requests_count)

        response = self.get_response(request)
        self.responses_count += 1
        # print("responses count: ", self.responses_count)
        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print("get ", self.exceptions_count, " exception so far")


class ThrottleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_time = {}
        self.limit = 100
        self.time_frame = timedelta(minutes=1)

    def __call__(self, request: HttpRequest):
        client_ip = request.META.get('REMOTE_ADDR')
        now_time = datetime.now()

        if client_ip not in self.request_time:
            self.request_time[client_ip] = {'time': now_time, 'cnt': 1}
        else:
            time_info = self.request_time[client_ip]
            if now_time - time_info['time'] < self.time_frame:
                if time_info['cnt'] < self.limit:
                    time_info['cnt'] += 1
                else:
                    return render(
                        request,
                        "requestdataapp/error-count-request.html",
                        status=HTTPStatus.TOO_MANY_REQUESTS
                    )
            else:
                time_info['time'] = now_time
                time_info['cnt'] = 1
        response = self.get_response(request)

        return response