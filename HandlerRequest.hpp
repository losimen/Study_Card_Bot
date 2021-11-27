//
//  HandlerRequest.hpp
//  listener
//
//  Created by Павло Коваль on 27.11.2021.
//
#include <cpprest/http_client.h>
#include <cpprest/filestream.h>
#include <cpprest/http_listener.h>
#include <cpprest/json.h>
#include <map>

using namespace utility;
using namespace web;
using namespace web::http;
using namespace web::http::client;
using namespace web::http::experimental::listener;
using namespace concurrency::streams;

class HandlerRequest
{
protected:
    void _handle_post(const http_request& request);

    void _requestLogIn(const http_request& request);
    void _requestSignUp(const http_request& request);

    
public:

    HandlerRequest()
    {};


    void AddQueueThread();
};
